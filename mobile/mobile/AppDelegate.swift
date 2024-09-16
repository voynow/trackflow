import SwiftUI
import UIKit

class AppDelegate: NSObject, UIApplicationDelegate {
  func application(
    _ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]
  ) -> Bool {
    guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true),
      let code = components.queryItems?.first(where: { $0.name == "code" })?.value
    else {
      print("Invalid OAuth callback URL")
      return false
    }

    // Post a notification with the authorization code
    NotificationCenter.default.post(
      name: .stravaAuthorizationCompleted,
      object: nil,
      userInfo: ["code": code]
    )
    return true
  }
}

extension Notification.Name {
  static let stravaAuthorizationCompleted = Notification.Name("StravaAuthorizationCompleted")
}
