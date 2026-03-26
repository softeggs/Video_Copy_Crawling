import SwiftUI

struct DetailView: View {
    let video: VideoRecord
    @EnvironmentObject private var authManager: AuthManager
    @State private var displayedVideo: VideoRecord
    @State private var errorMessage: String?
    @State private var isLoading = false

    private let videoRepository: VideoRepositoryProtocol = AppServices.videoRepository

    init(video: VideoRecord) {
        self.video = video
        _displayedVideo = State(initialValue: video)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                if let errorMessage {
                    InlineErrorView(message: errorMessage)
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text(displayedVideo.title)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "1F2329"))

                    HStack {
                        Label(displayedVideo.author.isEmpty ? "未知作者" : displayedVideo.author, systemImage: "person.fill")
                        Spacer()
                        Label(displayedVideo.normalizedVideoType, systemImage: "play.circle.fill")
                        Spacer()
                        Text((displayedVideo.processedAt ?? displayedVideo.createdAt).prefix(10))
                            .foregroundColor(.gray)
                    }
                    .font(.subheadline)
                    .foregroundColor(Color(hex: "646A73"))
                }
                .padding()
                .background(Color.white)
                .cornerRadius(12)
                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)

                VStack(alignment: .leading, spacing: 12) {
                    Label("一句话总结", systemImage: "star.fill")
                        .font(.headline)
                        .foregroundColor(Color(hex: "5E5CE6"))

                    if isLoading && displayedVideo.summary.isEmpty {
                        ProgressView()
                    } else {
                        Text(displayedVideo.summary.isEmpty ? "暂无总结" : displayedVideo.summary)
                            .font(.body)
                            .foregroundColor(Color(hex: "1F2329"))
                            .lineSpacing(4)
                    }
                }
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color(hex: "5E5CE6").opacity(0.1))
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(hex: "5E5CE6").opacity(0.3), lineWidth: 1)
                )

                if !displayedVideo.url.isEmpty {
                    SourceLinkCard(videoURL: displayedVideo.url)
                }

                if !displayedVideo.corePoints.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("核心观点", systemImage: "list.bullet")
                            .font(.headline)
                            .foregroundColor(Color(hex: "1F2329"))

                        ForEach(Array(displayedVideo.corePoints.enumerated()), id: \.offset) { index, point in
                            HStack(alignment: .top, spacing: 12) {
                                Text("\(index + 1).")
                                    .font(.system(.body, design: .monospaced))
                                    .fontWeight(.bold)
                                    .foregroundColor(Color(hex: "5E5CE6"))
                                Text(point)
                                    .font(.body)
                                    .foregroundColor(Color(hex: "1F2329"))
                            }
                        }
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                }

                if !displayedVideo.goldenSentences.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("金句摘录", systemImage: "quote.opening")
                            .font(.headline)
                            .foregroundColor(Color(hex: "FAAD14"))

                        ForEach(displayedVideo.goldenSentences, id: \.self) { sentence in
                            HStack {
                                Rectangle()
                                    .fill(Color(hex: "FAAD14"))
                                    .frame(width: 4)
                                Text(sentence)
                                    .font(.system(.body, design: .serif))
                                    .italic()
                                    .foregroundColor(Color(hex: "646A73"))
                            }
                            .padding(.vertical, 4)
                        }
                    }
                    .padding()
                    .background(Color(hex: "FFFBE6"))
                    .cornerRadius(12)
                }

                if !displayedVideo.correctedText.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("详细内容", systemImage: "text.aligncenter")
                            .font(.headline)

                        Text(displayedVideo.correctedText)
                            .font(.body)
                            .foregroundColor(Color(hex: "1F2329"))
                            .lineSpacing(6)
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(12)
                }
            }
            .padding()
        }
        .background(Color(hex: "F7F8FA").edgesIgnoringSafeArea(.all))
        .navigationBarTitleDisplayMode(.inline)
        .task(id: video.id) {
            await loadLatestDetail()
        }
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: {
                    let text = """
                    \(displayedVideo.title)
                    - \(displayedVideo.author)

                    总结：\(displayedVideo.summary)

                    链接：\(displayedVideo.url)
                    """
                    let av = UIActivityViewController(activityItems: [text], applicationActivities: nil)
                    if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
                       let rootViewController = windowScene.windows.first(where: { $0.isKeyWindow })?.rootViewController {
                        rootViewController.present(av, animated: true)
                    }
                }) {
                    Image(systemName: "square.and.arrow.up")
                }
            }
        }
    }

    private func loadLatestDetail() async {
        guard let token = authManager.token else {
            return
        }

        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let latestVideo = try await videoRepository.fetchRecord(token: token, recordId: video.id)
            await MainActor.run {
                displayedVideo = latestVideo
                isLoading = false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }
}

struct SourceLinkCard: View {
    let videoURL: String
    @Environment(\.openURL) private var openURL

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("视频原始链接", systemImage: "link")
                .font(.headline)
                .foregroundColor(Color(hex: "3370FF"))

            Button {
                guard let url = URL(string: videoURL) else { return }
                openURL(url)
            } label: {
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: "arrow.up.forward.square")
                        .foregroundColor(Color(hex: "3370FF"))
                    Text(videoURL)
                        .font(.subheadline)
                        .foregroundColor(Color(hex: "3370FF"))
                        .multilineTextAlignment(.leading)
                        .underline()
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.plain)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}
