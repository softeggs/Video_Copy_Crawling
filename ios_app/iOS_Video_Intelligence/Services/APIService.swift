import Foundation

enum APIError: Error {
    case invalidURL
    case encodingError
    case unauthorized
    case serverError(String)
    case decodingError
    case unknown
}

class APIService {
    static let shared = APIService()
    private init() {}
    
    private let baseURL = "http://127.0.0.1:8001" // Local development URL
    
    func login(request: LoginRequest) async throws -> LoginResponse {
        let urlString = "\(baseURL)/api/auth/token"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let bodyString = "username=\(request.username)&password=\(request.password)"
        urlRequest.httpBody = bodyString.data(using: .utf8)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse else { throw APIError.unknown }
        
        if httpResponse.statusCode == 200 {
            do {
                return try JSONDecoder().decode(LoginResponse.self, from: data)
            } catch {
                throw APIError.decodingError
            }
        } else {
            throw APIError.unauthorized
        }
    }
    
    func submitVideo(videoUrl: String, token: String) async throws -> VideoSubmitResponse {
        let urlString = "\(baseURL)/api/videos/submit"
        guard let url = URL(string: urlString) else { throw APIError.invalidURL }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body: [String: String] = ["url": videoUrl, "source": "app"]
        urlRequest.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.serverError("Submission Failed")
        }
        
        return try JSONDecoder().decode(VideoSubmitResponse.self, from: data)
    }
    
    func fetchVideos(page: Int = 1, status: String? = nil, token: String) async throws -> VideoListResponse {
        var components = URLComponents(string: "\(baseURL)/api/videos/list")
        components?.queryItems = [
            URLQueryItem(name: "page", value: "\(page)"),
            URLQueryItem(name: "page_size", value: "20")
        ]
        
        if let status = status {
            components?.queryItems?.append(URLQueryItem(name: "status", value: status))
        }
        
        guard let url = components?.url else { throw APIError.invalidURL }
        
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "GET"
        urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: urlRequest)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw APIError.serverError("Fetch Failed")
        }
        
        return try JSONDecoder().decode(VideoListResponse.self, from: data)
    }
}
