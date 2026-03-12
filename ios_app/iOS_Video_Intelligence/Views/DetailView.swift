import SwiftUI

struct DetailView: View {
    let video: VideoRecord

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                VStack(alignment: .leading, spacing: 12) {
                    Text(video.title)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "1F2329"))

                    HStack {
                        Label(video.author, systemImage: "person.fill")
                        Spacer()
                        Label(video.normalizedVideoType, systemImage: "play.circle.fill")
                        Spacer()
                        Text((video.processedAt ?? video.createdAt).prefix(10))
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

                    Text(video.summary)
                        .font(.body)
                        .foregroundColor(Color(hex: "1F2329"))
                        .lineSpacing(4)
                }
                .padding()
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color(hex: "5E5CE6").opacity(0.1))
                .cornerRadius(12)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color(hex: "5E5CE6").opacity(0.3), lineWidth: 1)
                )

                if !video.url.isEmpty {
                    SourceLinkCard(videoURL: video.url)
                }

                if !video.corePoints.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("核心观点", systemImage: "list.bullet")
                            .font(.headline)
                            .foregroundColor(Color(hex: "1F2329"))

                        ForEach(Array(video.corePoints.enumerated()), id: \.offset) { index, point in
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

                if !video.goldenSentences.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("金句摘录", systemImage: "quote.opening")
                            .font(.headline)
                            .foregroundColor(Color(hex: "FAAD14"))

                        ForEach(video.goldenSentences, id: \.self) { sentence in
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

                if !video.correctedText.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("详细内容", systemImage: "text.aligncenter")
                            .font(.headline)

                        Text(video.correctedText)
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
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: {
                    let text = """
                    \(video.title)
                    - \(video.author)

                    总结：\(video.summary)

                    链接：\(video.url)
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
