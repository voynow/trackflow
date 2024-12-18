import SwiftUI

struct OnboardingView: View {
  @EnvironmentObject var appState: AppState
  @State private var errorMessage: String?
  @State private var email: String = ""
  @State private var hasSubmittedEmail = false
  @State private var isOnboardingComplete = false

  var body: some View {
    ZStack {
      ColorTheme.black.edgesIgnoringSafeArea(.all)
      
      if !hasSubmittedEmail {
        OnboardingEmailView(email: $email) { submittedEmail in
          hasSubmittedEmail = true
          UserDefaults.standard.set(submittedEmail, forKey: "user_email")
          guard let token = appState.jwtToken else {
            errorMessage = "No token found"
            return
          }
          APIManager.shared.updateEmail(token: token, email: submittedEmail) { result in
            DispatchQueue.main.async {
              switch result {
              case .success:
                if isOnboardingComplete {
                  appState.status = .loggedIn
                }
              case .failure(let error):
                print("Failed to update email: \(error)")
                errorMessage = "Failed to update email: \(error)"
              }
            }
          }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
          ColorTheme.black
            .opacity(0.95)
            .edgesIgnoringSafeArea(.all)
        )
        .zIndex(1)
      } else {
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
    }
    .onAppear {
      startOnboarding()
    }
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
          isOnboardingComplete = true
          if hasSubmittedEmail {
            appState.status = .loggedIn
          }
        case .failure(let error):
          errorMessage = "Failed to complete setup: \(error.localizedDescription)"
        }
      }
    }
  }
}
