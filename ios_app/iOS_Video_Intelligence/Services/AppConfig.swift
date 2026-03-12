import Foundation

enum AppConfig {
    static let useFeishuDirect = true

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
        static let baseURL = "https://your-server.com/api"
    }
}

enum AppServices {
    static let authService: AuthServiceProtocol = LocalMockAuthService()

    static let videoRepository: VideoRepositoryProtocol = {
        if AppConfig.useFeishuDirect {
            return FeishuVideoRepository(client: FeishuAPIClient.shared)
        }

        fatalError("Server mode is not implemented yet.")
    }()
}
