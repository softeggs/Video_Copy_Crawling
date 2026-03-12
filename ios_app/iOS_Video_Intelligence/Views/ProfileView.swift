import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        NavigationView {
            List {
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
                            Text("156")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("累计")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }

                        Spacer()
                        Divider()
                        Spacer()

                        VStack {
                            Text("12")
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
                            Text("3")
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
