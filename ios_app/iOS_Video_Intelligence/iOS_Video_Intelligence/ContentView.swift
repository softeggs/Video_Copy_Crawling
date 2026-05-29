import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        Group {
            if authManager.isRestoringSession {
                SessionRestoreView()
            } else if authManager.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
    }
}

private struct SessionRestoreView: View {
    var body: some View {
        ZStack {
            Color(hex: "F7F8FA").ignoresSafeArea()

            VStack(spacing: 16) {
                ProgressView()
                    .progressViewStyle(.circular)
                    .scaleEffect(1.2)

                Text("Restoring session...")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }
        }
    }
}
