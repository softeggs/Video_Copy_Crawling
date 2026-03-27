import Foundation

protocol VideoRepositoryProtocol {
    func fetchRecords(token: String, page: Int, status: String?) async throws -> VideoListResponse
    func fetchRecord(token: String, recordId: String) async throws -> VideoRecord
    func submitVideo(token: String, url: String) async throws -> VideoSubmitResponse
    func fetchTypeStats(token: String) async throws -> [TypeStat]
    func fetchOverview(token: String) async throws -> VideoOverviewResponse
    // P3 记录能力
    func deleteRecord(token: String, recordId: String) async throws
    func toggleFavorite(token: String, recordId: String, isFavorited: Bool) async throws -> FavoriteResponse
    func fetchRecordStatus(token: String, recordId: String) async throws -> VideoStatusResponse
    // P3 快捷指令密钥
    func listShortcutKeys(token: String) async throws -> [ShortcutKeySummary]
    func createShortcutKey(token: String, name: String) async throws -> CreateShortcutKeyResponse
    func revokeShortcutKey(token: String, keyId: Int) async throws -> Bool
    func shortcutSubmit(key: String, url: String) async throws -> ShortcutSubmitResponse
}

final class BackendVideoRepository: VideoRepositoryProtocol {
    private let apiService: APIService

    init(apiService: APIService) {
        self.apiService = apiService
    }

