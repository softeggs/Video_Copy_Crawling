import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var overview = VideoOverviewResponse(total: 0, today: 0, pending: 0)
    @State private var isLoadingOverview = false
    @State private var errorMessage: String?

    private let videoRepository: VideoRepositoryProtocol = AppServices.videoRepository

    var body: some View {
        NavigationView {
            List {
                if let errorMessage {
                    Section {
                        InlineErrorView(message: errorMessage)
                    }
                }

                Section {
                    HStack(spacing: 16) {
                        Image(systemName: "person.circle.fill")
                            .resizable()
                            .frame(width: 60, height: 60)
                            .foregroundColor(Color(hex: "5E5CE6"))

                        VStack(alignment: .leading, spacing: 4) {
                            Text(authManager.currentUser?.displayName ?? "用户")
                                .font(.headline)
                            Text(authManager.currentUser?.username ?? "未登录用户")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                    }
                    .padding(.vertical, 8)
                }

                Section(header: Text("统计概览")) {
                    HStack {
                        Spacer()
                        VStack {
                            if isLoadingOverview {
                                ProgressView()
                            } else {
                                Text("\(overview.total)")
                                    .font(.title2)
                                    .fontWeight(.bold)
                            }
                            Text("累计")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }

                        Spacer()
                        Divider()
                        Spacer()

                        VStack {
                            Text("\(overview.today)")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("今日")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }

                        Spacer()
                        Divider()
                        Spacer()

                        VStack {
                            Text("\(overview.pending)")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(Color(hex: "FAAD14"))
                            Text("待处理")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        Spacer()
                    }
                    .padding(.vertical, 8)
                }

                Section(header: Text("高效工具")) {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "bolt.fill")
                                .foregroundColor(.yellow)
                            Text("iOS 快捷指令（推荐）")
                                .font(.headline)
                        }

                        Text("添加到轻点背面后，可从任意 App 快速保存视频链接。")
                            .font(.subheadline)
                            .foregroundColor(.gray)

                        Button(action: {
                            if let url = URL(string: "https://www.icloud.com/shortcuts/c8d471ecbc54424388ec070917e00885") {
                                UIApplication.shared.open(url)
                            }
                        }) {
                            HStack {
                                Image(systemName: "square.and.arrow.down")
                                Text("安装快捷指令")
                            }
                            .font(.subheadline)
                            .fontWeight(.medium)
                            .foregroundColor(.white)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(Color(hex: "5E5CE6"))
                            .cornerRadius(20)
                        }
                        .padding(.top, 4)

                        NavigationLink(destination: ShortcutTutorialView()) {
                            Text("查看设置教程")
                                .font(.caption)
                                .foregroundColor(Color(hex: "5E5CE6"))
                        }
                    }
                    .padding(.vertical, 8)

                    NavigationLink(destination: ShortcutKeysView()) {
                        HStack {
                            Image(systemName: "key.fill")
                                .foregroundColor(Color(hex: "FAAD14"))
                            VStack(alignment: .leading, spacing: 2) {
                                Text("快捷指令密钥")
                                    .font(.subheadline)
                                Text("生成和管理 API 密钥，自动化提交")
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                }

                Section(header: Text("设置")) {
                    NavigationLink(destination: Text("通知设置")) {
                        Label("通知", systemImage: "bell")
                    }
                    NavigationLink(destination: Text("缓存管理")) {
                        Label("缓存", systemImage: "cylinder.split.1x2")
                    }
                    NavigationLink(destination: Text("关于我们")) {
                        Label("关于我们", systemImage: "info.circle")
                    }
                }

                Section {
                    Button(action: {
                        authManager.logout()
                    }) {
                        Text("退出登录")
                            .foregroundColor(.red)
                    }
                }
            }
            .listStyle(InsetGroupedListStyle())
            .navigationTitle("我的")
            .task(id: authManager.token) {
                await loadOverview()
            }
        }
    }

    private func loadOverview() async {
        guard let token = authManager.token else {
            await MainActor.run {
                overview = VideoOverviewResponse(total: 0, today: 0, pending: 0)
                isLoadingOverview = false
                errorMessage = nil
            }
            return
        }

        await MainActor.run {
            isLoadingOverview = true
            errorMessage = nil
        }

        do {
            let loadedOverview = try await videoRepository.fetchOverview(token: token)
            await MainActor.run {
                overview = loadedOverview
                isLoadingOverview = false
            }
        } catch {
            await MainActor.run {
                overview = VideoOverviewResponse(total: 0, today: 0, pending: 0)
                isLoadingOverview = false
                errorMessage = error.localizedDescription
            }
        }
    }
}

struct ShortcutTutorialView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                TutorialStep(
                    icon: "square.and.arrow.down",
                    title: "1. 安装快捷指令",
                    description: "点击“安装快捷指令”，按照系统提示将它添加到快捷指令库。"
                )

                TutorialStep(
                    icon: "gear",
                    title: "2. 设置轻点背面",
                    description: "前往“设置 > 辅助功能 > 触控 > 轻点背面”。"
                )

                TutorialStep(
                    icon: "hand.tap",
                    title: "3. 选择触发动作",
                    description: "选择“双击”或“三击”，然后在快捷指令列表中选择“视频情报提取”。"
                )

                TutorialStep(
                    icon: "play.fill",
                    title: "4. 开始使用",
                    description: "在抖音等 App 中复制视频链接后，轻点手机背面即可快速保存。"
                )

                Spacer()
            }
            .padding()
        }
        .navigationTitle("设置教程")
        .background(Color(hex: "F7F8FA"))
    }
}

