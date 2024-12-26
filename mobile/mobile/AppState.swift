import SwiftUI
import UserNotifications

class AppState: ObservableObject {
  @Published var status: AppStateStatus = .loggedOut
  @Published var jwtToken: String? = nil
  @Published var notificationStatus: UNAuthorizationStatus = .notDetermined
  @Published var showProfile: Bool = false
  @Published var selectedTab: Int = 0

  init() {
    NotificationCenter.default.addObserver(
      forName: .didSetupRace,
      object: nil,
      queue: .main
    ) { [weak self] _ in
      print("DEBUG: didSetupRace notification received in AppState")
      self?.status = .generatingPlan
      self?.showProfile = false
      self?.selectedTab = 1
    }
  }

  func checkNotificationStatus() {
    UNUserNotificationCenter.current().getNotificationSettings { settings in
      DispatchQueue.main.async {
        self.notificationStatus = settings.authorizationStatus
      }
    }
  }

  func requestNotificationPermission() {
    UNUserNotificationCenter.current().delegate =
      UIApplication.shared.delegate as? UNUserNotificationCenterDelegate

    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) {
      granted, error in
      DispatchQueue.main.async {
        self.checkNotificationStatus()
        if granted {
          UIApplication.shared.registerForRemoteNotifications()
        }
      }
    }
  }
}
