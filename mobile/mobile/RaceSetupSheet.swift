import SwiftUI

struct RaceSetupSheet: View {
  @Binding var preferences: Preferences
  @Binding var isPresented: Bool
  let onSave: () -> Void

  @State private var selectedDistance: String = ""
  @State private var selectedDate: Date = Date()

  var body: some View {
    NavigationView {
      Form {
        Section {
          Picker("Race Distance", selection: $selectedDistance) {
            Text("Select Distance").tag("")
            Text("5K").tag("5K")
            Text("10K").tag("10K")
            Text("Half Marathon").tag("Half Marathon")
            Text("Marathon").tag("Marathon")
            Text("Ultra Marathon").tag("Ultra Marathon")
          }
          .pickerStyle(MenuPickerStyle())

          DatePicker(
            "Race Date",
            selection: $selectedDate,
            in: Date()...,
            displayedComponents: .date
          )
        }

        Section {
          VStack(alignment: .center, spacing: 16) {
            InfoRow(
              icon: "target",
              text: "Set a goal to stay motivated"
            )

            InfoRow(
              icon: "figure.run",
              text: "Your training plan will update automatically"
            )

            InfoRow(
              icon: "calendar.badge.clock",
              text: "You can adjust your race anytime"
            )
          }
          .frame(maxWidth: .infinity)
          .padding(.vertical, 8)
        }
        .listRowBackground(Color.clear)
      }
      .navigationTitle("Set a Race Goal")
      .navigationBarItems(
        leading: Button("Cancel") { isPresented = false },
        trailing: Button("Save") {
          guard !selectedDistance.isEmpty else { return }
          preferences.raceDistance = selectedDistance
          preferences.raceDate = selectedDate

          onSave()
          isPresented = false
        }
        .disabled(selectedDistance.isEmpty)
      )
    }
    .onAppear {
      if let existingDistance = preferences.raceDistance {
        selectedDistance = existingDistance
      }
      if let existingDate = preferences.raceDate {
        selectedDate = existingDate
      }
    }
  }
}

private struct InfoRow: View {
  let icon: String
  let text: String

  var body: some View {
    HStack {
      Image(systemName: icon)
        .foregroundColor(.blue)
      Text(text)
        .foregroundColor(.secondary)
        .font(.subheadline)
    }
    .frame(maxWidth: .infinity, alignment: .leading)
    .frame(width: 300)
  }
}
