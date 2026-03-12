import Foundation

final class FeishuAPIClient {
    static let shared = FeishuAPIClient()

    private let session: URLSession
    private let decoder: JSONDecoder
    private let tokenLock = NSLock()
    private var cachedTenantAccessToken: String?
    private var tokenExpirationDate: Date?

    init(session: URLSession = .shared) {
        self.session = session
        self.decoder = JSONDecoder()
    }

    func getTenantAccessToken(forceRefresh: Bool = false) async throws -> String {
        if !forceRefresh, let token = validCachedToken() {
            return token
        }

        let url = try makeURL(path: "/auth/v3/tenant_access_token/internal")
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(
            withJSONObject: [
                "app_id": AppConfig.Feishu.appId,
                "app_secret": AppConfig.Feishu.appSecret,
            ]
        )

        let (data, response) = try await perform(request)
        guard (200 ..< 300).contains(response.statusCode) else {
            throw makeHTTPError(statusCode: response.statusCode, data: data)
        }

        let tokenResponse: FeishuTenantAccessTokenResponse
        do {
            tokenResponse = try decoder.decode(FeishuTenantAccessTokenResponse.self, from: data)
        } catch {
            throw AppServiceError.decodingError
        }

        guard tokenResponse.code == 0 else {
            throw AppServiceError.serverError(tokenResponse.msg)
        }

        cacheToken(tokenResponse.tenantAccessToken, expiresIn: tokenResponse.expire)
        return tokenResponse.tenantAccessToken
    }

    func listRecords(
        tableId: String,
        pageToken: String?,
        pageSize: Int,
        filter: String?
    ) async throws -> FeishuListRecordsData {
        var queryItems = [
            URLQueryItem(name: "page_size", value: String(pageSize)),
        ]

        if let pageToken, !pageToken.isEmpty {
            queryItems.append(URLQueryItem(name: "page_token", value: pageToken))
        }

        if let filter, !filter.isEmpty {
            queryItems.append(URLQueryItem(name: "filter", value: filter))
        }

        let path = "/bitable/v1/apps/\(AppConfig.Feishu.appToken)/tables/\(tableId)/records"
        let request = try makeRequest(path: path, method: "GET", queryItems: queryItems)
        let data = try await performAuthorized(request)

        let response: FeishuListRecordsResponse
        do {
            response = try decoder.decode(FeishuListRecordsResponse.self, from: data)
        } catch {
            throw AppServiceError.decodingError
        }

        guard response.code == 0 else {
            throw AppServiceError.serverError(response.msg)
        }

        return response.data
    }

    func getRecord(tableId: String, recordId: String) async throws -> FeishuRecord {
        let path = "/bitable/v1/apps/\(AppConfig.Feishu.appToken)/tables/\(tableId)/records/\(recordId)"
        let request = try makeRequest(path: path, method: "GET")
        let data = try await performAuthorized(request)

        let response: FeishuRecordEnvelopeResponse
        do {
            response = try decoder.decode(FeishuRecordEnvelopeResponse.self, from: data)
        } catch {
            throw AppServiceError.decodingError
        }

        guard response.code == 0 else {
            throw AppServiceError.serverError(response.msg)
        }

        return response.data.record
    }

    func createRecord(tableId: String, fields: [String: Any]) async throws -> FeishuRecord {
        let path = "/bitable/v1/apps/\(AppConfig.Feishu.appToken)/tables/\(tableId)/records"
        let body = try JSONSerialization.data(withJSONObject: ["fields": fields])
        var request = try makeRequest(path: path, method: "POST")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = body

        let data = try await performAuthorized(request)

        let response: FeishuRecordEnvelopeResponse
        do {
            response = try decoder.decode(FeishuRecordEnvelopeResponse.self, from: data)
        } catch {
            throw AppServiceError.decodingError
        }

        guard response.code == 0 else {
            throw AppServiceError.serverError(response.msg)
        }

        return response.data.record
    }

    private func makeRequest(
        path: String,
        method: String,
        queryItems: [URLQueryItem] = []
    ) throws -> URLRequest {
        let url = try makeURL(path: path, queryItems: queryItems)
        var request = URLRequest(url: url)
        request.httpMethod = method
        return request
    }

    private func makeURL(path: String, queryItems: [URLQueryItem] = []) throws -> URL {
        guard var components = URLComponents(string: AppConfig.Feishu.baseURL + path) else {
            throw AppServiceError.invalidURL
        }

        if !queryItems.isEmpty {
            components.queryItems = queryItems
        }

        guard let url = components.url else {
            throw AppServiceError.invalidURL
        }

        return url
    }

    private func performAuthorized(_ request: URLRequest, retryAfterRefresh: Bool = true) async throws -> Data {
        var authorizedRequest = request
        let token = try await getTenantAccessToken()
        authorizedRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        let (data, response) = try await perform(authorizedRequest)
        if response.statusCode == 401, retryAfterRefresh {
            invalidateCachedToken()

            var retryRequest = request
            let refreshedToken = try await getTenantAccessToken(forceRefresh: true)
            retryRequest.setValue("Bearer \(refreshedToken)", forHTTPHeaderField: "Authorization")

            let (retryData, retryResponse) = try await perform(retryRequest)
            guard (200 ..< 300).contains(retryResponse.statusCode) else {
                throw makeHTTPError(statusCode: retryResponse.statusCode, data: retryData)
            }

            return retryData
        }

        guard (200 ..< 300).contains(response.statusCode) else {
            throw makeHTTPError(statusCode: response.statusCode, data: data)
        }

        return data
    }

    private func perform(_ request: URLRequest) async throws -> (Data, HTTPURLResponse) {
        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AppServiceError.invalidResponse
        }

        return (data, httpResponse)
    }

    private func validCachedToken() -> String? {
        tokenLock.lock()
        defer { tokenLock.unlock() }

        guard
            let cachedTenantAccessToken,
            let tokenExpirationDate,
            tokenExpirationDate > Date().addingTimeInterval(60)
        else {
            return nil
        }

        return cachedTenantAccessToken
    }

    private func cacheToken(_ token: String, expiresIn: Int) {
        tokenLock.lock()
        cachedTenantAccessToken = token
        tokenExpirationDate = Date().addingTimeInterval(TimeInterval(max(expiresIn - 60, 60)))
        tokenLock.unlock()
    }

    private func invalidateCachedToken() {
        tokenLock.lock()
        cachedTenantAccessToken = nil
        tokenExpirationDate = nil
        tokenLock.unlock()
    }

    private func makeHTTPError(statusCode: Int, data: Data) -> AppServiceError {
        let message = extractMessage(from: data) ?? HTTPURLResponse.localizedString(forStatusCode: statusCode)

        switch statusCode {
        case 401:
            return .unauthorized
        default:
            return .serverError(message)
        }
    }

    private func extractMessage(from data: Data) -> String? {
        guard
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let message = object["msg"] as? String
        else {
            return nil
        }

        return message
    }
}
