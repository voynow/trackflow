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

    // List of features
    let features: [Feature] = [
        Feature(icon: "🎯", title: "Personalized Plans", description: "AI powered hyper-personalized training recommendations tailored to your preferences."),
        Feature(icon: "📊", title: "Strava Integration", description: "Go for a run, upload it to Strava, and TrackFlow will update your progress accordingly."),
        Feature(icon: "🏆", title: "Goal Oriented", description: "Our weekly plans are designed to help you achieve your goals, whether you want to run a marathon or recover from an injury.")
    ]

    var body: some View {
        VStack {
            Text("🏃‍♂️🎯")
            Spacer()
            HStack(spacing: 0) {
                Text("Track")
                    .font(.system(size: 50))
                    .fontWeight(.bold)
                    .foregroundColor(ColorTheme.t0)
                
                Text("Flow")
                    .font(.system(size: 50))
                    .fontWeight(.bold)
                    .foregroundColor(ColorTheme.primary)
            }

            
            Text("Your AI Running Companion")
                .font(.title3)
                .foregroundColor(ColorTheme.t1)
                .padding(.bottom, 40)
            FeaturesListView(features: features)
                .padding(.horizontal)
            Spacer(minLength: 40)
            Button(action: {
                authManager.authenticateWithStrava()
            }) {
                HStack {
                    Text("Sign in with Stava")
                    .fontWeight(.bold)
                    Image("stravaIcon")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(height: 25)
                }
                .padding()
                .frame(maxWidth: 0.65 * UIScreen.main.bounds.width)
                .background(ColorTheme.primary)
                .foregroundColor(ColorTheme.inverseText)
                .cornerRadius(12)
                .font(.headline)
            }
            .padding(.horizontal)
            .onOpenURL { url in
                authManager.handleURL(url)
            }
            .alert(isPresented: $authManager.showAlert) {
                Alert(title: Text("Strava App Not Installed"), message: Text("Please install the Strava app to continue."), dismissButton: .default(Text("OK")))
            }

            Spacer()
        }
        .padding()
        .background(ColorTheme.bg0.edgesIgnoringSafeArea(.all))
    }
}

// Features list view
struct FeaturesListView: View {
    let features: [Feature]

    var body: some View {

            ForEach(features) { feature in
                HStack(alignment: .top, spacing: 16) {
                    Text(feature.icon)
                        .font(.largeTitle)
                        .padding(8)
                        .background(ColorTheme.bg2)
                        .cornerRadius(8)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(feature.title)
                            .font(.headline)
                            .foregroundColor(ColorTheme.t0)
                        
                        Text(feature.description)
                            .font(.subheadline)
                            .foregroundColor(ColorTheme.t1)
                    }
                }
                .padding()
                .background(ColorTheme.bg1)
                .cornerRadius(12)
        }
    }
}
