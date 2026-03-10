import SwiftUI

struct LoginView: View {
    @StateObject private var authManager = AuthManager.shared
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        ZStack {
            Color(hex: "F7F8FA").edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 30) {
                // Logo Area
                VStack(spacing: 10) {
                    Image(systemName: "video.bubble.left.fill")
                        .font(.system(size: 60))
                        .foregroundStyle(LinearGradient(colors: [Color(hex: "5E5CE6"), Color(hex: "3370FF")], startPoint: .topLeading, endPoint: .bottomTrailing))
                    
                    Text("Video Intelligence")
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "1F2329"))
                    
                    Text("Professional Intelligence Extraction")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }
                .padding(.top, 60)
                
                // Form Area
                VStack(spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Username")
                            .font(.caption)
                            .foregroundColor(.gray)
                        TextField("Enter username", text: $username)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(8)
                            .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.gray.opacity(0.2), lineWidth: 1))
                            .textInputAutocapitalization(.never)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Password")
                            .font(.caption)
                            .foregroundColor(.gray)
                        SecureField("Enter password", text: $password)
                            .padding()
                            .background(Color.white)
                            .cornerRadius(8)
                            .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.gray.opacity(0.2), lineWidth: 1))
                    }
                    
                    if let errorMessage = errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                    
                    Button(action: login) {
                        HStack {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("Login")
                                    .fontWeight(.semibold)
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            LinearGradient(colors: [Color(hex: "5E5CE6"), Color(hex: "3370FF")], startPoint: .leading, endPoint: .trailing)
                        )
                        .foregroundColor(.white)
                        .cornerRadius(8)
                        .shadow(color: Color(hex: "5E5CE6").opacity(0.3), radius: 5, x: 0, y: 3)
                    }
                    .disabled(isLoading || username.isEmpty || password.isEmpty)
                }
                .padding(24)
                .background(Color.white)
                .cornerRadius(16)
                .shadow(color: Color.black.opacity(0.05), radius: 10, x: 0, y: 5)
                .padding(.horizontal)
                
                Spacer()
                
                Text("Test Account: test_user / test123")
                    .font(.caption)
                    .foregroundColor(.gray)
                    .padding(.bottom, 20)
            }
        }
    }
    
    private func login() {
        isLoading = true
        errorMessage = nil
        
        Task {
            do {
                try await authManager.login(username: username, password: password)
                // Success handled by AuthManager publishing change
            } catch {
                await MainActor.run {
                    errorMessage = "Login failed: \(error.localizedDescription)"
                    isLoading = false
                }
            }
        }
    }
}


