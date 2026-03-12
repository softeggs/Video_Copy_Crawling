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

    @Test func authManagerPersistsRestoresAndClearsSession() async throws {
        let suiteName = "AuthManagerTests-\(UUID().uuidString)"
        guard let defaults = UserDefaults(suiteName: suiteName) else {
            Issue.record("Failed to create isolated UserDefaults suite.")
            return
        }

        defaults.removePersistentDomain(forName: suiteName)
        defer { defaults.removePersistentDomain(forName: suiteName) }

        let manager = AuthManager(authService: LocalMockAuthService(), userDefaults: defaults)
        #expect(manager.isAuthenticated == false)

        try await manager.login(username: "test", password: "0104")

        #expect(manager.isAuthenticated == true)
        #expect(manager.currentUser?.tableId == LocalMockAuthService.tableID)
        #expect(manager.token == "local_mock_test_token")

        let restoredManager = AuthManager(authService: LocalMockAuthService(), userDefaults: defaults)
        #expect(restoredManager.isAuthenticated == true)
        #expect(restoredManager.currentUser?.username == "test")
        #expect(restoredManager.currentUser?.displayName == "测试账号")

        restoredManager.logout()

        #expect(restoredManager.isAuthenticated == false)
        #expect(restoredManager.currentUser == nil)
        #expect(restoredManager.token == nil)
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
