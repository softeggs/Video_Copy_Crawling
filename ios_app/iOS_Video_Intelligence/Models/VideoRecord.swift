import Foundation

struct VideoRecord: Identifiable, Codable, Equatable {
    let id: String
    let title: String
    let author: String
    let url: String
    let summary: String
    let corePoints: [String]
    let correctedText: String
    let goldenSentences: [String]
    let tags: [String]
    let videoType: String
    let status: String
    let markdownContent: String
    let createdAt: String
    let processedAt: String?

    var normalizedVideoType: String {
        VideoTypeNormalizer.normalize(videoType)
    }

    var searchableContent: String {
        [
            title,
            author,
            summary,
            correctedText,
            corePoints.joined(separator: " "),
            goldenSentences.joined(separator: " "),
            tags.joined(separator: " "),
            videoType,
            normalizedVideoType,
        ]
        .joined(separator: " ")
        .lowercased()
    }

    func matchesSearch(_ query: String) -> Bool {
        let trimmedQuery = query.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard !trimmedQuery.isEmpty else {
            return true
        }

        return searchableContent.contains(trimmedQuery)
    }
}

struct User: Codable, Equatable {
    let userId: String
    let username: String
    let displayName: String
    let tableId: String

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case username
        case displayName = "display_name"
        case tableId = "table_id"
    }
}

struct LoginRequest: Codable, Equatable {
    let username: String
    let password: String
}

struct LoginResponse: Codable, Equatable {
    let token: String
    let user: User
}

struct VideoSubmitResponse: Codable, Equatable {
    let success: Bool
    let recordId: String
    let status: String
    let estimatedTime: String?
    let message: String?

    enum CodingKeys: String, CodingKey {
        case success
        case recordId = "record_id"
        case status
        case estimatedTime = "estimated_time"
        case message
    }
}

struct VideoListResponse: Codable, Equatable {
    let total: Int
    let page: Int
    let pageSize: Int
    let items: [VideoRecord]
    let hasMore: Bool

    enum CodingKeys: String, CodingKey {
        case total
        case page
        case pageSize = "page_size"
        case items
        case hasMore = "has_more"
    }
}

struct TypeStat: Identifiable, Codable, Equatable {
    var id: String { videoType }
    let videoType: String
    let count: Int
}

enum VideoTypeNormalizer {
    private static let groupedAliases: [(keywords: [String], label: String)] = [
        (["工具推荐"], "工具推荐"),
        (["教程"], "教程"),
    ]

    private static let removableSuffixes = ["类型", "类别", "类", "分享"]

    static func normalize(_ rawValue: String) -> String {
        let compacted = rawValue
            .trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: " ", with: "")

        guard !compacted.isEmpty else {
            return "其他"
        }

        for alias in groupedAliases {
            if alias.keywords.contains(where: { compacted.contains($0) }) {
                return alias.label
            }
        }

        var normalized = compacted
        for suffix in removableSuffixes {
            if normalized.hasSuffix(suffix), normalized.count > suffix.count {
                normalized = String(normalized.dropLast(suffix.count))
            }
        }

        return normalized.isEmpty ? "其他" : normalized
    }
}

struct FeishuTenantAccessTokenResponse: Codable, Equatable {
    let code: Int
    let msg: String
    let tenantAccessToken: String
    let expire: Int

    enum CodingKeys: String, CodingKey {
        case code
        case msg
        case tenantAccessToken = "tenant_access_token"
        case expire
    }
}

struct FeishuListRecordsResponse: Codable, Equatable {
    let code: Int
    let msg: String
    let data: FeishuListRecordsData
}

struct FeishuListRecordsData: Codable, Equatable {
    let hasMore: Bool
    let pageToken: String?
    let total: Int?
    let items: [FeishuRecord]

    enum CodingKeys: String, CodingKey {
        case hasMore = "has_more"
        case pageToken = "page_token"
        case total
        case items
    }
}

struct FeishuRecordEnvelopeResponse: Codable, Equatable {
    let code: Int
    let msg: String
    let data: FeishuRecordEnvelopeData
}

struct FeishuRecordEnvelopeData: Codable, Equatable {
    let record: FeishuRecord
}

enum FeishuFieldValue: Codable, Equatable {
    case string(String)
    case int(Int)
    case double(Double)
    case bool(Bool)
    case array([FeishuFieldValue])
    case dictionary([String: FeishuFieldValue])
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if container.decodeNil() {
            self = .null
        } else if let value = try? container.decode([String: FeishuFieldValue].self) {
            self = .dictionary(value)
        } else if let value = try? container.decode([FeishuFieldValue].self) {
            self = .array(value)
        } else if let value = try? container.decode(Int.self) {
            self = .int(value)
        } else if let value = try? container.decode(Double.self) {
            self = .double(value)
        } else if let value = try? container.decode(Bool.self) {
            self = .bool(value)
        } else if let value = try? container.decode(String.self) {
            self = .string(value)
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported Feishu field value")
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        switch self {
        case .string(let value):
            try container.encode(value)
        case .int(let value):
            try container.encode(value)
        case .double(let value):
            try container.encode(value)
        case .bool(let value):
            try container.encode(value)
        case .array(let value):
            try container.encode(value)
        case .dictionary(let value):
            try container.encode(value)
        case .null:
            try container.encodeNil()
        }
    }

