import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authManager: AuthManager
    
    var body: some View {
        NavigationView {
            List {
                // User Info Section
                Section {
                    HStack(spacing: 16) {
                        Image(systemName: "person.circle.fill")
                            .resizable()
                            .frame(width: 60, height: 60)
                            .foregroundColor(Color(hex: "5E5CE6"))
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(authManager.currentUser?.displayName ?? "User")
                                .font(.headline)
                            Text(authManager.currentUser?.username ?? "username")
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                    }
                    .padding(.vertical, 8)
                }
                
                // Statistics Section
                Section(header: Text("Statistics")) {
                    HStack {
                        Spacer()
                        VStack {
                            Text("156")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("Total")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        Spacer()
                        try! Divider()
                        Spacer()
                        
                        VStack {
                            Text("12")
                                .font(.title2)
                                .fontWeight(.bold)
                            Text("Today")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        
                        Spacer()
                        try! Divider()
                        Spacer()
                        
                        VStack {
                            Text("3")
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(Color(hex: "FAAD14"))
                            Text("Pending")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                        Spacer()
                    }
                    .padding(.vertical, 8)
                }
                
                // Shortcut Section
                Section(header: Text("Efficient Tools")) {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Image(systemName: "bolt.fill")
                                .foregroundColor(.yellow)
                            Text("iOS Shortcut (Recommended)")
                                .font(.headline)
                        }
                        
                        Text("Add to Back Tap for instant saving from any app.")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                        
                        Button(action: {
                            if let url = URL(string: "https://www.icloud.com/shortcuts/c8d471ecbc54424388ec070917e00885") {
                                UIApplication.shared.open(url)
                            }
                        }) {
                            HStack {
                                Image(systemName: "square.and.arrow.down")
                                Text("Install Shortcut")
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
                            Text("View Setup Tutorial")
                                .font(.caption)
                                .foregroundColor(Color(hex: "5E5CE6"))
                        }
                    }
                    .padding(.vertical, 8)
                }
                
                // Settings Section
                Section(header: Text("Settings")) {
                    NavigationLink(destination: Text("Notifications Settings")) {
                        Label("Notifications", systemImage: "bell")
                    }
                    NavigationLink(destination: Text("Cache Management")) {
                        Label("Cache", systemImage: "cylinder.split.1x2")
                    }
                    NavigationLink(destination: Text("About Us")) {
                        Label("About", systemImage: "info.circle")
                    }
                }
                
                // Logout Section
                Section {
                    Button(action: {
                        authManager.logout()
                    }) {
                        Text("Logout")
                            .foregroundColor(.red)
                    }
                }
            }
            .listStyle(InsetGroupedListStyle())
            .navigationTitle("Me")
        }
    }
}

struct ShortcutTutorialView: View {
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                TutorialStep(
                    icon: "square.and.arrow.down",
                    title: "1. Install Shortcut",
                    description: "Tap the 'Install Shortcut' button and follow the system prompts to add it to your library."
                )
                
                TutorialStep(
                    icon: "gear",
                    title: "2. Configure Back Tap",
                    description: "Go to Settings > Accessibility > Touch > Back Tap."
                )
                
                TutorialStep(
                    icon: "hand.tap",
                    title: "3. Choose Action",
                    description: "Select 'Double Tap' or 'Triple Tap' and scroll down to choose the 'Video Intel' shortcut."
                )
                
                TutorialStep(
                    icon: "play.fill",
                    title: "4. Start Using",
                    description: "In apps like TikTok or Douyin, copy the video link, then tap the back of your phone to save instantly."
                )
                
                Spacer()
            }
            .padding()
        }
        .navigationTitle("Tutorial")
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
