import Foundation

enum AppServiceError: LocalizedError, Equatable {
    case invalidURL
    case invalidCredentials
    case missingCurrentUser
    case missingTableID
    case invalidResponse
    case unauthorized
    case serverError(String)
    case decodingError
    case paginationStateUnavailable

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "请求地址无效。"
        case .invalidCredentials:
            return "用户名或密码错误。"
        case .missingCurrentUser:
            return "当前未登录，请重新登录。"
        case .missingTableID:
            return "当前账号未绑定飞书表格。"
        case .invalidResponse:
            return "服务返回了无效响应。"
        case .unauthorized:
            return "鉴权失败，请重新登录。"
        case .serverError(let message):
            return message
        case .decodingError:
            return "响应数据解析失败。"
        case .paginationStateUnavailable:
            return "分页状态不可用，请下拉刷新后重试。"
        }
    }
}

protocol AuthServiceProtocol {
    func login(username: String, password: String) async throws -> LoginResponse
}

final class LocalMockAuthService: AuthServiceProtocol {
    static let validUsername = "test"
    static let validPassword = "0104"
    static let tableID = "tbl339YsqSYxEygQ"

    func login(username: String, password: String) async throws -> LoginResponse {
        guard username == Self.validUsername, password == Self.validPassword else {
            throw AppServiceError.invalidCredentials
        }

        let user = User(
            userId: "local-test-user",
            username: username,
            displayName: "测试账号",
            tableId: Self.tableID
        )

        return LoginResponse(token: "local_mock_\(username)_token", user: user)
    }
}