    func fetchRecords(token: String, page: Int, status: String?) async throws -> VideoListResponse {
        do {
            return try await apiService.fetchVideos(page: page, status: status, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func fetchRecord(token: String, recordId: String) async throws -> VideoRecord {
        do {
            return try await apiService.fetchVideo(recordId: recordId, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func submitVideo(token: String, url: String) async throws -> VideoSubmitResponse {
        do {
            return try await apiService.submitVideo(videoUrl: url, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func fetchTypeStats(token: String) async throws -> [TypeStat] {
        do {
            return try await apiService.fetchTypeStats(token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func fetchOverview(token: String) async throws -> VideoOverviewResponse {
        do {
            return try await apiService.fetchOverview(token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    // MARK: - P3 记录能力

    func deleteRecord(token: String, recordId: String) async throws {
        do {
            try await apiService.deleteVideo(recordId: recordId, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func toggleFavorite(token: String, recordId: String, isFavorited: Bool) async throws -> FavoriteResponse {
        do {
            return try await apiService.toggleFavorite(recordId: recordId, isFavorited: isFavorited, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func fetchRecordStatus(token: String, recordId: String) async throws -> VideoStatusResponse {
        do {
            return try await apiService.fetchVideoStatus(recordId: recordId, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    // MARK: - P3 快捷指令密钥

    func listShortcutKeys(token: String) async throws -> [ShortcutKeySummary] {
        do {
            return try await apiService.listShortcutKeys(token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func createShortcutKey(token: String, name: String) async throws -> CreateShortcutKeyResponse {
        do {
            return try await apiService.createShortcutKey(name: name, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func revokeShortcutKey(token: String, keyId: Int) async throws -> Bool {
        do {
            return try await apiService.revokeShortcutKey(keyId: keyId, token: token)
        } catch {
            throw mapAppServiceError(error)
        }
    }

    func shortcutSubmit(key: String, url: String) async throws -> ShortcutSubmitResponse {
        do {
            return try await apiService.shortcutSubmit(key: key, url: url)
        } catch {
            throw mapAppServiceError(error)
        }
    }
}

final class FeishuVideoRepository: VideoRepositoryProtocol {
    private let client: FeishuAPIClient
    private let pageSize: Int
    private var pageTokenCache: [String: [Int: String]] = [:]

    init(client: FeishuAPIClient, pageSize: Int = AppConfig.Feishu.pageSize) {
        self.client = client
        self.pageSize = pageSize
    }

    func fetchRecords(token _: String, page: Int, status: String?) async throws -> VideoListResponse {
        let tableId = try currentTableID()
        let key = cacheKey(tableId: tableId, status: status)
        let requestedPage = max(page, 1)

        if requestedPage == 1 {
            pageTokenCache[key] = [:]
        }

        let pageToken: String?
        if requestedPage == 1 {
            pageToken = nil
        } else if let cachedToken = pageTokenCache[key]?[requestedPage] {
            pageToken = cachedToken
        } else {
            throw AppServiceError.paginationStateUnavailable
        }

        let listData = try await client.listRecords(
            tableId: tableId,
            pageToken: pageToken,
            pageSize: pageSize,
            filter: nil
        )

        if listData.hasMore, let nextPageToken = listData.pageToken {
            pageTokenCache[key, default: [:]][requestedPage + 1] = nextPageToken
        } else {
            pageTokenCache[key]?[requestedPage + 1] = nil
        }

        let allItems = listData.items.map { $0.toVideoRecord() }
        let filteredItems = applyStatusFilter(status, to: allItems)

        return VideoListResponse(
            total: listData.total ?? filteredItems.count,
            page: requestedPage,
            pageSize: pageSize,
            items: filteredItems,
            hasMore: listData.hasMore
        )
    }

    func fetchRecord(token _: String, recordId: String) async throws -> VideoRecord {
        let tableId = try currentTableID()
        let record = try await client.getRecord(tableId: tableId, recordId: recordId)
        return record.toVideoRecord()
    }

    func submitVideo(token _: String, url: String) async throws -> VideoSubmitResponse {
        let tableId = try currentTableID()
        let record = try await client.createRecord(
            tableId: tableId,
            fields: [
                "原始链接": [
                    "link": url,
                    "text": url,
                ],
                "处理状态": AppConfig.Feishu.defaultSubmitStatus,
            ]
        )

        return VideoSubmitResponse(
            success: true,
            recordId: record.recordId,
            status: AppConfig.Feishu.defaultSubmitStatus,
            estimatedTime: "2-5分钟",
            message: nil
        )
    }

    func fetchTypeStats(token _: String) async throws -> [TypeStat] {
        let tableId = try currentTableID()
        var counts: [String: Int] = [:]
        var nextPageToken: String?
        var hasMore = false

        repeat {
            let response = try await client.listRecords(
                tableId: tableId,
                pageToken: nextPageToken,
                pageSize: AppConfig.Feishu.statsPageSize,
                filter: nil
            )

            response.items.forEach { item in
                let videoType = item.toVideoRecord().normalizedVideoType
                counts[videoType, default: 0] += 1
            }

            hasMore = response.hasMore
            nextPageToken = response.pageToken
        } while hasMore && nextPageToken != nil

        return counts
            .map { TypeStat(videoType: $0.key, count: $0.value) }
            .sorted {
                if $0.count == $1.count {
                    return $0.videoType < $1.videoType
                }

                return $0.count > $1.count
            }
    }

    func fetchOverview(token _: String) async throws -> VideoOverviewResponse {
        let tableId = try currentTableID()
        let allRecords = try await fetchAllRecords(tableId: tableId)
        let todayPrefix = currentDatePrefix()
        let pendingStatuses: Set<String> = ["待处理", "处理中", "AI润色中"]

        return VideoOverviewResponse(
            total: allRecords.count,
            today: allRecords.filter { $0.createdAt.hasPrefix(todayPrefix) }.count,
            pending: allRecords.filter { pendingStatuses.contains($0.status) }.count
        )
    }

    // MARK: - P3 记录能力（飞书兜底模式不支持，抛出明确错误）

    func deleteRecord(token _: String, recordId _: String) async throws {
        throw AppServiceError.notSupported(feature: "删除记录")
    }

    func toggleFavorite(token _: String, recordId _: String, isFavorited _: Bool) async throws -> FavoriteResponse {
        throw AppServiceError.notSupported(feature: "收藏功能")
    }

    func fetchRecordStatus(token _: String, recordId _: String) async throws -> VideoStatusResponse {
        throw AppServiceError.notSupported(feature: "处理状态")
    }

    // MARK: - P3 快捷指令密钥（飞书兜底模式不支持）

    func listShortcutKeys(token _: String) async throws -> [ShortcutKeySummary] {
        throw AppServiceError.notSupported(feature: "快捷指令密钥")
    }

    func createShortcutKey(token _: String, name _: String) async throws -> CreateShortcutKeyResponse {
        throw AppServiceError.notSupported(feature: "快捷指令密钥")
    }

    func revokeShortcutKey(token _: String, keyId _: Int) async throws -> Bool {
        throw AppServiceError.notSupported(feature: "快捷指令密钥")
    }

    func shortcutSubmit(key _: String, url _: String) async throws -> ShortcutSubmitResponse {
        throw AppServiceError.notSupported(feature: "快捷指令密钥")
    }

    private func currentTableID() throws -> String {
        guard let tableId = AuthManager.shared.currentUser?.tableId, !tableId.isEmpty else {
            throw AppServiceError.missingTableID
        }

        return tableId
    }

    private func fetchAllRecords(tableId: String) async throws -> [VideoRecord] {
        var records: [VideoRecord] = []
        var nextPageToken: String?
        var hasMore = false

        repeat {
            let response = try await client.listRecords(
                tableId: tableId,
                pageToken: nextPageToken,
                pageSize: AppConfig.Feishu.statsPageSize,
                filter: nil
            )

            records.append(contentsOf: response.items.map { $0.toVideoRecord() })
            hasMore = response.hasMore
            nextPageToken = response.pageToken
        } while hasMore && nextPageToken != nil

        return records
    }

    private func currentDatePrefix() -> String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .gregorian)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: Date())
    }

    private func cacheKey(tableId: String, status: String?) -> String {
        let normalizedStatus = status ?? "all"
        return "\(tableId)::\(normalizedStatus)"
    }

    private func applyStatusFilter(_ status: String?, to items: [VideoRecord]) -> [VideoRecord] {
        guard let status, !status.isEmpty else {
            return items
        }

        return items.filter { $0.status == status }
    }
}
