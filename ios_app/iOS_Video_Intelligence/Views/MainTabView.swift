import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            SubmitView()
                .tabItem {
                    Image(systemName: "plus.circle.fill")
                    Text("Submit")
                }
            
            HistoryView()
                .tabItem {
                    Image(systemName: "doc.text.fill")
                    Text("Records")
                }
            
            ProfileView()
                .tabItem {
                    Image(systemName: "person.circle.fill")
                    Text("Me")
                }
        }
        .accentColor(Color(hex: "5E5CE6"))
    }
}
