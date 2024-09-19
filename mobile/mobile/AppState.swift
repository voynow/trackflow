import SwiftUI

class AppState: ObservableObject {
    @Published var isLoggedIn: Bool = false
    @Published var jwtToken: String? = nil
    @Published var isLoading: Bool = false
}
