import SwiftUI

struct ProfileView: View {
  @Binding var isPresented: Bool
  @Binding var profileData: ProfileData
  @EnvironmentObject var appState: AppState
  @Binding var showProfile: Bool
  @State private var isSaving: Bool = false

  var body: some View {
    VStack(spacing: 0) {
      DashboardNavbar(onLogout: handleSignOut, showProfile: $showProfile)
        .background(ColorTheme.superDarkGrey)
        .zIndex(1)

      ScrollView {
        VStack {
          ProfileHeader(profileData: profileData)
          PreferencesContainer(
            preferences: Binding(
              get: {
                Preferences(fromJSON: profileData.preferences ?? "{}")
              },
              set: { newValue in
                if let preferencesJSON = try? JSONEncoder().encode(newValue),
                  let preferencesString = String(data: preferencesJSON, encoding: .utf8)
                {
                  profileData.preferences = preferencesString
                }
              }
            ))
        }
        .padding()
        SignOutButton(action: handleSignOut)
      }
    }
    .frame(maxWidth: .infinity, maxHeight: .infinity)
    .background(ColorTheme.superDarkGrey.edgesIgnoringSafeArea(.all))
  }

  private func handleSignOut() {
    appState.isLoggedIn = false
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
    isPresented = false
  }
}

struct ProfileHeader: View {
  let profileData: ProfileData

  var body: some View {
    HStack(spacing: 16) {
      ProfileImage(url: URL(string: profileData.profile))
      ProfileInfo(profileData: profileData)
      Spacer()
    }
    .padding(.vertical, 16)
    .padding(.horizontal)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}

struct ProfileImage: View {
  let url: URL?

  var body: some View {
    AsyncImage(url: url) { phase in
      switch phase {
      case .empty:
        ProgressView()
          .frame(width: 70, height: 70)
      case .success(let image):
        image
          .resizable()
          .aspectRatio(contentMode: .fill)
      case .failure:
        Image(systemName: "person.circle.fill")
          .resizable()
          .foregroundColor(Color.gray.opacity(0.3))
      @unknown default:
        Color.gray.opacity(0.3)
      }
    }
    .frame(width: 70, height: 70)
    .clipShape(Circle())
  }
}

struct ProfileInfo: View {
  let profileData: ProfileData

  var body: some View {
    VStack(alignment: .leading, spacing: 6) {
      Text("\(profileData.firstname) \(profileData.lastname)")
        .font(.system(size: 18, weight: .semibold))
        .foregroundColor(ColorTheme.white)

      Text(profileData.email)
        .font(.system(size: 14))
        .foregroundColor(ColorTheme.lightGrey)

      HStack(spacing: 6) {
        Circle()
          .fill(profileData.isActive ? ColorTheme.green : ColorTheme.darkGrey)
          .frame(width: 8, height: 8)

        Text(profileData.isActive ? "Active" : "Inactive")
          .font(.system(size: 12))
          .foregroundColor(ColorTheme.lightGrey)
      }
    }
  }
}

struct SignOutButton: View {
  let action: () -> Void

  var body: some View {
    Button(action: action) {
      Text("Sign Out")
        .font(.system(size: 18, weight: .semibold))
        .foregroundColor(ColorTheme.white)
        .frame(maxWidth: .infinity)
        .padding()
        .background(ColorTheme.primary)
        .cornerRadius(12)
    }
    .padding(.horizontal)
    .padding(.bottom, 20)
  }
}
