import SwiftUI
import UIKit

class StravaAuthManager: ObservableObject {
  private let clientID = "95101"
  private let redirectURI = "trackflow://www.trackflow.xyz"
  private let scope = "read_all,profile:read_all,activity:read_all"

  @Published var showAlert = false
  private var appState: AppState

  init(appState: AppState) {
    self.appState = appState
  }

  func authenticateWithStrava() {
    let appOAuthUrlStravaScheme = URL(
      string:
        "strava://oauth/mobile/authorize?client_id=\(clientID)&redirect_uri=\(redirectURI.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")&response_type=code&approval_prompt=auto&scope=\(scope)"
    )!

    if UIApplication.shared.canOpenURL(appOAuthUrlStravaScheme) {
      UIApplication.shared.open(appOAuthUrlStravaScheme, options: [:])
    } else {
      showAlert = true
    }
  }

  func handleURL(_ url: URL) {
    if url.scheme == "trackflow" && url.host == "www.trackflow.xyz" {
      if let queryItems = URLComponents(url: url, resolvingAgainstBaseURL: false)?.queryItems,
        let code = queryItems.first(where: { $0.name == "code" })?.value
      {
        handleAuthorizationCode(code)
      }
    }
  }

  private func handleAuthorizationCode(_ code: String) {
    appState.isLoading = true

    Task {
      defer {
        DispatchQueue.main.async {
          self.appState.isLoading = false
        }
      }

      do {
        let url = URL(string: "https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["code": code]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(SignupResponse.self, from: data)

        if response.success {
          UserDefaults.standard.set(response.jwt_token, forKey: "jwt_token")
          DispatchQueue.main.async {
            self.appState.isLoggedIn = true
            self.appState.jwtToken = response.jwt_token
          }
        } else {
          throw NSError(
            domain: "AuthError", code: 0,
            userInfo: [NSLocalizedDescriptionKey: "Verification failed"]
          )
        }
      } catch {
        print("Error during verification: \(error.localizedDescription)")
      }
    }
  }

}

