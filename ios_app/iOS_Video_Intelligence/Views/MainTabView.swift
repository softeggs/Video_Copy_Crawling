import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            SubmitView()
                .tabItem {
                    Image(systemName: "plus.circle.fill")
                    Text("提交")
                }

            HistoryView()
                .tabItem {
                    Image(systemName: "doc.text.fill")
                    Text("记录")
                }

            ProfileView()
                .tabItem {
                    Image(systemName: "person.circle.fill")
                    Text("我的")
                }
        }
        .accentColor(Color(hex: "5E5CE6"))
    }
}
