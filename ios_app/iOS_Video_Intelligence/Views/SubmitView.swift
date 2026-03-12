import SwiftUI

struct SubmitView: View {
    @State private var url = ""
    @State private var isSubmitting = false
    @State private var showSuccess = false
    @State private var errorMessage: String?
    @State private var typeStats: [TypeStat] = []
    @State private var isLoadingStats = false
    @EnvironmentObject var authManager: AuthManager

    private let videoRepository: VideoRepositoryProtocol = AppServices.videoRepository
    private let statColumns = [GridItem(.flexible()), GridItem(.flexible())]

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("新建提交")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(Color(hex: "1F2329"))

                        Text("粘贴抖音、B站或小红书视频链接")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)
                    .padding(.top, 20)

                    VStack(spacing: 16) {
                        TextField("请输入视频链接", text: $url)
                            .padding()
                            .background(Color(hex: "F0F2F5"))
                            .cornerRadius(12)
                            .disableAutocorrection(true)
                            .autocapitalization(.none)

                        Button(action: pasteFromClipboard) {
                            HStack {
                                Image(systemName: "doc.on.clipboard")
                                Text("从剪贴板粘贴")
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

                    if let errorMessage {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.caption)
                            .padding(.horizontal)
                    }

                    Button(action: submitVideo) {
                        HStack {
                            if isSubmitting {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            } else {
                                Text("提交视频")
                                    .fontWeight(.semibold)
                                Image(systemName: "arrow.up.circle.fill")
                            }
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(url.isEmpty ? Color.gray.opacity(0.5) : Color(hex: "5E5CE6"))
                        .foregroundColor(.white)
                        .cornerRadius(12)
                        .shadow(
                            color: url.isEmpty ? .clear : Color(hex: "5E5CE6").opacity(0.3),
                            radius: 8,
                            x: 0,
                            y: 4
                        )
                    }
                    .disabled(url.isEmpty || isSubmitting)
                    .padding(.horizontal)

                    VStack(alignment: .leading, spacing: 16) {
                        HStack {
                            Text("视频类型统计")
                                .font(.headline)
                                .foregroundColor(Color(hex: "1F2329"))

                            Spacer()

                            if isLoadingStats {
                                ProgressView()
                                    .progressViewStyle(.circular)
                            }
                        }

                        if !isLoadingStats && typeStats.isEmpty {
                            Text("暂无记录，提交第一条视频后这里会显示统计。")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        } else {
                            LazyVGrid(columns: statColumns, spacing: 12) {
                                ForEach(typeStats) { stat in
                                    TypeStatCard(stat: stat)
                                }
                            }
                        }
                    }
                    .padding(20)
                    .background(Color.white)
                    .cornerRadius(16)
                    .shadow(color: Color.black.opacity(0.05), radius: 10, x: 0, y: 5)
                    .padding(.horizontal)

                    Spacer(minLength: 24)
                }
            }
            .background(Color(hex: "F7F8FA").ignoresSafeArea())
            .navigationBarHidden(true)
            .task(id: authManager.currentUser?.tableId) {
                await loadTypeStats()
            }
            .alert(isPresented: $showSuccess) {
                Alert(
                    title: Text("提交成功"),
                    message: Text("该视频已加入处理队列。"),
                    dismissButton: .default(Text("确定"))
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
        guard let tableId = authManager.currentUser?.tableId else {
            errorMessage = AppServiceError.missingCurrentUser.localizedDescription
            return
        }

        isSubmitting = true
        errorMessage = nil

        Task {
            do {
                let response = try await videoRepository.submitVideo(tableId: tableId, url: url)
                let refreshedStats = try? await videoRepository.fetchTypeStats(tableId: tableId)

                await MainActor.run {
                    isSubmitting = false
                    if response.success {
                        url = ""
                        typeStats = refreshedStats ?? typeStats
                        showSuccess = true
                    } else {
                        errorMessage = response.message ?? "提交失败"
                    }
                }
            } catch {
                await MainActor.run {
                    isSubmitting = false
                    errorMessage = error.localizedDescription
                }
            }
        }
    }

    private func loadTypeStats() async {
        guard let tableId = authManager.currentUser?.tableId else {
            await MainActor.run {
                typeStats = []
                isLoadingStats = false
            }
            return
        }

        await MainActor.run {
            isLoadingStats = true
        }

        do {
            let stats = try await videoRepository.fetchTypeStats(tableId: tableId)
            await MainActor.run {
                typeStats = stats
                isLoadingStats = false
            }
        } catch {
            await MainActor.run {
                typeStats = []
                isLoadingStats = false
                errorMessage = error.localizedDescription
            }
        }
    }
}

struct TypeStatCard: View {
    let stat: TypeStat

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(stat.videoType)
                .font(.headline)
                .foregroundColor(Color(hex: "1F2329"))
                .lineLimit(1)

            Text("\(stat.count)")
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(Color(hex: "5E5CE6"))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color(hex: "F7F8FA"))
        .cornerRadius(12)
    }
}
