import SwiftUI

struct ProfileView: View {
  @Binding var isPresented: Bool
  @Binding var showProfile: Bool
  @State private var profileData: ProfileData?
  @EnvironmentObject var appState: AppState
  @State private var isSaving: Bool = false
  @State private var isLoading: Bool = true
  @State private var showTrainingPlanPrompt: Bool = false

  var body: some View {
    ZStack {
      ColorTheme.black.edgesIgnoringSafeArea(.all)

      if isLoading {
        ProfileSkeletonView()
      } else {
        VStack(spacing: 24) {
          profileHeader
          if let profileData = profileData {
            ScrollView {
              VStack(spacing: 24) {
                ProfileInfoCard(profileData: profileData)
                PreferencesContainer(preferences: preferencesBinding)
                SignOutButton(action: handleSignOut)
              }
              .padding()
            }
          } else {
            Text("Failed to load profile")
              .foregroundColor(ColorTheme.lightGrey)
          }
        }
        .overlay(
          Group {
            if showTrainingPlanPrompt {
              TrainingPlanPrompt(
                isPresented: $showTrainingPlanPrompt,
                raceDistance: preferencesBinding.wrappedValue.raceDistance ?? "",
                onGenerate: {
                  appState.status = .generatingPlan
                }
              )
              .animation(.easeInOut, value: showTrainingPlanPrompt)
            }
          }
        )
      }
    }
    .onAppear {
      fetchProfileData()
      NotificationCenter.default.addObserver(
        forName: .didSetupRace,
        object: nil,
        queue: .main
      ) { _ in
        showTrainingPlanPrompt = true
      }
    }
  }

  private var profileHeader: some View {
    HStack {
      Text("Profile")
        .font(.system(size: 28, weight: .black))
        .foregroundColor(ColorTheme.white)
      Spacer()
      Button(action: { showProfile = false }) {
        Image(systemName: "xmark")
          .foregroundColor(ColorTheme.lightGrey)
          .font(.system(size: 20, weight: .semibold))
      }
    }
    .padding(.horizontal)
    .padding(.top, 4)
  }

  private func handleSignOut() {
    appState.status = .loggedOut
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
    isPresented = false
  }

  private var preferencesBinding: Binding<Preferences> {
    Binding(
      get: {
        if let preferencesString = profileData?.preferences {
          if let jsonData = preferencesString.data(using: .utf8) {
            do {
              let decoder = JSONDecoder()
              decoder.dateDecodingStrategy = .iso8601
              let prefs = try decoder.decode(Preferences.self, from: jsonData)
              return prefs
            } catch {
              assertionFailure("Failed to decode preferences: \(error)")
              return Preferences()
            }
          }
        }
        return Preferences()
      },
      set: { newValue in
        do {
          let encoder = JSONEncoder()
          encoder.dateEncodingStrategy = .iso8601
          encoder.outputFormatting = .prettyPrinted

          let preferencesJSON = try encoder.encode(newValue)
          if let preferencesString = String(data: preferencesJSON, encoding: .utf8) {
            profileData?.preferences = preferencesString
          }
        } catch {
          assertionFailure("Failed to encode preferences: \(error)")
          if let emptyPrefs = try? JSONEncoder().encode(Preferences()),
            let emptyPrefsString = String(data: emptyPrefs, encoding: .utf8)
          {
            profileData?.preferences = emptyPrefsString
          }
        }
      }
    )
  }

  private func fetchProfileData() {
    guard let token = appState.jwtToken else {
      isLoading = false
      return
    }

    APIManager.shared.fetchProfileData(token: token) { result in
      DispatchQueue.main.async {
        self.isLoading = false
        if case .success(let profile) = result {
          self.profileData = profile
        }
      }
    }
  }
}

struct ProfileInfoCard: View {
  let profileData: ProfileData

