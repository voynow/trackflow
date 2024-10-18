import SwiftUI

struct PickerTextStyle: ViewModifier {
  let isSelected: Bool

  func body(content: Content) -> some View {
    content
      .foregroundColor(isSelected ? ColorTheme.white : ColorTheme.lightGrey.opacity(0.6))
  }
}

struct PreferencesContainer: View {
  @Binding var preferences: Preferences
  @State private var isSaving: Bool = false
  @EnvironmentObject var appState: AppState

  var body: some View {
    ZStack {
      PreferencesContent(
        preferences: $preferences, 
        onUpdate: savePreferences
      )

      if isSaving {
        ProgressView()
          .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.white))
          .scaleEffect(1.5)
      }
    }
    .disabled(isSaving)
  }

  private func savePreferences() {
    guard let token = appState.jwtToken else {
      return
    }

    isSaving = true
    APIManager.shared.savePreferences(token: token, preferences: preferences) { result in
      DispatchQueue.main.async {
        isSaving = false
        switch result {
        case .success:
          // The SaveBanner is now handled within PreferencesContent
          break
        case .failure(let error):
          print("Failed to save preferences: \(error)")
        }
      }
    }
  }
}

struct SaveBanner: View {
  var body: some View {
    HStack {
      Image(systemName: "checkmark.circle.fill")
        .foregroundColor(ColorTheme.green)
      Text("Preferences saved")
        .font(.system(size: 16, weight: .medium))
        .foregroundColor(ColorTheme.white)
    }
    .padding(.vertical, 8)
    .padding(.horizontal, 16)
    .background(Color.black.opacity(0.6))
    .cornerRadius(8)
    .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 2)
  }
}

struct PreferencesContent: View {
  @Binding var preferences: Preferences
  var onUpdate: () -> Void
  @State private var activeSaveSection: String?

  var body: some View {
    VStack(alignment: .leading, spacing: 24) {
      preferenceSectionView(
        title: "Race Details",
        subtitle: "Optionally select your race distance",
        sectionId: "race"
      ) {
        preferenceRowView(
          title: "Race Distance",
          value: Binding(
            get: { preferences.raceDistance ?? "" },
            set: {
              preferences.raceDistance = $0.isEmpty ? nil : $0
              onUpdate()
              showSaveBanner(for: "race")
            }
          )
        ) { binding in
          CustomPickerWrapper(
            selection: binding,
            content: AnyView(
              Picker("Race Distance", selection: binding) {
                Text("No Preference").tag("")
                Text("5K").tag("5k")
                Text("10K").tag("10k")
                Text("Half Marathon").tag("half marathon")
                Text("Marathon").tag("marathon")
                Text("Ultra Marathon").tag("ultra marathon")
              }
              .pickerStyle(MenuPickerStyle())
            )
          )
        }
      }

      preferenceSectionView(
        title: "Training Week",
        subtitle: "Help our AI understand your preferences",
        sectionId: "training"
      ) {
        ForEach(Day.allCases, id: \.self) { day in
          preferenceRowView(
            title: day.fullName,
            value: sessionTypeBinding(for: day)
          ) { binding in
            CustomPickerWrapper(
              selection: binding,
              content: AnyView(
                Picker("Session Type", selection: binding) {
                  Text("No Preference").tag("")
                  Text("Easy Run").tag("easy run")
                  Text("Long Run").tag("long run")
                  Text("Speed Workout").tag("speed workout")
                  Text("Rest Day").tag("rest day")
                  Text("Moderate Run").tag("moderate run")
                }
                .pickerStyle(MenuPickerStyle())
              )
            )
          }
        }
      }
    }
    .background(ColorTheme.black)
  }

  private func showSaveBanner(for section: String) {
    activeSaveSection = section
    DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
      if activeSaveSection == section {
        activeSaveSection = nil
      }
    }
  }

  private func sessionTypeBinding(for day: Day) -> Binding<String> {
    Binding(
      get: {
        preferences.idealTrainingWeek?.first(where: { $0.day == day })?.sessionType ?? ""
      },
      set: { newValue in
        updateSessionType(for: day, with: newValue)
        showSaveBanner(for: "training")
      }
    )
  }

  private func updateSessionType(for day: Day, with newValue: String) {
    if preferences.idealTrainingWeek == nil {
      preferences.idealTrainingWeek = []
    }

    if newValue.isEmpty {
      // Remove the entry if "No Preference" is selected
      preferences.idealTrainingWeek?.removeAll { $0.day == day }
    } else {
      if let index = preferences.idealTrainingWeek?.firstIndex(where: { $0.day == day }) {
        preferences.idealTrainingWeek?[index].sessionType = newValue
      } else {
        preferences.idealTrainingWeek?.append(TrainingDay(day: day, sessionType: newValue))
      }
    }
    onUpdate()
  }

  private func preferenceSectionView<Content: View>(
    title: String,
    subtitle: String,
    sectionId: String,
    @ViewBuilder content: () -> Content
  ) -> some View {
    ZStack(alignment: .topTrailing) {
      VStack(alignment: .leading, spacing: 16) {
        VStack(alignment: .leading, spacing: 4) {
          Text(title)
            .font(.system(size: 20, weight: .semibold))
            .foregroundColor(ColorTheme.white)
          Text(subtitle)
            .font(.system(size: 14))
            .foregroundColor(ColorTheme.midLightGrey)
        }
        content()
      }
      .padding(24)
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(12)
      
      if activeSaveSection == sectionId {
        SaveBanner()
          .transition(.move(edge: .top).combined(with: .opacity))
          .animation(.easeInOut(duration: 0.3), value: activeSaveSection)
          .padding(.top, 8)
          .padding(.trailing, 8)
      }
    }
  }

  private func preferenceRowView<Value: Equatable, EditContent: View>(
    title: String,
    value: Binding<Value>,
    @ViewBuilder editContent: (Binding<Value>) -> EditContent
  ) -> some View {
    HStack {
      Text(title)
        .font(.system(size: 16))
        .foregroundColor(ColorTheme.primaryLight)
      Spacer()
      editContent(value)
        .foregroundColor(ColorTheme.lightGrey)
    }
    .padding(.horizontal, 12)
  }
}

struct CustomPickerWrapper: View {
  @Binding var selection: String
  let content: AnyView

  var body: some View {
    content
      .opacity(selection.isEmpty ? 0.4 : 1.0)
  }
}
