import SwiftUI

// Feature model
struct Feature: Identifiable {
  let id = UUID()
  let icon: String
  let title: String
  let description: String
}

struct LandingPageView: View {
  @ObservedObject var authManager: StravaAuthManager

  let features: [Feature] = [
    Feature(
      icon: "figure.run", title: "Personalized Plans",
      description:
        "AI powered hyper-personalized training recommendations tailored to your preferences."),
    Feature(
      icon: "chart.bar.fill", title: "Strava Integration",
      description:
        "Go for a run, upload it to Strava, and TrackFlow will update your progress accordingly."),
    Feature(
      icon: "trophy.fill", title: "Goal Oriented",
      description:
        "Our weekly plans are designed to help you achieve your goals, whether you want to run a marathon or recover from an injury."
    ),
  ]

  var body: some View {
    GeometryReader { geometry in
      ScrollView {
        VStack(spacing: 24) {
          Text("🏃‍♂️🎯")
          Spacer()
          HStack(spacing: 0) {
            Text("Track")
              .font(.system(size: 50, weight: .black))
              .foregroundColor(ColorTheme.primaryLight)
            Text("Flow")
              .font(.system(size: 50, weight: .black))
              .foregroundColor(ColorTheme.primary)
          }

          Text("Step into the Next Generation of Training")
            .font(.title2)
            .foregroundColor(ColorTheme.lightGrey)
            .multilineTextAlignment(.center)
            .padding(.horizontal)

          signInButton

          FeaturesListView(features: features)
            .padding(.horizontal)
        }
        .padding()
        .frame(maxWidth: min(geometry.size.width, 600))
        .frame(maxWidth: .infinity)
      }
      .background(ColorTheme.black.edgesIgnoringSafeArea(.all))
      .onOpenURL { url in
        authManager.handleURL(url)
      }
      .alert(isPresented: $authManager.showAlert) {
        Alert(
          title: Text("Strava App Not Installed"),
          message: Text("Please install the Strava app to continue."),
          dismissButton: .default(Text("OK")))
      }
    }
  }

  var signInButton: some View {
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
      .background(
        LinearGradient(
          gradient: Gradient(colors: [ColorTheme.primary, ColorTheme.primaryLight]),
          startPoint: .leading, endPoint: .trailing)
      )
      .foregroundColor(ColorTheme.white)
      .cornerRadius(12)
      .shadow(radius: 5)
    }
    .padding(.horizontal)
  }
}

// Features list view
struct FeaturesListView: View {
  let features: [Feature]

  var body: some View {
    VStack(spacing: 16) {
      ForEach(features) { feature in
        HStack(alignment: .top, spacing: 16) {
          Image(systemName: feature.icon)
            .font(.system(size: 24))
            .foregroundColor(ColorTheme.primary)
            .frame(width: 40, height: 40)
            .background(ColorTheme.darkGrey)
            .cornerRadius(10)

          VStack(alignment: .leading, spacing: 4) {
            Text(feature.title)
              .font(.headline)
              .foregroundColor(ColorTheme.white)

            Text(feature.description)
              .font(.subheadline)
              .foregroundColor(ColorTheme.lightGrey)
          }
        }
        .padding()
        .background(ColorTheme.darkDarkGrey)
        .cornerRadius(12)
      }
    }
  }
}
