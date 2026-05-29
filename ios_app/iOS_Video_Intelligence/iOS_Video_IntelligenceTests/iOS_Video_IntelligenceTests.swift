import Foundation
import Testing
@testable import iOS_Video_Intelligence

struct iOS_Video_IntelligenceTests {

    @Test func localMockAuthServiceAcceptsValidCredentials() async throws {
        let service = LocalMockAuthService()

        let response = try await service.login(username: "test", password: "0104")

        #expect(response.user.username == "test")
        #expect(response.user.displayName == "测试账号")
        #expect(response.user.tableId == LocalMockAuthService.tableID)
        #expect(response.token == "local_mock_test_token")
    }

    @Test func localMockAuthServiceRejectsInvalidCredentials() async {
        let service = LocalMockAuthService()

        do {
            _ = try await service.login(username: "test", password: "wrong")
            Issue.record("Expected login to fail for invalid credentials.")
        } catch {
            #expect(error as? AppServiceError == .invalidCredentials)
        }
    }

    @Test func localMockAuthServiceReturnsCurrentUserForValidToken() async throws {
        let service = LocalMockAuthService()

        let user = try await service.fetchCurrentUser(token: "local_mock_test_token")

        #expect(user.username == "test")
        #expect(user.tableId == LocalMockAuthService.tableID)
    }

    @Test func authManagerPersistsRestoresAndClearsSession() async throws {
        let suiteName = "AuthManagerTests-\(UUID().uuidString)"
        guard let defaults = UserDefaults(suiteName: suiteName) else {
            Issue.record("Failed to create isolated UserDefaults suite.")
            return
        }

        defaults.removePersistentDomain(forName: suiteName)
        defer { defaults.removePersistentDomain(forName: suiteName) }

        let backendUser = User(
            userId: "1",
            username: "api_user",
            displayName: "API User",
            tableId: ""
        )

        let manager = AuthManager(
            authService: StubAuthService(
                loginResponse: LoginResponse(
                    token: "backend_token",
                    user: backendUser
                ),
                currentUserResult: .success(backendUser)
            ),
            userDefaults: defaults
        )
        #expect(manager.isAuthenticated == false)
        #expect(manager.isRestoringSession == false)

        try await manager.login(username: "api_user", password: "secret")

        #expect(manager.isAuthenticated == true)
        #expect(manager.isRestoringSession == false)
        #expect(manager.currentUser?.tableId == "")
        #expect(manager.currentUser?.displayName == "API User")
        #expect(manager.token == "backend_token")

        let restoredManager = AuthManager(
            authService: StubAuthService(
                loginResponse: LoginResponse(
                    token: "backend_token",
                    user: backendUser
                ),
                currentUserResult: .success(
                    User(
                        userId: "1",
                        username: "api_user",
                        displayName: "Updated API User",
                        tableId: "tbl_from_backend"
                    )
                )
            ),
            userDefaults: defaults
        )
        #expect(restoredManager.isRestoringSession == true)
        await waitForCondition { restoredManager.isRestoringSession == false }

        #expect(restoredManager.isAuthenticated == true)
        #expect(restoredManager.currentUser?.username == "api_user")
        #expect(restoredManager.currentUser?.displayName == "Updated API User")
        #expect(restoredManager.currentUser?.tableId == "tbl_from_backend")

        restoredManager.logout()

        #expect(restoredManager.isAuthenticated == false)
        #expect(restoredManager.isRestoringSession == false)
        #expect(restoredManager.currentUser == nil)
        #expect(restoredManager.token == nil)
        #expect(defaults.string(forKey: "authToken") == nil)
        #expect(defaults.data(forKey: "currentUser") == nil)
    }

