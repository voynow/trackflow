import SwiftUI

struct StravaConnectOverlay: View {
  var body: some View {
    VStack(spacing: 8) {
      Text("Connect with Strava")
        .font(.title3)
        .foregroundColor(ColorTheme.lightGrey)

      Text("To see your training data, please sign in with Strava")
        .font(.subheadline)
        .foregroundColor(ColorTheme.midLightGrey)
        .multilineTextAlignment(.center)
    }
    .padding()
    .background(ColorTheme.darkDarkGrey.opacity(0.9))
    .cornerRadius(12)
  }
}

#Preview {
  ZStack {
    Color.black
    DashboardSkeletonView()
      .overlay(StravaConnectOverlay())
  }
}
