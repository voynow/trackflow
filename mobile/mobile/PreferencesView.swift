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
  @State private var showingSavedPopup: Bool = false
  @State private var isSaving: Bool = false
  @EnvironmentObject var appState: AppState

  var body: some View {
    ZStack {
      PreferencesContent(preferences: $preferences, onUpdate: savePreferences)

      if showingSavedPopup {
        SavedPopup()
          .transition(.scale.combined(with: .opacity))
          .animation(.easeInOut(duration: 0.3), value: showingSavedPopup)
      }

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
          withAnimation {
            showingSavedPopup = true
          }
          DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            withAnimation {
              showingSavedPopup = false
            }
          }
        case .failure(let error):
          print("Failed to save preferences: \(error)")
        }
      }
    }
  }
}

struct SavedPopup: View {
  var body: some View {
    Text("Saved")
      .font(.system(size: 32, weight: .semibold))
      .foregroundColor(ColorTheme.green)
      .padding(12)
      .background(ColorTheme.green.opacity(0.25))
      .cornerRadius(16)
      .shadow(color: Color.black.opacity(0.1), radius: 10, x: 0, y: 5)
  }
}

struct PreferencesContent: View {
  @Binding var preferences: Preferences
  var onUpdate: () -> Void

  var body: some View {
    VStack(alignment: .leading, spacing: 24) {
      preferenceSectionView(title: "Race Details") {
        preferenceRowView(
          title: "Race Distance",
          value: Binding(
            get: { preferences.raceDistance ?? "" },
            set: {
              preferences.raceDistance = $0.isEmpty ? nil : $0
              onUpdate()
            }
          )
        ) {
          Picker("Race Distance", selection: $0) {
            Text("Select distance").tag("none")
            Text("5K").tag("5k")
            Text("10K").tag("10k")
            Text("Half Marathon").tag("half marathon")
            Text("Marathon").tag("marathon")
            Text("Ultra Marathon").tag("ultra marathon")
          }
          .pickerStyle(MenuPickerStyle())
        }
      }

      preferenceSectionView(title: "Ideal Training Week") {
        ForEach(Day.allCases, id: \.self) { day in
          preferenceRowView(
            title: day.fullName,
            value: sessionTypeBinding(for: day)
          ) { binding in
            CustomPickerWrapper(
              selection: binding,
              content:
                AnyView(
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

  private func sessionTypeBinding(for day: Day) -> Binding<String> {
    Binding(
      get: {
        preferences.idealTrainingWeek?.first(where: { $0.day == day })?.sessionType ?? ""
      },
      set: { newValue in
        updateSessionType(for: day, with: newValue)
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
    title: String, @ViewBuilder content: () -> Content
  ) -> some View {
    VStack(alignment: .leading, spacing: 16) {
      Text(title)
        .font(.system(size: 20, weight: .semibold))
        .foregroundColor(ColorTheme.white)
      content()
    }
    .padding(24)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }

  private func preferenceRowView<Value: Equatable, EditContent: View>(
    title: String,
    value: Binding<Value>,
    @ViewBuilder editContent: (Binding<Value>) -> EditContent
  ) -> some View {
    HStack {
      Text(title)
        .font(.system(size: 16))
        .foregroundColor(ColorTheme.white)
      Spacer()
      editContent(value)
        .foregroundColor(ColorTheme.lightGrey) // Add this line to change the color
    }
    .padding(.vertical, 8)
    .padding(.horizontal, 12)
  }
}

struct CustomPickerWrapper: View {
  @Binding var selection: String
  let content: AnyView

  var body: some View {
    content
      .opacity(selection.isEmpty ? 0.4 : 1.0)
      .foregroundColor(selection.isEmpty ? ColorTheme.lightGrey : ColorTheme.white) // Add this line
      .animation(.easeInOut(duration: 0.1), value: selection)
  }
}
