import Foundation
import Combine

class AuthManager: ObservableObject {
    static let shared = AuthManager()
    
    @Published var isAuthenticated: Bool = false
    @Published var currentUser: User?
    @Published var token: String?
    
    private let tokenKey = "authToken"
    private let userKey = "currentUser"
    
    private init() {
        // 默认直接登录,不需要账号密码验证
        self.isAuthenticated = true
        self.token = "mock_token"
        self.currentUser = User(
            userId: "default_user",
            username: "user",
            displayName: "默认用户",
            tableId: "default_table"
        )
    }
    
    func login(username: String, password: String) async throws {
        let request = LoginRequest(username: username, password: password)
        let response = try await APIService.shared.login(request: request)
        
        await MainActor.run {
            self.token = response.token
            self.currentUser = response.user
            self.isAuthenticated = true
            
            // Persist
            UserDefaults.standard.set(response.token, forKey: tokenKey)
            if let userData = try? JSONEncoder().encode(response.user) {
                UserDefaults.standard.set(userData, forKey: userKey)
            }
        }
    }
    
    func logout() {
        self.isAuthenticated = false
        self.token = nil
        self.currentUser = nil
        UserDefaults.standard.removeObject(forKey: tokenKey)
        UserDefaults.standard.removeObject(forKey: userKey)
    }
}
