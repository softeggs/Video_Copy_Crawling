import SwiftUI

struct DetailView: View {
    let video: VideoRecord
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // Header Information
                VStack(alignment: .leading, spacing: 12) {
                    Text(video.title)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(Color(hex: "1F2329"))
                    
                    HStack {
                        Label(video.author, systemImage: "person.fill")
                        Spacer()
                        Label(video.videoType, systemImage: "play.circle.fill")
                        Spacer()
                        Text(video.createdAt.prefix(10))
                            .foregroundColor(.gray)
                    }
                    .font(.subheadline)
                    .foregroundColor(Color(hex: "646A73"))
                }
                .padding()
                .background(Color.white)
                .cornerRadius(12)
                .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
                
                // Summary Card
                VStack(alignment: .leading, spacing: 12) {
                    Label("One Sentence Summary", systemImage: "star.fill")
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
                
                // Core Points
                if !video.corePoints.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("Core Points", systemImage: "list.bullet")
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
                
                // Golden Sentences
                if !video.goldenSentences.isEmpty {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("Golden Sentences", systemImage: "quote.opening")
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
                
                // Content
                if !video.correctedText.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Label("Detailed Content", systemImage: "text.aligncenter")
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
                    // Share action
                    let text = """
                    \(video.title)
                    - \(video.author)
                    
                    Summary: \(video.summary)
                    
                    link: \(video.url)
                    """
                    let av = UIActivityViewController(activityItems: [text], applicationActivities: nil)
                    UIApplication.shared.windows.first?.rootViewController?.present(av, animated: true, completion: nil)
                }) {
                    Image(systemName: "square.and.arrow.up")
                }
            }
        }
    }
}
