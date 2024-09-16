//
//  ContentView.swift
//  mobile
//
//  Created by jamie voynow on 9/15/24.
//

import AuthenticationServices
import SwiftUI

struct ContentView: View {
  @State private var showSignup = false
  @State private var showSignIn = false
  @State private var authorizationCode: String?

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
        SignUpView(isPresented: $showSignup, authorizationCode: $authorizationCode)
      }
      .onReceive(NotificationCenter.default.publisher(for: .stravaAuthorizationCompleted)) {
        notification in
        if let code = notification.userInfo?["code"] as? String {
          authorizationCode = code
          showSignup = true
        }
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
  @Binding var authorizationCode: String?
  @State private var email: String = ""
  @State private var preferences: String = ""
  @State private var isLoading: Bool = false
  @State private var error: String?

  var body: some View {
    NavigationView {
      VStack(spacing: 20) {
        Text("Sign Up")
          .font(.largeTitle)
          .fontWeight(.bold)
          .padding(.top, 40)

        TextField("Email", text: $email)
          .textFieldStyle(RoundedBorderTextFieldStyle())
          .autocapitalization(.none)
          .keyboardType(.emailAddress)
          .padding(.horizontal)

        TextField("Preferences (e.g., Training for 2nd marathon)", text: $preferences)
          .textFieldStyle(RoundedBorderTextFieldStyle())
          .padding(.horizontal)

        Button(action: handleSignUp) {
          if isLoading {
            ProgressView()
              .progressViewStyle(CircularProgressViewStyle(tint: .white))
          } else {
            Text("Sign Up with Strava")
          }
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.blue)
        .foregroundColor(.white)
        .cornerRadius(12)
        .padding(.horizontal)

        if let error = error {
          Text(error)
            .foregroundColor(.red)
            .padding()
        }

        Spacer()
      }
      .navigationBarItems(trailing: Button("Cancel") { isPresented = false })
    }
  }

  private func handleSignUp() {
    isLoading = true
    error = nil

    if let code = authorizationCode {
      // We have an authorization code, proceed with account verification
      verifyAccount(code: code)
    } else {
      // No authorization code, initiate Strava OAuth flow
      initiateStravaAuth()
    }
  }

  private func initiateStravaAuth() {
    // Save email and preferences to UserDefaults
    UserDefaults.standard.set(email, forKey: "email")
    UserDefaults.standard.set(preferences, forKey: "preferences")

    let clientId = "95101"
    let redirectUri = "trackflow://oauth-callback"
    let scope = "read_all,profile:read_all,activity:read_all"

    guard
      let stravaUrl = URL(
        string:
          "https://www.strava.com/oauth/authorize?client_id=\(clientId)&redirect_uri=\(redirectUri)&response_type=code&approval_prompt=auto&scope=\(scope)"
      )
    else {
      error = "Invalid Strava URL"
      isLoading = false
      return
    }

    UIApplication.shared.open(stravaUrl)
  }

  private func verifyAccount(code: String) {
    // Implement account verification with your backend
    // This is where you'd make a network request to your API
    // Similar to the verifyAccount function in your web app
  }
}

struct ContentView_Previews: PreviewProvider {
  static var previews: some View {
    ContentView()
  }
}
