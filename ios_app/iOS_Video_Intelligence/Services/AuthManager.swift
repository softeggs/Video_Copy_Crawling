import Foundation
import Combine

class AuthManager: ObservableObject {
    static let shared = AuthManager()

    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var token: String?

    private let tokenKey = "authToken"
    private let userKey = "currentUser"
    private let authService: AuthServiceProtocol
    private let userDefaults: UserDefaults

    init(
        authService: AuthServiceProtocol = AppServices.authService,
        userDefaults: UserDefaults = .standard
    ) {
        self.authService = authService
        self.userDefaults = userDefaults
        restoreSession()
    }

    func login(username: String, password: String) async throws {
        let response = try await authService.login(username: username, password: password)

        await MainActor.run {
            token = response.token
            currentUser = response.user
            isAuthenticated = true
            persistSession(token: response.token, user: response.user)
        }
    }

    func logout() {
        isAuthenticated = false
        token = nil
        currentUser = nil
        userDefaults.removeObject(forKey: tokenKey)
        userDefaults.removeObject(forKey: userKey)
    }

    private func restoreSession() {
        guard
            let storedToken = userDefaults.string(forKey: tokenKey),
            let userData = userDefaults.data(forKey: userKey),
            let storedUser = try? JSONDecoder().decode(User.self, from: userData)
        else {
            logout()
            return
        }

        token = storedToken
        currentUser = storedUser
        isAuthenticated = true
    }

    private func persistSession(token: String, user: User) {
        userDefaults.set(token, forKey: tokenKey)
        if let userData = try? JSONEncoder().encode(user) {
            userDefaults.set(userData, forKey: userKey)
        }
    }
}
