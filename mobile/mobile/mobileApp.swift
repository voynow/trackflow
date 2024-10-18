import SwiftUI

@main
struct mobileApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView(appState: appState)
                .environmentObject(appState)
                .onAppear {
                    checkAndRefreshToken()
                }
        }
    }

    private func checkAndRefreshToken() {
        if let token = UserDefaults.standard.string(forKey: "jwt_token") {
            APIManager.shared.refreshToken(token: token) { result in
                DispatchQueue.main.async {
                    switch result {
                    case .success(let newToken):
                        appState.isLoggedIn = true
                        appState.jwtToken = newToken
                        UserDefaults.standard.set(newToken, forKey: "jwt_token")
                    case .failure(_):
                        // Token refresh failed, user needs to log in again
                        appState.isLoggedIn = false
                        appState.jwtToken = nil
                        UserDefaults.standard.removeObject(forKey: "jwt_token")
                    }
                }
            }
        }
    }
}
