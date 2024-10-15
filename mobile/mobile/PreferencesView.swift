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
    ZStack(alignment: .topTrailing) {
      VStack(alignment: .leading, spacing: 20) {
        Text("Preferences")
          .font(.title)
          .fontWeight(.bold)
          .foregroundColor(ColorTheme.white)

        PreferencesContent(preferences: $preferences, onUpdate: savePreferences)
      }
      .padding()
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(12)

      SavedPopup(isShowing: $showingSavedPopup)
        .padding([.top, .trailing], 16)
    }
    .disabled(isSaving)
    .overlay(
      Group {
        if isSaving {
          ProgressView()
            .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.white))
            .scaleEffect(1.5)
        }
      }
    )
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
          showingSavedPopup = true
          DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            showingSavedPopup = false
          }
        case .failure(let error):
          print("Failed to save preferences: \(error.localizedDescription)")
        }
      }
    }
  }
}

struct SavedPopup: View {
  @Binding var isShowing: Bool

  var body: some View {
    Group {
      if isShowing {
        Text("Saved")
          .font(.subheadline)
          .fontWeight(.semibold)
          .foregroundColor(ColorTheme.white)
          .padding(.horizontal, 16)
          .padding(.vertical, 8)
          .background(ColorTheme.green)
          .cornerRadius(20)
          .transition(.scale.combined(with: .opacity))
          .animation(.easeInOut(duration: 0.3), value: isShowing)
      }
    }
  }
}

struct PreferencesContent: View {
  @Binding var preferences: Preferences
  var onUpdate: () -> Void

  var body: some View {
    VStack(alignment: .leading, spacing: 20) {
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
            title: day.rawValue,
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

    if let index = preferences.idealTrainingWeek?.firstIndex(where: { $0.day == day }) {
      preferences.idealTrainingWeek?[index].sessionType = newValue
    } else {
      preferences.idealTrainingWeek?.append(TrainingDay(day: day, sessionType: newValue))
    }
    onUpdate()
  }

  private func preferenceSectionView<Content: View>(
    title: String, @ViewBuilder content: () -> Content
  ) -> some View {
    VStack(alignment: .leading, spacing: 4) {
      Text(title)
        .font(.headline)
        .fontWeight(.semibold)
        .foregroundColor(ColorTheme.lightGrey)
      content()
    }
  }

  private func preferenceRowView<Value: Equatable, EditContent: View>(
    title: String,
    value: Binding<Value>,
    @ViewBuilder editContent: (Binding<Value>) -> EditContent
  ) -> some View {
    HStack {
      Text(title)
        .font(.subheadline)
        .foregroundColor(ColorTheme.lightGrey)
      Spacer()
      editContent(value)
        .frame(height: 30)
        .foregroundColor(
          (value.wrappedValue as? String)?.isEmpty == true
            ? ColorTheme.lightGrey
            : ColorTheme.white
        )
    }
    .frame(height: 44)
  }
}

struct CustomPickerWrapper: View {
  @Binding var selection: String
  let content: AnyView

  var body: some View {
    content
      .opacity(selection.isEmpty ? 0.6 : 1.0)
  }
}
