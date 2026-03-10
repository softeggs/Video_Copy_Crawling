import Foundation

struct VideoRecord: Identifiable, Codable {
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
    let createdAt: String // ISO8601 String
    let processedAt: String?

    enum CodingKeys: String, CodingKey {
        case id = "record_id"
        case title, author, url, summary
        case corePoints = "core_points"
        case correctedText = "corrected_text"
        case goldenSentences = "golden_sentences"
        case tags
        case videoType = "video_type"
        case status
        case markdownContent = "markdown_content"
        case createdAt = "created_at"
        case processedAt = "processed_at"
    }
}

struct User: Codable {
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

struct LoginRequest: Codable {
    let username: String
    let password: String
}

struct LoginResponse: Codable {
    let token: String
    let user: User
}

struct VideoSubmitResponse: Codable {
    let success: Bool
    let recordId: String
    let status: String
    let estimatedTime: String
    let message: String?
    
    enum CodingKeys: String, CodingKey {
        case success
        case recordId = "record_id"
        case status
        case estimatedTime = "estimated_time"
        case message
    }
}

struct VideoListResponse: Codable {
    let total: Int
    let page: Int
    let pageSize: Int
    let items: [VideoRecord]
    
    enum CodingKeys: String, CodingKey {
        case total, page
        case pageSize = "page_size"
        case items
    }
}
