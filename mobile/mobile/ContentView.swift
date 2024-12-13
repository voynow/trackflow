import SwiftUI

struct ContentView: View {
  @EnvironmentObject var appState: AppState
  @StateObject private var authManager: StravaAuthManager

  init(appState: AppState) {
    _authManager = StateObject(wrappedValue: StravaAuthManager(appState: appState))
  }

  var body: some View {
    ZStack {
      switch appState.status {
      case .newUser:
        OnboardingView()
      case .loggedIn:
        ZStack {
          DashboardView()
          
          if appState.showProfile {
            ProfileView(
              isPresented: $appState.showProfile,
              showProfile: $appState.showProfile
            )
            .transition(.move(edge: .trailing))
            .zIndex(2)
          }
        }
      case .loggedOut:
        LandingPageView(authManager: authManager)
      case .loading:
        LoadingView()
      }
    }
  }
}

struct ContentView_Previews: PreviewProvider {
  @StateObject private var appState = AppState()

  static var previews: some View {
    ContentView(appState: AppState()).environmentObject(AppState())
  }
}
