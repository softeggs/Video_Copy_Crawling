import SwiftUI

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

enum VideoURLExtractor {
    private static let supportedHosts = [
        "bilibili.com",
        "b23.tv",
        "xiaohongshu.com",
        "xhslink.com",
        "douyin.com",
        "iesdouyin.com",
        "v.douyin.com",
    ]

    static func extract(from text: String) -> String? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return nil
        }

        if let directURL = normalizedSupportedURL(from: trimmed) {
            return directURL
        }

        guard let detector = try? NSDataDetector(types: NSTextCheckingResult.CheckingType.link.rawValue) else {
            return nil
        }

        let range = NSRange(trimmed.startIndex..<trimmed.endIndex, in: trimmed)
        let matches = detector.matches(in: trimmed, options: [], range: range)

        for match in matches {
            guard let candidateURL = match.url?.absoluteString else {
                continue
            }

            if let normalizedURL = normalizedSupportedURL(from: candidateURL) {
                return normalizedURL
            }
        }

        return nil
    }

    private static func normalizedSupportedURL(from candidate: String) -> String? {
        let trimmed = candidate.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return nil
        }

        let withScheme: String
        if trimmed.contains("://") {
            withScheme = trimmed
        } else if trimmed.hasPrefix("www.") || looksLikeSupportedHost(trimmed) {
            withScheme = "https://\(trimmed)"
        } else {
            return nil
        }

        guard var components = URLComponents(string: withScheme) else {
            return nil
        }

        guard let host = components.host?.lowercased(), isSupportedHost(host) else {
            return nil
        }

        components.fragment = nil
        return components.url?.absoluteString
    }

    private static func looksLikeSupportedHost(_ candidate: String) -> Bool {
        let lowered = candidate.lowercased()
        return supportedHosts.contains { lowered.hasPrefix($0) || lowered.hasPrefix("www.\($0)") }
    }

    private static func isSupportedHost(_ host: String) -> Bool {
        supportedHosts.contains { host == $0 || host.hasSuffix(".\($0)") }
    }
}
