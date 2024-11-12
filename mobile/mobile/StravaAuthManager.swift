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
    appState.status = .loading

    Task {
      do {
        guard let url = URL(string: "\(APIManager.shared.apiURL)/authenticate/") else {
          throw NSError(
            domain: "AuthError", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["code": code]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await APIManager.shared.session.data(for: request)

        if let httpResponse = response as? HTTPURLResponse,
          !(200..<300).contains(httpResponse.statusCode)
        {
          throw NSError(
            domain: "AuthError",
            code: httpResponse.statusCode,
            userInfo: [NSLocalizedDescriptionKey: "Authentication failed"]
          )
        }

        let authResponse = try JSONDecoder().decode(SignupResponse.self, from: data)

        if authResponse.success {
          UserDefaults.standard.set(authResponse.jwt_token, forKey: "jwt_token")
          DispatchQueue.main.async {
            self.appState.jwtToken = authResponse.jwt_token
            if let isNewUser = authResponse.is_new_user, isNewUser {
              self.appState.status = .newUser
            } else {
              self.appState.status = .loggedIn
            }
          }
        } else {
          throw NSError(
            domain: "AuthError",
            code: 0,
            userInfo: [NSLocalizedDescriptionKey: "Authentication failed"]
          )
        }
      } catch {
        print("Error during authentication: \(error.localizedDescription)")
        DispatchQueue.main.async {
          self.appState.status = .loggedOut
        }
      }
    }
  }

}
