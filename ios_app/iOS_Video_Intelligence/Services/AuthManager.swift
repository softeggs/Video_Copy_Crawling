import Foundation
import Combine

class AuthManager: ObservableObject {
    static let shared = AuthManager()

    @Published var isAuthenticated = false
    @Published var isRestoringSession = true
    @Published var currentUser: User?
    @Published var token: String?

    private let tokenKey = "authToken"
    private let userKey = "currentUser"
    private let authService: AuthServiceProtocol
    private let userDefaults: UserDefaults
    private var sessionExpiredObserver: NSObjectProtocol?

    init(
        authService: AuthServiceProtocol = AppServices.authService,
        userDefaults: UserDefaults = .standard
    ) {
        self.authService = authService
        self.userDefaults = userDefaults
        sessionExpiredObserver = NotificationCenter.default.addObserver(
            forName: .authSessionExpired,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.applyLoggedOutState(clearPersistedSession: true)
        }
        restoreSession()
    }

    deinit {
        if let sessionExpiredObserver {
            NotificationCenter.default.removeObserver(sessionExpiredObserver)
        }
    }

    func login(username: String, password: String) async throws {
        let response = try await authService.login(username: username, password: password)

        await MainActor.run {
            token = response.token
            currentUser = response.user
            isAuthenticated = true
            isRestoringSession = false
            persistSession(token: response.token, user: response.user)
        }
    }

    func logout() {
        applyLoggedOutState(clearPersistedSession: true)
    }

    func handleSessionExpirationIfNeeded(_ error: Error) async -> Bool {
        guard case AppServiceError.unauthorized = error as? AppServiceError else {
            return false
        }

        await MainActor.run {
            applyLoggedOutState(clearPersistedSession: true)
        }
        return true
    }

    private func restoreSession() {
        guard
            let storedToken = userDefaults.string(forKey: tokenKey),
            let userData = userDefaults.data(forKey: userKey),
            let storedUser = try? JSONDecoder().decode(User.self, from: userData)
        else {
            applyLoggedOutState(clearPersistedSession: true)
            return
        }

        token = storedToken
        currentUser = storedUser
        isAuthenticated = false
        isRestoringSession = true

        Task {
            await validateRestoredSession(token: storedToken)
        }
    }

    @MainActor
    private func validateRestoredSession(token: String) async {
        do {
            let user = try await authService.fetchCurrentUser(token: token)
            self.token = token
            currentUser = user
            isAuthenticated = true
            isRestoringSession = false
            persistSession(token: token, user: user)
        } catch {
            applyLoggedOutState(clearPersistedSession: true)
        }
    }

    private func applyLoggedOutState(clearPersistedSession: Bool) {
        isAuthenticated = false
        isRestoringSession = false
        token = nil
        currentUser = nil

        guard clearPersistedSession else {
            return
        }

        userDefaults.removeObject(forKey: tokenKey)
        userDefaults.removeObject(forKey: userKey)
    }

    private func persistSession(token: String, user: User) {
        userDefaults.set(token, forKey: tokenKey)
        if let userData = try? JSONEncoder().encode(user) {
            userDefaults.set(userData, forKey: userKey)
        }
    }
}

extension Notification.Name {
    static let authSessionExpired = Notification.Name("AuthSessionExpired")
}