  var body: some View {
    VStack(alignment: .leading, spacing: 16) {
      HStack(spacing: 16) {
        VStack {
          AsyncImage(url: URL(string: profileData.profile)) { phase in
            switch phase {
            case .empty:
              LoadingIcon()
            case .success(let image):
              image
                .resizable()
                .aspectRatio(contentMode: .fill)
            case .failure:
              Image(systemName: "person.fill")
                .foregroundColor(ColorTheme.midLightGrey)
            @unknown default:
              EmptyView()
            }
          }
          .frame(width: 80, height: 80)
          .clipShape(Circle())
          .overlay(Circle().stroke(ColorTheme.primary, lineWidth: 2))
        }
        Spacer()
        VStack(alignment: .leading, spacing: 4) {
          Text("\(profileData.firstname) \(profileData.lastname)")
            .font(.system(size: 24, weight: .bold))
            .foregroundColor(ColorTheme.white)
          if let email = profileData.email {
            Text(email)
              .font(.system(size: 14))
              .foregroundColor(ColorTheme.lightGrey)
          }
          Text("Member since \(formattedJoinDate)")
            .font(.system(size: 14))
            .foregroundColor(ColorTheme.lightGrey)
        }
      }
    }
    .padding(.vertical, 24)
    .padding(.horizontal, 36)
    .frame(maxWidth: .infinity)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(20)
  }

  private var formattedJoinDate: String {
    "Sept '24"
  }
}

struct SignOutButton: View {
  let action: () -> Void

  var body: some View {
    Button(action: action) {
      Text("Sign Out")
        .font(.system(size: 18, weight: .semibold))
        .foregroundColor(ColorTheme.primaryDark)
        .frame(maxWidth: .infinity)
        .padding()
        .background(ColorTheme.darkDarkGrey)
        .overlay(
          RoundedRectangle(cornerRadius: 12)
            .stroke(ColorTheme.primaryDark, lineWidth: 2)
        )
    }
  }
}

struct LoadingIcon: View {
  var body: some View {
    Circle()
      .fill(ColorTheme.darkDarkGrey)
      .overlay(
        Image(systemName: "person.fill")
          .foregroundColor(ColorTheme.midLightGrey)
      )
      .frame(width: 50, height: 50)
  }
}

extension Notification.Name {
  static let didSetupRace = Notification.Name("didSetupRace")
}

struct TrainingPlanPrompt: View {
  @Binding var isPresented: Bool
  let raceDistance: String
  let onGenerate: () -> Void

  var body: some View {
    ZStack {
      Color.black.opacity(0.8)
        .edgesIgnoringSafeArea(.all)

      VStack(spacing: 24) {
        VStack(spacing: 8) {
          HStack(alignment: .firstTextBaseline) {
            Image(systemName: "figure.run")
              .font(.system(size: 24))
              .foregroundColor(ColorTheme.primary)

            Text("Ready to Start Training?")
              .font(.system(size: 24, weight: .bold))
              .foregroundColor(ColorTheme.white)
          }

          Text("Let's generate your personalized \(raceDistance) training plan.")
            .font(.system(size: 16))
            .foregroundColor(ColorTheme.lightGrey)
            .multilineTextAlignment(.center)
        }

        HStack(spacing: 16) {
          Button(action: { isPresented = false }) {
            Text("Maybe Later")
              .font(.system(size: 16, weight: .medium))
              .foregroundColor(ColorTheme.lightGrey)
              .frame(maxWidth: .infinity)
              .padding(.vertical, 12)
              .background(ColorTheme.darkDarkGrey)
              .cornerRadius(8)
          }

          Button(action: {
            onGenerate()
            isPresented = false
          }) {
            HStack {
              Text("Generate Plan")
              Image(systemName: "chevron.right")
            }
            .font(.system(size: 16, weight: .semibold))
            .foregroundColor(ColorTheme.black)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(ColorTheme.primary)
            .cornerRadius(8)
          }
        }
      }
      .padding(24)
      .background(ColorTheme.darkGrey)
      .cornerRadius(16)
      .padding(.horizontal, 40)
    }
    .transition(.opacity)
  }
}
