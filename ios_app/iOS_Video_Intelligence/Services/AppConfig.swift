import Foundation

enum AppConfig {
    static let useFeishuDirect = false

    enum Feishu {
        static let appId = "cli_a9c17878db38dced"
        static let appSecret = "PJkZZukSOeKMdUQluzT2aeYqC3ZRZfYp"
        static let appToken = "ZPKVb5lDqaoRpAsBv7wccjuAnOe"
        static let baseURL = "https://open.feishu.cn/open-apis"
        static let pageSize = 20
        static let statsPageSize = 200
        static let defaultSubmitStatus = "待处理"
    }

    enum Server {
        static let baseURL = "http://192.168.0.32:8002"
    }
}

enum AppServices {
    static let authService: AuthServiceProtocol = {
        if AppConfig.useFeishuDirect {
            return LocalMockAuthService()
        }

        return BackendAuthService(apiService: .shared)
    }()

    static let videoRepository: VideoRepositoryProtocol = {
        if AppConfig.useFeishuDirect {
            return FeishuVideoRepository(client: FeishuAPIClient.shared)
        }

        return BackendVideoRepository(apiService: .shared)
    }()
}