    @Test func authManagerClearsPersistedSessionWhenCurrentUserFetchFails() async throws {
        let suiteName = "AuthManagerUnauthorized-\(UUID().uuidString)"
        guard let defaults = UserDefaults(suiteName: suiteName) else {
            Issue.record("Failed to create isolated UserDefaults suite.")
            return
        }

        defaults.removePersistentDomain(forName: suiteName)
        defer { defaults.removePersistentDomain(forName: suiteName) }

        let storedUser = User(
            userId: "1",
            username: "api_user",
            displayName: "API User",
            tableId: ""
        )
        defaults.set("expired_token", forKey: "authToken")
        defaults.set(try JSONEncoder().encode(storedUser), forKey: "currentUser")

        let manager = AuthManager(
            authService: StubAuthService(
                loginResponse: LoginResponse(token: "unused", user: storedUser),
                currentUserResult: .failure(AppServiceError.unauthorized)
            ),
            userDefaults: defaults
        )

        #expect(manager.isRestoringSession == true)
        await waitForCondition { manager.isRestoringSession == false }

        #expect(manager.isAuthenticated == false)
        #expect(manager.currentUser == nil)
        #expect(manager.token == nil)
        #expect(defaults.string(forKey: "authToken") == nil)
        #expect(defaults.data(forKey: "currentUser") == nil)
    }

    @Test func videoTypeNormalizerGroupsAliasLabels() {
        #expect(VideoTypeNormalizer.normalize("教程类") == "教程")
        #expect(VideoTypeNormalizer.normalize("教程分享") == "教程")
        #expect(VideoTypeNormalizer.normalize("工具推荐类") == "工具推荐")
        #expect(VideoTypeNormalizer.normalize("工具推荐") == "工具推荐")
    }

    @Test func videoRecordSearchMatchesDetailedContentAndNormalizedType() {
        let record = VideoRecord(
            id: "rec_search",
            title: "标题",
            author: "作者",
            url: "https://example.com",
            summary: "一句话总结",
            corePoints: ["第一点"],
            correctedText: "这里包含一个独特关键词 alpha-beta",
            goldenSentences: ["金句"],
            tags: ["标签A"],
            videoType: "教程分享",
            status: "已完成",
            markdownContent: "",
            createdAt: "2026-03-10T10:00:00.000Z",
            processedAt: nil
        )

        #expect(record.matchesSearch("alpha-beta"))
        #expect(record.matchesSearch("教程"))
        #expect(record.matchesSearch("标签A"))
        #expect(record.matchesSearch("不存在") == false)
    }

    @Test func videoRecordDecodesBackendSnakeCasePayload() throws {
        let data = """
        {
          "id": "12",
          "title": "测试视频",
          "author": "作者A",
          "url": "https://example.com/video",
          "summary": "一句话总结",
          "core_points": ["观点1", "观点2"],
          "corrected_text": "详细内容",
          "golden_sentences": ["金句1"],
          "tags": ["AI"],
          "video_type": "教程类",
          "status": "已完成",
          "markdown_content": "# 标题",
          "created_at": "2026-03-10T10:00:00Z",
          "processed_at": "2026-03-10T10:05:00Z"
        }
        """.data(using: .utf8)!

        let record = try JSONDecoder().decode(VideoRecord.self, from: data)

        #expect(record.id == "12")
        #expect(record.corePoints == ["观点1", "观点2"])
        #expect(record.correctedText == "详细内容")
        #expect(record.goldenSentences == ["金句1"])
        #expect(record.videoType == "教程类")
        #expect(record.markdownContent == "# 标题")
    }

    @Test func typeStatsAndOverviewDecodeBackendResponses() throws {
        let statsData = """
        [
          { "video_type": "教程类", "count": 2 },
          { "video_type": "工具推荐", "count": 1 }
        ]
        """.data(using: .utf8)!

        let overviewData = """
        {
          "total": 8,
          "today": 3,
          "pending": 2
        }
        """.data(using: .utf8)!

        let stats = try JSONDecoder().decode([TypeStat].self, from: statsData)
        let overview = try JSONDecoder().decode(VideoOverviewResponse.self, from: overviewData)

        #expect(stats.map(\.videoType) == ["教程类", "工具推荐"])
        #expect(stats.map(\.count) == [2, 1])
        #expect(overview.total == 8)
        #expect(overview.today == 3)
        #expect(overview.pending == 2)
    }

