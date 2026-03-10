import SwiftUI

struct SubmitView: View {
    @State private var url: String = ""
    @State private var isSubmitting: Bool = false
    @State private var showSuccess: Bool = false
    @State private var errorMessage: String?
    @EnvironmentObject var authManager: AuthManager
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F7F8FA").edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 24) {
                    // Header
                    VStack(alignment: .leading, spacing: 8) {
                        Text("New Submission")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(Color(hex: "1F2329"))
                        
                        Text("Paste a video link from Douyin, Bilibili or Xiaohongshu")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                    .padding(.top, 20)
                    
                    // Input Card
                    VStack(spacing: 16) {
                        TextField("https://...", text: $url)
                            .padding()
                            .background(Color(hex: "F0F2F5"))
                            .cornerRadius(12)
                            .disableAutocorrection(true)
                            .autocapitalization(.none)
                        
                        Button(action: pasteFromClipboard) {
                            HStack {
                                Image(systemName: "doc.on.clipboard")
                                Text("Paste from Clipboard")
                            }
                            .font(.subheadline)
                            .foregroundColor(Color(hex: "5E5CE6"))
                        }
                    }
                    .padding(20)
                    .background(Color.white)
                    .cornerRadius(16)
                    .shadow(color: Color.black.opacity(0.05), radius: 10, x: 0, y: 5)
                    .padding(.horizontal)
                    
                    if let errorMessage = errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                            .padding(.horizontal)
                    }
                    
                    // Submit Button
                    Button(action: submitVideo) {
                        HStack {
                            if isSubmitting {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("Submit Video")
                                    .fontWeight(.semibold)
                                Image(systemName: "arrow.up.circle.fill")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            url.isEmpty ? Color.gray.opacity(0.5) : Color(hex: "5E5CE6")
                        )
                        .foregroundColor(.white)
                        .cornerRadius(12)
                        .shadow(color: url.isEmpty ? .clear : Color(hex: "5E5CE6").opacity(0.3), radius: 8, x: 0, y: 4)
                    }
                    .disabled(url.isEmpty || isSubmitting)
                    .padding(.horizontal)
                    
                    Spacer()
                    
                    // Quick Stats
                    HStack(spacing: 40) {
                        VStack {
                            Text("12")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("Today")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        VStack {
                            Text("3")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(Color(hex: "FAAD14"))
                            Text("Processing")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    }
                    .padding(.bottom, 40)
                }
            }
            .navigationBarHidden(true)
            .alert(isPresented: $showSuccess) {
                Alert(
                    title: Text("Submission Successful"),
                    message: Text("The video has been added to the queue."),
                    dismissButton: .default(Text("OK")) {
                        url = ""
                    }
                )
            }
        }
    }
    
    private func pasteFromClipboard() {
        if let string = UIPasteboard.general.string {
            url = string
        }
    }
    
    private func submitVideo() {
        guard !url.isEmpty else { return }
        guard let token = authManager.token else { return }
        
        isSubmitting = true
        errorMessage = nil
        
        Task {
            do {
                let response = try await APIService.shared.submitVideo(videoUrl: url, token: token)
                await MainActor.run {
                    isSubmitting = false
                    if response.success {
                        showSuccess = true
                    } else {
                        errorMessage = response.message ?? "Submission failed"
                    }
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    errorMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}