struct TutorialStep: View {
    let icon: String
    let title: String
    let description: String

    var body: some View {
        HStack(alignment: .top, spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 40, height: 40)
                .background(Circle().fill(Color(hex: "5E5CE6")))

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.subheadline)
                    .foregroundColor(.gray)
                    .lineSpacing(4)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

// MARK: - 快捷指令密钥管理

struct ShortcutKeysView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var keys: [ShortcutKeySummary] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var newKeyName = ""
    @State private var createdKey: CreateShortcutKeyResponse?
    @State private var showCreateSheet = false
    @State private var revokeTargetKeyId: Int?
    @State private var showRevokeConfirm = false

    private let videoRepository: VideoRepositoryProtocol = AppServices.videoRepository

    var body: some View {
        List {
            if let errorMessage {
                Section {
                    InlineErrorView(message: errorMessage)
                }
            }

            // 说明卡片
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Label("什么是快捷指令密钥？", systemImage: "info.circle")
                        .font(.headline)
                        .foregroundColor(Color(hex: "5E5CE6"))

                    Text("快捷指令密钥是一种免登录提交方式。生成后可直接通过 API 提交视频链接，无需账号密码。")
                        .font(.subheadline)
                        .foregroundColor(.gray)

                    Text("⚠️ 密钥只显示一次，请立即复制保存。服务端只保存哈希，无法找回明文。")
                        .font(.caption)
                        .foregroundColor(.orange)
                }
                .padding(.vertical, 4)
            }

            // 生成新密钥
            Section(header: Text("生成密钥")) {
                HStack {
                    TextField("密钥名称（可选）", text: $newKeyName)
                        .font(.subheadline)

                    Button {
                        showCreateSheet = true
                    } label: {
                        if isLoading {
                            ProgressView()
                        } else {
                            Text("生成")
                                .fontWeight(.medium)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Color(hex: "5E5CE6"))
                    .disabled(isLoading)
                }
            }

            // 新密钥已生成提示
            if let createdKey {
                Section(header: Text("新生成的密钥（仅显示一次）")) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("请立即复制保存！")
                            .font(.caption)
                            .foregroundColor(.orange)
                            .fontWeight(.bold)

                        Text(createdKey.key)
                            .font(.system(.body, design: .monospaced))
                            .foregroundColor(.primary)
                            .padding(10)
                            .background(Color(hex: "F0F2F5"))
                            .cornerRadius(8)
                            .textSelection(.enabled)

                        Button {
                            UIPasteboard.general.string = createdKey.key
                        } label: {
                            Label("复制密钥", systemImage: "doc.on.doc")
                                .font(.subheadline)
                        }

                        Text("密钥前缀：\(createdKey.keyPrefix)****")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text("创建时间：\(createdKey.createdAt.prefix(10))")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .padding(.vertical, 4)
                }
            }

