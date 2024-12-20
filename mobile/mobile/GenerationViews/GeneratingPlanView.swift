import SwiftUI

struct GeneratingPlanView: View {
  @EnvironmentObject var appState: AppState
  @State private var errorMessage: String?

  var body: some View {
    WaitingForGenerationView(onComplete: {
      appState.showProfile = false
      startGeneratingPlan()
      appState.selectedTab = 1
    })
  }

  private func startGeneratingPlan() {
    guard let token = appState.jwtToken else {
      errorMessage = "No token found"
      return
    }

    APIManager.shared.refreshUser(token: token) { result in
      DispatchQueue.main.async {
        switch result {
        case .success:
          appState.status = .loggedIn
        case .failure(let error):
          errorMessage = "Failed to generate plan: \(error.localizedDescription)"
        }
      }
    }
  }
}
