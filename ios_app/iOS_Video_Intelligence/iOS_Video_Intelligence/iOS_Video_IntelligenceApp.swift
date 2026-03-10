//
//  iOS_Video_IntelligenceApp.swift
//  iOS_Video_Intelligence
//
//  Created by 双脚拉斯 on 2026/2/13.
//

import SwiftUI

@main
struct iOS_Video_IntelligenceApp: App {
    @StateObject private var authManager = AuthManager.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
        }
    }
}
