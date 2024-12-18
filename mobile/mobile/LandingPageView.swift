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
  @State private var currentPage: Int = 0

  let pages: [(image: String, title: String, subtitle: String)] = [
    ("AppDashboard", "Train Smarter", "AI-powered plans that adapt to your progress"),
    ("AppDashboardAlt", "Connect with Strava", "Seamless integration with your activities"),
    ("AppProfile", "Achieve Your Goals", "From 5K to marathon, we've got you covered"),
  ]

  var body: some View {
    GeometryReader { geometry in
      VStack(spacing: 0) {
        // Image carousel at top
        TabView(selection: $currentPage) {
          ForEach(0..<pages.count, id: \.self) { index in
            Image(pages[index].image)
              .resizable()
              .aspectRatio(contentMode: .fit)
              .frame(height: geometry.size.height * 0.65)
              .clipShape(RoundedRectangle(cornerRadius: 30))
              .padding(.horizontal, 20)
              .shadow(
                color: Color(white: 0.3, opacity: 0.3),
                radius: 15,
                x: 0,
                y: 8
              )
              .background(
                Color(white: 0.12)
                  .blur(radius: 20)
                  .offset(y: 10)
                  .clipShape(RoundedRectangle(cornerRadius: 30))
              )
              .overlay(
                LinearGradient(
                  gradient: Gradient(colors: [.clear, .black.opacity(0.3)]),
                  startPoint: .top,
                  endPoint: .bottom
                )
                .clipShape(RoundedRectangle(cornerRadius: 30))
              )
              .tag(index)
          }
        }
        .tabViewStyle(PageTabViewStyle(indexDisplayMode: .automatic))
        .frame(height: geometry.size.height * 0.75)

        Spacer()

        // Title and subtitle
        VStack(spacing: 8) {
          Text(pages[currentPage].title)
            .font(.system(size: 32, weight: .bold))
            .foregroundColor(.white)

          Text(pages[currentPage].subtitle)
            .font(.system(size: 16))
            .foregroundColor(.white.opacity(0.8))
            .multilineTextAlignment(.center)
            .padding(.horizontal)
        }
        .padding(.bottom, 40)


        signInButton
          .padding(.horizontal, 24)
          .padding(.bottom, geometry.safeAreaInsets.bottom + 24)
      }
      .ignoresSafeArea(edges: .top)
    }
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
      .background(ColorTheme.primary)
      .foregroundColor(ColorTheme.white)
      .cornerRadius(12)
      .shadow(radius: 5)
    }
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
