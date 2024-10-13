import SwiftUI

struct PreferencesContainer: View {
  @Binding var preferences: Preferences
  @State private var isSaving: Bool = false

  var body: some View {
    VStack(alignment: .leading) {
      Text("Preferences")
        .font(.title2)
        .fontWeight(.bold)
        .foregroundColor(ColorTheme.white)

      PreferencesContent(preferences: $preferences, onUpdate: savePreferences)
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
    .overlay(
      Group {
        if isSaving {
          ProgressView()
            .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.primary))
        }
      }
    )
  }

  private func savePreferences() {
    isSaving = true
    // Simulate API call
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
      isSaving = false
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
            Text("Select distance").tag("")
            Text("5K").tag("5k")
            Text("10K").tag("10k")
            Text("Half Marathon").tag("half marathon")
            Text("Marathon").tag("marathon")
            Text("Ultra Marathon").tag("ultra marathon")
            Text("None").tag("none")
          }
          .pickerStyle(MenuPickerStyle())
        }
      }

      preferenceSectionView(title: "Ideal Training Week") {
        ForEach(Day.allCases, id: \.self) { day in
          preferenceRowView(
            title: day.rawValue,
            value: sessionTypeBinding(for: day)
          ) {
            Picker("Session Type", selection: $0) {
              Text("No Preference").tag("")
              Text("Easy Run").tag("easy run")
              Text("Long Run").tag("long run")
              Text("Speed Workout").tag("speed workout")
              Text("Rest Day").tag("rest day")
              Text("Moderate Run").tag("moderate run")
            }
            .pickerStyle(MenuPickerStyle())
          }
        }
      }
    }
  }

  private func sessionTypeBinding(for day: Day) -> Binding<String> {
    Binding(
      get: { sessionType(for: day) },
      set: {
        updateSessionType(for: day, with: $0)
        onUpdate()
      }
    )
  }

  private func sessionType(for day: Day) -> String {
    preferences.idealTrainingWeek?.first(where: { $0.day == day })?.sessionType ?? ""
  }

  private func updateSessionType(for day: Day, with newValue: String) {
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

  private func preferenceRowView<Value, EditContent: View>(
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
        .foregroundColor(ColorTheme.white)
        .frame(height: 30)
    }
    .frame(height: 44)
  }
}
