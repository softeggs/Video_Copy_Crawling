import SwiftUI

private enum RecordSortOption: String, CaseIterable, Identifiable {
    case newestFirst = "最新优先"
    case oldestFirst = "最早优先"

    var id: String { rawValue }
}

struct HistoryView: View {
    private let allCategoriesLabel = "全部类别"

    @State private var allVideos: [VideoRecord] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var loadedTableId: String?
    @State private var searchText = ""
    @State private var selectedSort: RecordSortOption = .newestFirst
    @State private var selectedCategory = "全部类别"
    @EnvironmentObject var authManager: AuthManager

    private let videoRepository: VideoRepositoryProtocol = AppServices.videoRepository

    private var availableCategories: [String] {
        [allCategoriesLabel] + Array(Set(allVideos.map(\.normalizedVideoType))).sorted()
    }

    private var filteredVideos: [VideoRecord] {
        var result = allVideos.filter { video in
            video.matchesSearch(searchText)
        }

        if selectedCategory != allCategoriesLabel {
            result = result.filter { $0.normalizedVideoType == selectedCategory }
        }

        return result.sorted(by: sortComparator)
    }

    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F7F8FA").edgesIgnoringSafeArea(.all)

                VStack(spacing: 0) {
                    if let errorMessage {
                        InlineErrorView(message: errorMessage)
                            .padding([.horizontal, .top])
                    }

                    filterToolbar
                        .padding(.horizontal)
                        .padding(.top, errorMessage == nil ? 12 : 8)
                        .padding(.bottom, 8)

                    if isLoading && allVideos.isEmpty {
                        Spacer()
                        ProgressView()
                        Spacer()
                    } else if filteredVideos.isEmpty {
                        Spacer()
                        EmptyStateView(
                            title: searchText.isEmpty ? "暂无记录" : "没有匹配结果",
                            subtitle: searchText.isEmpty ? "下拉刷新以获取最新处理结果。" : "试试其他关键词或筛选条件。"
                        )
                        Spacer()
                    } else {
                        List {
                            ForEach(filteredVideos) { video in
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
                            await refreshData()
                        }
                    }
                }
            }
            .navigationTitle("记录")
            .searchable(text: $searchText, prompt: "搜索详细内容")
            .task(id: authManager.currentUser?.tableId) {
                guard let tableId = authManager.currentUser?.tableId else {
                    await MainActor.run {
                        loadedTableId = nil
                        allVideos = []
                        errorMessage = nil
                    }
                    return
                }

                guard loadedTableId != tableId || allVideos.isEmpty else {
                    return
                }

                await MainActor.run {
                    loadedTableId = tableId
                }
                await refreshData()
            }
        }
    }

    private var filterToolbar: some View {
        HStack(spacing: 12) {
            Menu {
                Picker("排序方式", selection: $selectedSort) {
                    ForEach(RecordSortOption.allCases) { option in
                        Text(option.rawValue).tag(option)
                    }
                }
            } label: {
                FilterChip(title: selectedSort.rawValue, systemImage: "arrow.up.arrow.down")
            }

            Menu {
                Picker("类别筛选", selection: $selectedCategory) {
                    ForEach(availableCategories, id: \.self) { category in
                        Text(category).tag(category)
                    }
                }
            } label: {
                FilterChip(title: selectedCategory, systemImage: "line.3.horizontal.decrease.circle")
            }

            Spacer()

            Text("共 \(filteredVideos.count) 条")
                .font(.caption)
                .foregroundColor(.gray)
        }
    }

    private func refreshData() async {
        guard let tableId = authManager.currentUser?.tableId else {
            await MainActor.run {
                errorMessage = AppServiceError.missingCurrentUser.localizedDescription
            }
            return
        }

        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let videos = try await loadAllRecords(tableId: tableId)
            await MainActor.run {
                allVideos = videos
                if !availableCategories.contains(selectedCategory) {
                    selectedCategory = allCategoriesLabel
                }
                isLoading = false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func loadAllRecords(tableId: String) async throws -> [VideoRecord] {
        var page = 1
        var hasMore = false
        var loadedRecords: [VideoRecord] = []

        repeat {
            let response = try await videoRepository.fetchRecords(tableId: tableId, page: page, status: nil)
            let newItems = response.items.filter { incoming in
                !loadedRecords.contains(where: { $0.id == incoming.id })
            }
            loadedRecords.append(contentsOf: newItems)
            hasMore = response.hasMore
            page += 1
        } while hasMore

        return loadedRecords
    }

    private func sortComparator(lhs: VideoRecord, rhs: VideoRecord) -> Bool {
        switch selectedSort {
        case .newestFirst:
            return recordDate(lhs) > recordDate(rhs)
        case .oldestFirst:
            return recordDate(lhs) < recordDate(rhs)
        }
    }

    private func recordDate(_ video: VideoRecord) -> Date {
        parseDate(video.processedAt) ?? parseDate(video.createdAt) ?? .distantPast
    }

    private func parseDate(_ value: String?) -> Date? {
        guard let value, !value.isEmpty else {
            return nil
        }

        let formatterWithFraction = ISO8601DateFormatter()
        formatterWithFraction.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = formatterWithFraction.date(from: value) {
            return date
        }

        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        return formatter.date(from: value)
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
                Text(video.author.isEmpty ? "未知作者" : video.author)
                    .font(.caption)

                Text("•")

                Image(systemName: "play.circle.fill")
                    .font(.caption)
                Text(video.normalizedVideoType)
                    .font(.caption)
            }
            .foregroundColor(.gray)

            Text(video.summary.isEmpty ? "暂无总结" : video.summary)
                .font(.subheadline)
                .foregroundColor(Color(hex: "646A73"))
                .lineLimit(2)

            HStack {
                Text(displayDate(video.processedAt ?? video.createdAt))
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

    private func displayDate(_ value: String) -> String {
        guard !value.isEmpty else {
            return "--"
        }

        return String(value.prefix(10))
    }
}

struct EmptyStateView: View {
    let title: String
    let subtitle: String

    init(title: String = "暂无记录", subtitle: String = "") {
        self.title = title
        self.subtitle = subtitle
    }

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 50))
                .foregroundColor(.gray.opacity(0.5))
            Text(title)
                .font(.headline)
                .foregroundColor(.gray)
            if !subtitle.isEmpty {
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(.gray.opacity(0.8))
                    .multilineTextAlignment(.center)
            }
        }
        .padding(.horizontal, 32)
    }
}

struct InlineErrorView: View {
    let message: String

    var body: some View {
        Text(message)
            .font(.caption)
            .foregroundColor(.red)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(12)
            .background(Color.red.opacity(0.08))
            .cornerRadius(10)
    }
}

struct FilterChip: View {
    let title: String
    let systemImage: String

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: systemImage)
            Text(title)
                .lineLimit(1)
        }
        .font(.caption)
        .foregroundColor(Color(hex: "1F2329"))
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color.white)
        .clipShape(Capsule())
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
    }
}
