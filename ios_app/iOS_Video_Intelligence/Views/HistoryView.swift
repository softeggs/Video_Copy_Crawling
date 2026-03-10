import SwiftUI

struct HistoryView: View {
    @State private var videos: [VideoRecord] = []
    @State private var isLoading: Bool = false
    @State private var errorMessage: String?
    @EnvironmentObject var authManager: AuthManager
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F7F8FA").edgesIgnoringSafeArea(.all)
                
                if isLoading && videos.isEmpty {
                    ProgressView()
                } else if videos.isEmpty {
                    EmptyStateView()
                } else {
                    List {
                        ForEach(videos) { video in
                            ZStack {
                                NavigationLink(destination: DetailView(video: video)) {
                                    EmptyView()
                                }
                                .opacity(0)
                                
                                VideoCard(video: video)
                            }
                            .listRowBackground(Color.clear)
                            .listRowSeparator(.hidden)
                            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
                        }
                    }
                    .listStyle(.plain)
                    .refreshable {
                        await loadData()
                    }
                }
            }
            .navigationTitle("Records")
            .onAppear {
                Task { await loadData() }
            }
        }
    }
    
    private func loadData() async {
        guard let token = authManager.token else { return }
        
        isLoading = true
        do {
            let response = try await APIService.shared.fetchVideos(token: token)
            await MainActor.run {
                self.videos = response.items
                self.isLoading = false
            }
        } catch {
            await MainActor.run {
                self.errorMessage = error.localizedDescription
                self.isLoading = false
            }
        }
    }
}

struct VideoCard: View {
    let video: VideoRecord
    
    var statusColor: Color {
        switch video.status {
        case "已完成": return Color(hex: "52C41A")
        case "处理中": return Color(hex: "1890FF")
        case "失败": return Color(hex: "F5222D")
        default: return Color(hex: "FAAD14")
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(video.title)
                    .font(.headline)
                    .lineLimit(1)
                    .foregroundColor(Color(hex: "1F2329"))
                
                Spacer()
                
                Text(video.status)
                    .font(.caption2)
                    .fontWeight(.bold)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(statusColor.opacity(0.1))
                    .foregroundColor(statusColor)
                    .cornerRadius(4)
            }
            
            HStack {
                Image(systemName: "person.fill")
                    .font(.caption)
                Text(video.author)
                    .font(.caption)
                
                Text("•")
                
                Image(systemName: "play.circle.fill")
                    .font(.caption)
                Text(video.videoType)
                    .font(.caption)
            }
            .foregroundColor(.gray)
            
            Text(video.summary)
                .font(.subheadline)
                .foregroundColor(Color(hex: "646A73"))
                .lineLimit(2)
            
            HStack {
                Text(video.createdAt.prefix(10)) // Simple date formatting
                    .font(.caption2)
                    .foregroundColor(.gray.opacity(0.8))
                
                Spacer()
                
                if !video.tags.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack {
                            ForEach(video.tags.prefix(3), id: \.self) { tag in
                                Text("#\(tag)")
                                    .font(.caption2)
                                    .foregroundColor(Color(hex: "5E5CE6"))
                                    .padding(.horizontal, 6)
                                    .padding(.vertical, 2)
                                    .background(Color(hex: "5E5CE6").opacity(0.1))
                                    .cornerRadius(4)
                            }
                        }
                    }
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

struct EmptyStateView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 50))
                .foregroundColor(.gray.opacity(0.5))
            Text("No records found")
                .font(.headline)
                .foregroundColor(.gray)
        }
    }
}
