import SwiftUI

struct OnboardingView: View {
  @EnvironmentObject var appState: AppState
  @State private var progress: Double = 0
  @State private var currentStage: Int = 0
  @State private var errorMessage: String?
  @State private var showExtendedWaitMessage: Bool = false

  let timer = Timer.publish(every: 0.1, on: .main, in: .common).autoconnect()

  let stages: [String] = [
    "Our AI is getting to know you",
    "Analyzing your Strava data",
    "Our AI Agent is impressed!",
    "Analyzing your workouts",
    "Considering volume and intensity",
    "Generating candidate training plans",
    "Selecting the best plan for you",
    "Fine-tuning recommendations",
  ]

  var body: some View {
    GeometryReader { geometry in
      ZStack {
        ColorTheme.black.edgesIgnoringSafeArea(.all)

        VStack(spacing: 20) {
          Spacer()

          brandingView

          Text("Account setup typically takes 30 seconds. Please do not close this window.")
            .font(.system(size: 16, weight: .light))
            .foregroundColor(ColorTheme.lightGrey)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 20)

          Spacer()

          Text(stages[currentStage])
            .font(.system(size: 18, weight: .bold))
            .foregroundColor(ColorTheme.primaryLight)
            .transition(.opacity)
            .id(currentStage)
            .multilineTextAlignment(.center)

          ProgressView(value: progress)
            .progressViewStyle(LinearProgressViewStyle(tint: ColorTheme.primary))
            .frame(height: 4)

          if let errorMessage = errorMessage {
            Text(errorMessage)
              .font(.subheadline)
              .foregroundColor(.red)
              .multilineTextAlignment(.center)
          }

          if showExtendedWaitMessage {
            Text(
              "We apologize for the wait. Your account is still being set up and will be ready very soon."
            )
            .font(.system(size: 16, weight: .light))
            .foregroundColor(ColorTheme.lightGrey)
            .multilineTextAlignment(.center)
            .padding(.horizontal, 40)
            .transition(.opacity)
          }

          Spacer()
        }
        .padding(.horizontal, 40)
        .frame(width: geometry.size.width)
      }
    }
    .onAppear(perform: startOnboarding)
    .onReceive(timer) { _ in
      updateProgress()
    }
  }

  private var brandingView: some View {
    VStack(spacing: 16) {
      Text("🏃‍♂️🎯")
        .font(.system(size: 20))

      HStack(spacing: 0) {
        Text("Track")
          .font(.system(size: 40, weight: .black))
          .foregroundColor(ColorTheme.primaryLight)
        Text("Flow")
          .font(.system(size: 40, weight: .black))
          .foregroundColor(ColorTheme.primary)
      }
    }
  }

  private func startOnboarding() {
    guard let token = UserDefaults.standard.string(forKey: "jwt_token") else {
      errorMessage = "No token found. Please log in again."
      return
    }

    APIManager.shared.startOnboarding(token: token) { result in
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

  private func updateProgress() {
    if progress < 1.0 {
      progress = min(progress + 0.003, 1.0)
      let newStage = min(Int(progress * Double(stages.count)), stages.count - 1)
      if newStage != currentStage {
        withAnimation(.easeInOut(duration: 0.5)) {
          currentStage = newStage
        }
      }
      
      if progress >= 0.9 && !showExtendedWaitMessage {
        withAnimation {
          showExtendedWaitMessage = true
        }
      }
    } else if errorMessage == nil && appState.status != .loggedIn {
      // Keep progress at 1.0 and show the last stage
      currentStage = stages.count - 1
      showExtendedWaitMessage = true
    }
  }
}
