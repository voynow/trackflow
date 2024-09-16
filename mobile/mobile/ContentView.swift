import SwiftUI

struct ContentView: View {
  @State private var showSignup = false
  @State private var showSignIn = false

  var body: some View {
    ScrollView {
      VStack(spacing: 40) {
        Text("🏃‍♂️🎯")
        VStack(spacing: 10) {
          Text("Track")
            .font(.system(size: 48, weight: .bold))
            + Text("Flow")
            .font(.system(size: 48, weight: .bold))
            .foregroundColor(.blue)

          Text("AI-Powered Training Plans, Tailored Just for You")
            .font(.title2)
            .foregroundColor(.secondary)
            .multilineTextAlignment(.center)
        }

        // Features list
        FeaturesListView()

        // Action buttons
        VStack(spacing: 16) {
          Button(action: {
            showSignup = true
          }) {
            Text("Get Started")
              .font(.headline)
              .foregroundColor(.white)
              .frame(maxWidth: .infinity)
              .padding()
              .background(Color.blue)
              .cornerRadius(12)
          }

          Button(action: {
            showSignIn = true
            print("Signing in")
          }) {
            Text("Sign In")
              .font(.headline)
              .foregroundColor(.blue)
              .frame(maxWidth: .infinity)
              .padding()
              .background(Color.blue.opacity(0.1))
              .cornerRadius(12)
          }
        }
        .padding(.horizontal)
      }
      .padding()
      .sheet(isPresented: $showSignup) {
        SignUpView(isPresented: $showSignup)
      }
    }
  }
}

struct FeaturesListView: View {
  let features = [
    (
      "🎯", "Personalized Plans",
      "AI powered hyper-personalized training recommendations tailored to your preferences."
    ),
    (
      "📊", "Strava Integration",
      "Go for a run, upload it to Strava, and TrackFlow will update your progress accordingly."
    ),
    (
      "🏆", "Goal Oriented",
      "Our weekly plans are designed to help you achieve your goals, whether you want to run a marathon, or recover from an injury."
    ),
  ]

  var body: some View {
    VStack(alignment: .leading, spacing: 20) {
      ForEach(features, id: \.0) { feature in
        HStack(alignment: .top, spacing: 12) {
          Text(feature.0)
            .font(.system(size: 36))
            .frame(width: 50, alignment: .center)
          VStack(alignment: .leading, spacing: 4) {
            Text(feature.1)
              .font(.headline)
            Text(feature.2)
              .font(.subheadline)
              .foregroundColor(.gray)
          }
        }
      }
    }
    .padding(.horizontal, 16)
    .padding(.vertical, 8)
  }
}

struct SignUpView: View {
  @Binding var isPresented: Bool
  @State private var email: String = ""
  @State private var preferences: String = ""

  var body: some View {
    NavigationView {
      VStack(spacing: 20) {
        Text("Sign Up")
          .font(.largeTitle)
          .fontWeight(.bold)
          .padding(.top, 40)

        TextField("Email", text: $email)
          .textFieldStyle(RoundedBorderTextFieldStyle())
          .padding(.horizontal)

        TextField("Preferences (e.g., Training for 2nd marathon)", text: $preferences)
          .textFieldStyle(RoundedBorderTextFieldStyle())
          .padding(.horizontal)

        Button(action: {
          print("Signing up with email: \(email), preferences: \(preferences)")
        }) {
          Text("Sign Up")
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(12)
            .padding(.horizontal)
        }

        Spacer()
      }
      .navigationBarItems(trailing: Button("Cancel") { isPresented = false })
    }
  }
}

struct ContentView_Previews: PreviewProvider {
  static var previews: some View {
    ContentView()
  }
}
