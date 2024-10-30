import SwiftUI
import UserNotifications

class AppState: ObservableObject {
  @Published var status: AppStateStatus = .loggedOut
  @Published var jwtToken: String? = nil
  @Published var notificationStatus: UNAuthorizationStatus = .notDetermined
  
  func checkNotificationStatus() {
    UNUserNotificationCenter.current().getNotificationSettings { settings in
      DispatchQueue.main.async {
        self.notificationStatus = settings.authorizationStatus
      }
    }
  }

  func requestNotificationPermission() {
    UNUserNotificationCenter.current().delegate = UIApplication.shared.delegate as? UNUserNotificationCenterDelegate
    
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
      DispatchQueue.main.async {
        self.checkNotificationStatus()
        if granted {
          UIApplication.shared.registerForRemoteNotifications()
        }
      }
    }
  }
}