    @Test func videoURLExtractorPullsShareLinkOutOfSocialCopywriting() {
        let sharedText = """
        车改完了，鱼在哪里？ http://xhslink.com/o/2hanfdheS5H
        复制后打开【小红书】查看笔记！
        """

        let extractedURL = VideoURLExtractor.extract(from: sharedText)

        #expect(extractedURL == "http://xhslink.com/o/2hanfdheS5H")
    }

    @Test func videoURLExtractorRejectsTextWithoutSupportedVideoLink() {
        let extractedURL = VideoURLExtractor.extract(from: "这是普通文本，没有可提交链接。")

        #expect(extractedURL == nil)
    }

    @Test func apiServiceLoginUsesJsonBodyAndDecodesResponse() async throws {
        let session = makeSession(
            statusCode: 200,
            body: """
            {
              "token": "backend_token",
              "user": {
                "user_id": "1",
                "username": "api_user",
                "display_name": "API User",
                "table_id": ""
              }
            }
            """
        ) { request in
            #expect(request.url?.absoluteString == "http://192.168.0.32:8002/auth/login")
            #expect(request.httpMethod == "POST")
            #expect(request.value(forHTTPHeaderField: "Content-Type") == "application/json")
            let body = String(data: request.httpBody ?? Data(), encoding: .utf8)
            #expect(body == #"{"username":"api_user","password":"secret"}"#)
        }

        let service = APIService(session: session, baseURL: "http://192.168.0.32:8002")
        let response = try await service.login(request: LoginRequest(username: "api_user", password: "secret"))

        #expect(response.token == "backend_token")
        #expect(response.user.displayName == "API User")
    }

    @Test func apiServiceFetchCurrentUserUsesBearerToken() async throws {
        let session = makeSession(
            statusCode: 200,
            body: """
            {
              "user_id": "1",
              "username": "api_user",
              "display_name": "API User",
              "table_id": "tbl_123"
            }
            """
        ) { request in
            #expect(request.url?.absoluteString == "http://192.168.0.32:8002/auth/me")
            #expect(request.httpMethod == "GET")
            #expect(request.value(forHTTPHeaderField: "Authorization") == "Bearer backend_token")
        }

        let service = APIService(session: session, baseURL: "http://192.168.0.32:8002")
        let user = try await service.fetchCurrentUser(token: "backend_token")

        #expect(user.username == "api_user")
        #expect(user.tableId == "tbl_123")
    }

