import SwiftUI

struct OnboardingView: View {
  @EnvironmentObject var appState: AppState
  @State private var errorMessage: String?

  var body: some View {
    WaitingForGenerationView(
      stages: [
        "Our AI is getting to know you",
        "Analyzing your Strava data",
        "Our AI Agent is impressed!",
        "Analyzing your workouts",
        "Considering volume and intensity",
        "Generating candidate training plans",
        "Selecting the best plan for you",
        "Fine-tuning recommendations",
      ],
      title: "TrackFlow",
      subtitle: "Account setup typically takes 30 seconds. Thank you for your patience!",
      onComplete: { startOnboarding() }
    )
  }

  private func startOnboarding() {
    guard let token = UserDefaults.standard.string(forKey: "jwt_token") else {
      errorMessage = "No token found. Please log in again."
      return
    }

    APIManager.shared.refresh(token: token) { result in
      DispatchQueue.main.async {
        switch result {
        case .success:
          appState.status = .loggedIn
        case .failure(let error):
          if let decodingError = error as? DecodingError {
            errorMessage = "Failed to decode response: \(decodingError)"
          } else if let urlError = error as? URLError {
            errorMessage = "Network error: \(urlError.localizedDescription)"
          } else {
            errorMessage = "Onboarding failed: \(error.localizedDescription)"
          }
          print("Detailed error: \(error)")
        }
      }
    }
  }
}
