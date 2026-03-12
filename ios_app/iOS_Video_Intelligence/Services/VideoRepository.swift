import Foundation

protocol VideoRepositoryProtocol {
    func fetchRecords(tableId: String, page: Int, status: String?) async throws -> VideoListResponse
    func fetchRecord(tableId: String, recordId: String) async throws -> VideoRecord
    func submitVideo(tableId: String, url: String) async throws -> VideoSubmitResponse
    func fetchTypeStats(tableId: String) async throws -> [TypeStat]
}

final class FeishuVideoRepository: VideoRepositoryProtocol {
    private let client: FeishuAPIClient
    private let pageSize: Int
    private var pageTokenCache: [String: [Int: String]] = [:]

    init(client: FeishuAPIClient, pageSize: Int = AppConfig.Feishu.pageSize) {
        self.client = client
        self.pageSize = pageSize
    }

    func fetchRecords(tableId: String, page: Int, status: String?) async throws -> VideoListResponse {
        guard !tableId.isEmpty else {
            throw AppServiceError.missingTableID
        }

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

    func fetchRecord(tableId: String, recordId: String) async throws -> VideoRecord {
        guard !tableId.isEmpty else {
            throw AppServiceError.missingTableID
        }

        let record = try await client.getRecord(tableId: tableId, recordId: recordId)
        return record.toVideoRecord()
    }

    func submitVideo(tableId: String, url: String) async throws -> VideoSubmitResponse {
        guard !tableId.isEmpty else {
            throw AppServiceError.missingTableID
        }

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

    func fetchTypeStats(tableId: String) async throws -> [TypeStat] {
        guard !tableId.isEmpty else {
            throw AppServiceError.missingTableID
        }

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
