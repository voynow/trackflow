import SwiftUI

struct LandingPageView: View {
  @ObservedObject var authManager: StravaAuthManager

  var body: some View {
    VStack(spacing: 0) {
      OnboardingCarousel(showCloseButton: false)

      signInButton
        .padding(.horizontal, 24)
        .padding(.bottom, 32)
    }
    .background(ColorTheme.black)
    .onOpenURL { url in
      authManager.handleURL(url)
    }
    .alert(isPresented: $authManager.showAlert) {
      Alert(
        title: Text("Strava App Not Installed"),
        message: Text("Please install the Strava app to continue."),
        dismissButton: .default(Text("OK"))
      )
    }
  }

  private var signInButton: some View {
    Button(action: {
      authManager.authenticateWithStrava()
    }) {
      HStack {
        Text("Sign in with Strava")
          .fontWeight(.semibold)
        Image("stravaIcon")
          .resizable()
          .aspectRatio(contentMode: .fit)
          .frame(height: 25)
      }
      .padding()
      .frame(maxWidth: .infinity)
      .background(ColorTheme.primary)
      .foregroundColor(ColorTheme.white)
      .cornerRadius(12)
      .shadow(radius: 5)
    }
  }
}
