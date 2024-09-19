import UIKit
import os

class AppDelegate: UIResponder, UIApplicationDelegate {
  private let logger = Logger(
    subsystem: Bundle.main.bundleIdentifier ?? "com.trackflow", category: "AppDelegate")

  func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {

    logger.info(
      "Application did finish launching with options: \(String(describing: launchOptions))")
    return true
  }
}
