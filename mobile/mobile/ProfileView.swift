import SwiftUI

struct ProfileView: View {
  @Binding var isPresented: Bool
  @State private var profileData: ProfileData?
  @EnvironmentObject var appState: AppState
  @Binding var showProfile: Bool
  @State private var isSaving: Bool = false
  @State private var isLoading: Bool = true
  @State private var lastFetchTime: Date?
  private let cacheTimeout: TimeInterval = 300

  var body: some View {
    ZStack {
      ColorTheme.black.edgesIgnoringSafeArea(.all)

      VStack(spacing: 24) {
        profileHeader

        if isLoading {
          ProfileSkeletonView()
        } else if let profileData = profileData {
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
    }
    .onAppear(perform: fetchProfileData)
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
                    ProfileCache.updatePreferences(preferencesString)
                }
            } catch {
                assertionFailure("Failed to encode preferences: \(error)")
                if let emptyPrefs = try? JSONEncoder().encode(Preferences()),
                   let emptyPrefsString = String(data: emptyPrefs, encoding: .utf8) {
                    profileData?.preferences = emptyPrefsString
                    ProfileCache.updatePreferences(emptyPrefsString)
                }
            }
        }
    )
  }

  private func shouldRefetchData() -> Bool {
    guard let lastFetch = lastFetchTime else {
      return true
    }
    let timeSinceLastFetch = Date().timeIntervalSince(lastFetch)
    let shouldRefetch = timeSinceLastFetch > cacheTimeout
    return shouldRefetch
  }

  private func fetchProfileData() {
    guard let token = appState.jwtToken else {
      isLoading = false
      return
    }

    if !ProfileCache.shouldRefetch() && ProfileCache.data != nil {
      self.profileData = ProfileCache.data
      isLoading = false
      return
    }

    APIManager.shared.fetchProfileData(token: token) { result in
      DispatchQueue.main.async {
        self.isLoading = false
        if case .success(let profile) = result {
          ProfileCache.update(profile)
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
  @State private var isRotating = false

  var body: some View {
    Circle()
      .trim(from: 0, to: 0.7)
      .stroke(ColorTheme.primaryDark, lineWidth: 2)
      .frame(width: 50, height: 50)
      .rotationEffect(Angle(degrees: isRotating ? 360 : 0))
      .animation(
        Animation.linear(duration: 1).repeatForever(autoreverses: false), value: isRotating
      )
      .onAppear {
        isRotating = true
      }
  }
}

private enum ProfileCache {
  static var lastFetchTime: Date?
  static var data: ProfileData?
  static let timeout: TimeInterval = 300

  static func shouldRefetch() -> Bool {
    guard let lastFetch = lastFetchTime else { return true }
    return Date().timeIntervalSince(lastFetch) > timeout
  }

  static func update(_ profile: ProfileData) {
    data = profile
    lastFetchTime = Date()
  }

  static func updatePreferences(_ preferences: String) {
    if var cachedData = data {
      guard let _ = preferences.data(using: .utf8) else {
        print("Debug: ProfileCache - Invalid preferences string")
        return
      }
      
      cachedData.preferences = preferences
      data = cachedData
      
      print("Debug: ProfileCache - Successfully updated preferences")
    } else {
      print("Debug: ProfileCache - No cached data to update")
    }
  }

  static func clear() {
    data = nil
    lastFetchTime = nil
  }
}