    var stringValue: String? {
        switch self {
        case .string(let value):
            return value
        case .int(let value):
            return String(value)
        case .double(let value):
            return String(value)
        case .bool(let value):
            return String(value)
        case .dictionary(let value):
            return value["text"]?.stringValue ?? value["link"]?.stringValue ?? value["name"]?.stringValue
        case .array(let value):
            let strings = value.compactMap { $0.stringValue?.trimmingCharacters(in: .whitespacesAndNewlines) }
            return strings.isEmpty ? nil : strings.joined(separator: ", ")
        case .null:
            return nil
        }
    }

    var arrayValue: [FeishuFieldValue]? {
        if case .array(let value) = self {
            return value
        }

        return nil
    }

    var dictionaryValue: [String: FeishuFieldValue]? {
        if case .dictionary(let value) = self {
            return value
        }

        return nil
    }

    var int64Value: Int64? {
        switch self {
        case .int(let value):
            return Int64(value)
        case .double(let value):
            return Int64(value)
        case .string(let value):
            return Int64(value)
        default:
            return nil
        }
    }
}

struct FeishuRecord: Codable, Equatable {
    let recordId: String
    let fields: [String: FeishuFieldValue]
    let createdTime: Int64?
    let lastModifiedTime: Int64?

    enum CodingKeys: String, CodingKey {
        case recordId = "record_id"
        case fields
        case createdTime = "created_time"
        case lastModifiedTime = "last_modified_time"
    }

    func toVideoRecord() -> VideoRecord {
        VideoRecord(
            id: recordId,
            title: stringField(named: "标题", fallback: "未命名记录"),
            author: stringField(named: "作者"),
            url: linkField(named: "原始链接"),
            summary: stringField(named: "一句话总结"),
            corePoints: multilineField(named: "核心观点"),
            correctedText: stringField(named: "详细内容"),
            goldenSentences: multilineField(named: "金句"),
            tags: tagsField(named: "标签"),
            videoType: stringField(named: "视频类型", fallback: "其他"),
            status: stringField(named: "处理状态", fallback: AppConfig.Feishu.defaultSubmitStatus),
            markdownContent: stringField(named: "笔记路径"),
            createdAt: Self.iso8601(fromMilliseconds: createdTime) ?? "",
            processedAt: timestampField(named: "处理时间")
        )
    }

    private func stringField(named name: String, fallback: String = "") -> String {
        guard let value = fields[name] else {
            return fallback
        }

        return value.stringValue?.trimmingCharacters(in: .whitespacesAndNewlines).nonEmpty ?? fallback
    }

    private func multilineField(named name: String) -> [String] {
        stringField(named: name)
            .components(separatedBy: .newlines)
            .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
            .filter { !$0.isEmpty }
    }

    private func tagsField(named name: String) -> [String] {
        guard let value = fields[name] else {
            return []
        }

        if let arrayValue = value.arrayValue {
            return arrayValue
                .compactMap { item in
                    if let dictionaryValue = item.dictionaryValue {
                        return dictionaryValue["text"]?.stringValue ?? dictionaryValue["name"]?.stringValue
                    }

                    return item.stringValue
                }
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
        }

        if let stringValue = value.stringValue {
            return stringValue
                .components(separatedBy: CharacterSet(charactersIn: ",，\n"))
                .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                .filter { !$0.isEmpty }
        }

        return []
    }

    private func linkField(named name: String) -> String {
        guard let value = fields[name] else {
            return ""
        }

        if let dictionaryValue = value.dictionaryValue {
            return dictionaryValue["link"]?.stringValue ?? dictionaryValue["text"]?.stringValue ?? ""
        }

        return value.stringValue ?? ""
    }

    private func timestampField(named name: String) -> String? {
        guard let milliseconds = fields[name]?.int64Value else {
            return nil
        }

        return Self.iso8601(fromMilliseconds: milliseconds)
    }

    static func iso8601(fromMilliseconds milliseconds: Int64?) -> String? {
        guard let milliseconds else {
            return nil
        }

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let date = Date(timeIntervalSince1970: TimeInterval(milliseconds) / 1000)
        return formatter.string(from: date)
    }
}

private extension String {
    var nonEmpty: String? {
        isEmpty ? nil : self
    }
}
