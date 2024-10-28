import SwiftUI

class AppState: ObservableObject {
  @Published var status: AppStateStatus = .loggedOut
  @Published var jwtToken: String? = nil
}