    @Test func backendAuthServiceMapsUnauthorizedToInvalidCredentials() async {
        let session = makeSession(statusCode: 401, body: #"{"detail":"Invalid username or password"}"#)
        let service = BackendAuthService(
            apiService: APIService(session: session, baseURL: "http://192.168.0.32:8002")
        )

        do {
            _ = try await service.login(username: "bad", password: "wrong")
            Issue.record("Expected login to fail for invalid backend credentials.")
        } catch {
            #expect(error as? AppServiceError == .invalidCredentials)
        }
    }

    @Test func apiServiceParsesFastAPIDetailErrors() async {
        let session = makeSession(statusCode: 422, body: #"{"detail":"URL format is invalid"}"#)
        let service = APIService(session: session, baseURL: "http://192.168.0.32:8002")

        do {
            _ = try await service.submitVideo(videoUrl: "bad-url", token: "token")
            Issue.record("Expected submitVideo to fail for invalid URL.")
        } catch let error as APIError {
            switch error {
            case .serverError(let message):
                #expect(message == "URL format is invalid")
            default:
                Issue.record("Expected serverError with FastAPI detail, got \(error.localizedDescription).")
            }
        } catch {
            Issue.record("Expected APIError, got \(error.localizedDescription).")
        }
    }

    @Test func feishuRecordMappingHandlesMixedFieldShapes() {
        let record = FeishuRecord(
            recordId: "rec_123",
            fields: [
                "标题": .string("测试标题"),
                "作者": .string("作者A"),
                "一句话总结": .string("一句话总结"),
                "核心观点": .string("观点一\n观点二"),
                "详细内容": .string("详细内容正文"),
                "金句": .string("金句一\n金句二"),
                "标签": .array([
                    .dictionary(["text": .string("标签A")]),
                    .string("标签B"),
                ]),
                "视频类型": .string("教程类"),
                "处理状态": .string("已完成"),
                "原始链接": .dictionary([
                    "link": .string("https://example.com/video"),
                    "text": .string("示例链接"),
                ]),
                "处理时间": .int(1710000000000),
                "笔记路径": .string("/tmp/note.md"),
            ],
            createdTime: 1700000000000,
            lastModifiedTime: nil
        )

        let video = record.toVideoRecord()

        #expect(video.id == "rec_123")
        #expect(video.title == "测试标题")
        #expect(video.author == "作者A")
        #expect(video.summary == "一句话总结")
        #expect(video.corePoints == ["观点一", "观点二"])
        #expect(video.correctedText == "详细内容正文")
        #expect(video.goldenSentences == ["金句一", "金句二"])
        #expect(video.tags == ["标签A", "标签B"])
        #expect(video.videoType == "教程类")
        #expect(video.normalizedVideoType == "教程")
        #expect(video.status == "已完成")
        #expect(video.url == "https://example.com/video")
        #expect(video.markdownContent == "/tmp/note.md")
        #expect(video.createdAt.contains("T"))
        #expect(video.processedAt != nil)
    }
}

private struct StubAuthService: AuthServiceProtocol {
    let loginResponse: LoginResponse
    let currentUserResult: Result<User, Error>

    func login(username _: String, password _: String) async throws -> LoginResponse {
        loginResponse
    }

    func fetchCurrentUser(token _: String) async throws -> User {
        try currentUserResult.get()
    }
}

private final class MockURLProtocol: URLProtocol, @unchecked Sendable {
    nonisolated(unsafe) static var requestHandler: ((URLRequest) throws -> (HTTPURLResponse, Data))?

    override class func canInit(with request: URLRequest) -> Bool {
        true
    }

    override class func canonicalRequest(for request: URLRequest) -> URLRequest {
        request
    }

    override func startLoading() {
        guard let handler = Self.requestHandler else {
            client?.urlProtocol(self, didFailWithError: URLError(.badServerResponse))
            return
        }

        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}

private func makeSession(
    statusCode: Int,
    body: String,
    assertRequest: ((URLRequest) -> Void)? = nil
) -> URLSession {
    MockURLProtocol.requestHandler = { request in
        assertRequest?(request)
        let response = HTTPURLResponse(
            url: request.url ?? URL(string: "http://192.168.0.32:8002")!,
            statusCode: statusCode,
            httpVersion: nil,
            headerFields: ["Content-Type": "application/json"]
        )!
        return (response, Data(body.utf8))
    }

    let configuration = URLSessionConfiguration.ephemeral
    configuration.protocolClasses = [MockURLProtocol.self]
    return URLSession(configuration: configuration)
}

private func waitForCondition(
    timeoutNanoseconds: UInt64 = 1_000_000_000,
    pollIntervalNanoseconds: UInt64 = 20_000_000,
    condition: @escaping @Sendable () -> Bool
) async {
    let deadline = DispatchTime.now().uptimeNanoseconds + timeoutNanoseconds

    while !condition() && DispatchTime.now().uptimeNanoseconds < deadline {
        try? await Task.sleep(nanoseconds: pollIntervalNanoseconds)
    }
}
