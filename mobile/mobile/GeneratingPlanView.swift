import SwiftUI

struct GeneratingPlanView: View {
  @EnvironmentObject var appState: AppState
  @State private var errorMessage: String?

  var body: some View {
    WaitingForGenerationView(
      stages: [
        "Analyzing your race goals",
        "Calculating optimal progression",
        "Designing your build phase",
        "Planning peak weeks",
        "Optimizing taper period",
        "Finalizing your training plan",
      ],
      title: "Generating Your Training Plan",
      subtitle: "This typically takes 20-30 seconds",
      onComplete: { startGeneratingPlan() }
    )
  }

  private func startGeneratingPlan() {
    guard let token = appState.jwtToken else {
      errorMessage = "No token found"
      return
    }

    APIManager.shared.startOnboarding(token: token) { result in
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
