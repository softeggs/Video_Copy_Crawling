import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case unauthorized
    case serverError(String)
    case decodingError
    case transportError(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "请求地址无效。"
        case .invalidResponse:
            return "服务返回了无效响应。"
        case .unauthorized:
            return "鉴权失败，请重新登录。"
        case .serverError(let message):
            return message
        case .decodingError:
            return "响应数据解析失败。"
        case .transportError(let message):
            return message
        }
    }
}

private struct AnyEncodable: Encodable {
    private let encodeImpl: (Encoder) throws -> Void

    init<T: Encodable>(_ value: T) {
        encodeImpl = value.encode(to:)
    }

    func encode(to encoder: Encoder) throws {
        try encodeImpl(encoder)
    }
}

private struct ErrorDetailItem: Decodable {
    let msg: String?
}

private enum ErrorDetailValue: Decodable {
    case string(String)
    case array([ErrorDetailItem])
    case unknown

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let value = try? container.decode(String.self) {
            self = .string(value)
        } else if let value = try? container.decode([ErrorDetailItem].self) {
            self = .array(value)
        } else {
            self = .unknown
        }
    }

    var message: String? {
        switch self {
        case .string(let value):
            return value
        case .array(let items):
            let messages = items.compactMap(\.msg)
            return messages.isEmpty ? nil : messages.joined(separator: "\n")
        case .unknown:
            return nil
        }
    }
}

private struct ErrorResponse: Decodable {
    let detail: ErrorDetailValue?
}

private struct VideoSubmitRequestPayload: Encodable {
    let url: String
    let tableId: String

    enum CodingKeys: String, CodingKey {
        case url
        case tableId = "table_id"
    }
}

final class APIService {
    static let shared = APIService()

    private let session: URLSession
    private let baseURL: String
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    init(
        session: URLSession = .shared,
        baseURL: String = AppConfig.Server.baseURL,
        decoder: JSONDecoder = JSONDecoder(),
        encoder: JSONEncoder = JSONEncoder()
    ) {
        self.session = session
        self.baseURL = baseURL
        self.decoder = decoder
        self.encoder = encoder
    }

    func login(request loginRequest: LoginRequest) async throws -> LoginResponse {
        try await request(path: "/auth/login", method: "POST", body: loginRequest)
    }

    func submitVideo(videoUrl: String, token: String) async throws -> VideoSubmitResponse {
        try await request(
            path: "/videos/submit",
            method: "POST",
            token: token,
            body: VideoSubmitRequestPayload(url: videoUrl, tableId: "")
        )
    }

    func fetchVideos(page: Int = 1, status: String? = nil, token: String) async throws -> VideoListResponse {
        var queryItems = [
            URLQueryItem(name: "page", value: "\(page)"),
            URLQueryItem(name: "page_size", value: "20"),
        ]

        if let status {
            queryItems.append(URLQueryItem(name: "status", value: status))
        }

        return try await request(
            path: "/videos",
            method: "GET",
            token: token,
            queryItems: queryItems
        )
    }

    func fetchVideo(recordId: String, token: String) async throws -> VideoRecord {
        try await request(
            path: "/videos/\(recordId)",
            method: "GET",
            token: token
        )
    }

    func fetchTypeStats(token: String) async throws -> [TypeStat] {
        try await request(
            path: "/videos/stats",
            method: "GET",
            token: token
        )
    }

    func fetchOverview(token: String) async throws -> VideoOverviewResponse {
        try await request(
            path: "/videos/overview",
            method: "GET",
            token: token
        )
    }

    private func request<Response: Decodable>(
        path: String,
        method: String,
        token: String? = nil,
        queryItems: [URLQueryItem] = [],
        body: Encodable? = nil
    ) async throws -> Response {
        guard let url = makeURL(path: path, queryItems: queryItems) else {
            throw APIError.invalidURL
        }

        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = method
        urlRequest.setValue("application/json", forHTTPHeaderField: "Accept")

        if let token {
            urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
            do {
                urlRequest.httpBody = try encoder.encode(AnyEncodable(body))
            } catch {
                throw APIError.serverError("请求编码失败。")
            }
        }

        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(for: urlRequest)
        } catch {
            throw APIError.transportError(error.localizedDescription)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200 ... 299).contains(httpResponse.statusCode) else {
            throw error(for: httpResponse.statusCode, data: data)
        }

        do {
            return try decoder.decode(Response.self, from: data)
        } catch {
            throw APIError.decodingError
        }
    }

    private func makeURL(path: String, queryItems: [URLQueryItem]) -> URL? {
        guard let base = URL(string: baseURL) else {
            return nil
        }

        let resolved = base.appending(path: path.trimmingCharacters(in: CharacterSet(charactersIn: "/")))
        guard !queryItems.isEmpty else {
            return resolved
        }

        var components = URLComponents(url: resolved, resolvingAgainstBaseURL: false)
        components?.queryItems = queryItems
        return components?.url
    }

    private func error(for statusCode: Int, data: Data) -> APIError {
        if statusCode == 401 {
            return .unauthorized
        }

        if
            let errorResponse = try? decoder.decode(ErrorResponse.self, from: data),
            let message = errorResponse.detail?.message,
            !message.isEmpty
        {
            return .serverError(message)
        }

        return .serverError(HTTPURLResponse.localizedString(forStatusCode: statusCode).capitalized)
    }
}