            // 已有密钥列表
            Section(header: Text("已生成的密钥（\(keys.count) 个）")) {
                if keys.isEmpty && !isLoading {
                    Text("暂无密钥")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .padding(.vertical, 8)
                } else {
                    ForEach(keys) { key in
                        ShortcutKeyRow(
                            key: key,
                            onRevoke: {
                                revokeTargetKeyId = key.id
                                showRevokeConfirm = true
                            }
                        )
                    }
                }
            }
        }
        .listStyle(InsetGroupedListStyle())
        .navigationTitle("快捷指令密钥")
        .navigationBarTitleDisplayMode(.large)
        .confirmationDialog(
            "确认吊销密钥",
            isPresented: $showRevokeConfirm,
            titleVisibility: .visible
        ) {
            Button("确认吊销", role: .destructive) {
                if let keyId = revokeTargetKeyId {
                    revokeKey(keyId: keyId)
                }
            }
            Button("取消", role: .cancel) {}
        } message: {
            Text("吊销后该密钥立即失效，无法恢复。确定要吊销吗？")
        }
        .task(id: authManager.token) {
            await loadKeys()
        }
        .refreshable {
            await loadKeys()
        }
    }

    private func loadKeys() async {
        guard let token = authManager.token else {
            await MainActor.run {
                errorMessage = AppServiceError.missingCurrentUser.localizedDescription
                keys = []
            }
            return
        }

        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let loadedKeys = try await videoRepository.listShortcutKeys(token: token)
            await MainActor.run {
                keys = loadedKeys
                isLoading = false
            }
        } catch {
            await MainActor.run {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func createKey() async {
        guard let token = authManager.token else { return }

        await MainActor.run {
            isLoading = true
            errorMessage = nil
        }

        do {
            let name = newKeyName.trimmingCharacters(in: .whitespacesAndNewlines)
            let resp = try await videoRepository.createShortcutKey(token: token, name: name.isEmpty ? "快捷指令密钥" : name)
            await MainActor.run {
                createdKey = resp
                keys.insert(ShortcutKeySummary(
                    id: resp.id,
                    keyPrefix: resp.keyPrefix,
                    name: resp.name,
                    isActive: true,
                    createdAt: resp.createdAt,
                    lastUsedAt: nil
                ), at: 0)
                newKeyName = ""
                isLoading = false
                showCreateSheet = false
            }
        } catch {
            await MainActor.run {
                errorMessage = "生成失败：\(error.localizedDescription)"
                isLoading = false
            }
        }
    }

    private func revokeKey(keyId: Int) {
        guard let token = authManager.token else { return }

        Task {
            do {
                _ = try await videoRepository.revokeShortcutKey(token: token, keyId: keyId)
                await MainActor.run {
                    keys = keys.map { key in
                        if key.id == keyId {
                            return ShortcutKeySummary(
                                id: key.id,
                                keyPrefix: key.keyPrefix,
                                name: key.name,
                                isActive: false,
                                createdAt: key.createdAt,
                                lastUsedAt: key.lastUsedAt
                            )
                        }
                        return key
                    }
                    revokeTargetKeyId = nil
                }
            } catch {
                await MainActor.run {
                    errorMessage = "吊销失败：\(error.localizedDescription)"
                    revokeTargetKeyId = nil
                }
            }
        }
    }
}

// MARK: - ShortcutKeyRow

struct ShortcutKeyRow: View {
    let key: ShortcutKeySummary
    let onRevoke: () -> Void

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 6) {
                    Text(key.name)
                        .font(.subheadline)
                        .fontWeight(.medium)

                    if key.isActive {
                        Text("有效")
                            .font(.caption2)
                            .fontWeight(.bold)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.green.opacity(0.1))
                            .foregroundColor(.green)
                            .cornerRadius(4)
                    } else {
                        Text("已吊销")
                            .font(.caption2)
                            .fontWeight(.bold)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.gray.opacity(0.1))
                            .foregroundColor(.gray)
                            .cornerRadius(4)
                    }
                }

                Text("前缀：\(key.keyPrefix)****")
                    .font(.caption)
                    .foregroundColor(.gray)

                Text("创建：\(key.createdAt.prefix(10))")
                    .font(.caption)
                    .foregroundColor(.gray)

                if let lastUsed = key.lastUsedAt {
                    Text("最后使用：\(lastUsed.prefix(10))")
                        .font(.caption)
                        .foregroundColor(.gray)
                } else {
                    Text("从未使用")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }

            Spacer()

            if key.isActive {
                Button(role: .destructive) {
                    onRevoke()
                } label: {
                    Text("吊销")
                        .font(.caption)
                        .fontWeight(.medium)
                }
                .buttonStyle(.bordered)
                .tint(.red)
            }
        }
        .padding(.vertical, 4)
    }
}
