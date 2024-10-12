import SwiftUI

struct ProfileView: View {
  @Binding var isPresented: Bool
  @Binding var profileData: ProfileData
  @State private var preferences: Preferences
  @State private var isEditing: Bool = false
  @State private var isSaving: Bool = false
  @EnvironmentObject var appState: AppState
  @Binding var showProfile: Bool

  init(isPresented: Binding<Bool>, profileData: Binding<ProfileData>, showProfile: Binding<Bool>) {
    self._isPresented = isPresented
    self._profileData = profileData
    self._showProfile = showProfile
    self._preferences = State(
      initialValue: Preferences(fromJSON: profileData.wrappedValue.preferences ?? "{}"))
  }

  var body: some View {
    VStack(spacing: 0) {
      DashboardNavbar(onLogout: handleSignOut, showProfile: $showProfile)
        .background(ColorTheme.superDarkGrey)
        .zIndex(1)

      ScrollView {
        VStack {
          HStack(spacing: 16) {
            AsyncImage(url: URL(string: profileData.profile)) { phase in
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

            Spacer()
          }
          .padding(.vertical, 16)
          .padding(.horizontal)
          .background(ColorTheme.darkDarkGrey)
          .cornerRadius(12)

          if isEditing {
            PreferencesForm(
              preferences: $preferences,
              onSave: handleSavePreferences,
              onCancel: { isEditing = false },
              isSaving: $isSaving
            )
          } else {
            PreferencesView(preferences: preferences, isEditing: $isEditing)
          }
        }
        .padding()
      }

      Spacer()

      Button(action: handleSignOut) {
        Text("Sign Out")
          .font(.system(size: 18, weight: .semibold))
          .foregroundColor(ColorTheme.white)
          .frame(maxWidth: .infinity)
          .padding()
          .background(ColorTheme.redPink)
          .cornerRadius(12)
      }
      .padding(.horizontal)
      .padding(.bottom, 20)
    }
    .frame(maxWidth: .infinity, maxHeight: .infinity)
    .background(ColorTheme.superDarkGrey.edgesIgnoringSafeArea(.all))
  }

  private func handleSavePreferences() {
    isSaving = true
    DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
      let encoder = JSONEncoder()
      if let preferencesJSON = try? encoder.encode(preferences),
        let preferencesString = String(data: preferencesJSON, encoding: .utf8)
      {
        profileData.preferences = preferencesString
      }
      isEditing = false
      isSaving = false
    }
  }

  private func handleSignOut() {
    appState.isLoggedIn = false
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
    isPresented = false
  }
}

struct PreferencesView: View {
  let preferences: Preferences
  @Binding var isEditing: Bool

  var body: some View {
    VStack(alignment: .leading, spacing: 20) {
      // Title and Edit button
      HStack {
        Text("Preferences")
          .font(.title)
          .fontWeight(.bold)
          .foregroundColor(ColorTheme.white)
        Spacer()
        Button(action: { isEditing.toggle() }) {
          Text("Edit")
            .foregroundColor(ColorTheme.primary)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(ColorTheme.darkGrey)
            .cornerRadius(8)
        }
      }
    
      // Race Details section
      PreferenceSection(title: "Race Details") {
        HStack {
          Text("Race Distance")
            .font(.subheadline)
            .foregroundColor(ColorTheme.lightGrey)
          Spacer()
          Text(preferences.raceDistance ?? "Not set")
            .foregroundColor(ColorTheme.white)
        }
      }

      // Ideal Training Week section
      PreferenceSection(title: "Ideal Training Week") {
        ForEach(Day.allCases, id: \.self) { day in
          HStack {
            Text(day.rawValue)
              .font(.subheadline)
              .foregroundColor(ColorTheme.lightGrey)
            Spacer()
            Text(
              preferences.idealTrainingWeek?.first(where: { $0.day == day })?.sessionType
                ?? "No Preference"
            )
            .foregroundColor(ColorTheme.white)
          }
        }
      }
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}

struct PreferenceSection<Content: View>: View {
  let title: String
  let content: Content

  init(title: String, @ViewBuilder content: () -> Content) {
    self.title = title
    self.content = content()
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      Text(title)
        .font(.title3)
        .fontWeight(.semibold)
        .foregroundColor(ColorTheme.lightGrey)
      
      content
        .padding()
        .cornerRadius(8)
    }
  }
}

struct PreferencesForm: View {
  @Binding var preferences: Preferences
  let onSave: () -> Void
  let onCancel: () -> Void
  @Binding var isSaving: Bool

  var body: some View {
    VStack(alignment: .leading, spacing: 16) {
      HStack {
        Text("Edit Preferences")
          .font(.title2)
          .fontWeight(.bold)
          .foregroundColor(ColorTheme.white)
        Spacer()
      }

      Text("Race Distance")
        .font(.headline)
        .foregroundColor(ColorTheme.lightGrey)
      Picker(
        "Race Distance",
        selection: Binding(
          get: { preferences.raceDistance ?? "" },
          set: { preferences.raceDistance = $0.isEmpty ? nil : $0 }
        )
      ) {
        Text("Select distance").tag("")
        Text("5K").tag("5k")
        Text("10K").tag("10k")
        Text("Half Marathon").tag("half marathon")
        Text("Marathon").tag("marathon")
        Text("Ultra Marathon").tag("ultra marathon")
        Text("None").tag("none")
      }
      .pickerStyle(MenuPickerStyle())
      .foregroundColor(ColorTheme.white)

      Text("Ideal Training Week")
        .font(.headline)
        .foregroundColor(ColorTheme.lightGrey)

      ForEach(Day.allCases, id: \.self) { day in
        HStack {
          Text(day.rawValue)
            .foregroundColor(ColorTheme.lightGrey)
          Spacer()
          Picker(
            "Session Type",
            selection: Binding(
              get: {
                preferences.idealTrainingWeek?.first(where: { $0.day == day })?.sessionType ?? ""
              },
              set: { newValue in
                if var week = preferences.idealTrainingWeek {
                  if let index = week.firstIndex(where: { $0.day == day }) {
                    week[index] = TrainingDay(day: day, sessionType: newValue)
                  } else {
                    week.append(TrainingDay(day: day, sessionType: newValue))
                  }
                  preferences.idealTrainingWeek = week
                } else {
                  preferences.idealTrainingWeek = [TrainingDay(day: day, sessionType: newValue)]
                }
              }
            )
          ) {
            Text("No Preference").tag("")
            Text("Easy Run").tag("easy run")
            Text("Long Run").tag("long run")
            Text("Speed Workout").tag("speed workout")
            Text("Rest Day").tag("rest day")
            Text("Moderate Run").tag("moderate run")
          }
          .pickerStyle(MenuPickerStyle())
          .foregroundColor(ColorTheme.white)
        }
      }

      HStack {
        Button(action: onCancel) {
          Text("Cancel")
            .foregroundColor(ColorTheme.white)
            .padding()
            .background(ColorTheme.darkGrey)
            .cornerRadius(8)
        }

        Spacer()

        Button(action: onSave) {
          if isSaving {
            ProgressView()
              .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.white))
          } else {
            Text("Save")
          }
        }
        .foregroundColor(ColorTheme.white)
        .padding()
        .background(ColorTheme.primary)
        .cornerRadius(8)
        .disabled(isSaving)
      }
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}
