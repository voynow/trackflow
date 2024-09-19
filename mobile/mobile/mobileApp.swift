import SwiftUI

@main
struct mobileApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView(appState: appState)
                .environmentObject(appState)
                .onAppear {
                    if let token = UserDefaults.standard.string(forKey: "jwt_token") {
                        appState.isLoggedIn = true
                        appState.jwtToken = token
                    }
                }
        }
    }
}