import SwiftUI

struct ContentView: View {
  @EnvironmentObject var appState: AppState
  @StateObject private var authManager: AuthManager

  init(appState: AppState) {
    _authManager = StateObject(wrappedValue: AuthManager(appState: appState))
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
      case .generatingPlan:
        WaitingForGenerationView(
          onComplete: {
            appState.showProfile = false
            appState.selectedTab = 1
            appState.status = .loggedIn
          },
          isAppleAuth: appState.authStrategy == .apple
        )
      }
    }
  }

  private func handleGenerationComplete() {
    appState.showProfile = false
    appState.selectedTab = 1

    guard let token = appState.jwtToken else {
      print("No token found")
      return
    }

    APIManager.shared.refreshUser(token: token) { result in
      DispatchQueue.main.async {
        switch result {
        case .success:
          appState.status = .loggedIn
        case .failure(let error):
          print("Failed to generate plan: \(error.localizedDescription)")
        }
      }
    }
  }
}

struct AppleAuthView: View {
  @ObservedObject var appState: AppState

  var body: some View {
    Color.clear
      .onAppear {
        appState.showProfile = false
        appState.selectedTab = 1
        appState.status = .loggedIn
      }
  }
}

struct ContentView_Previews: PreviewProvider {
  @StateObject private var appState = AppState()

  static var previews: some View {
    ContentView(appState: AppState()).environmentObject(AppState())
  }
}
