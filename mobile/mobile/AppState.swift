import SwiftUI

class AppState: ObservableObject {
  @Published var status: AppStateStatus = .loggedOut {
    didSet {
      print("AppState status changed to: \(status)")
    }
  }

  @Published var jwtToken: String? = nil {
    didSet {
      print("AppState jwtToken changed to: \(jwtToken ?? "nil")")
    }
  }
}
