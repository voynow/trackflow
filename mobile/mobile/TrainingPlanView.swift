import Charts
import SwiftUI

struct TrainingPlanView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingPlan: TrainingPlan?
  @State private var isLoading = true
  @State private var errorMessage: String?
  @State private var showProfile: Bool = false

  var body: some View {
    VStack {
      DashboardNavbar(onLogout: handleLogout, showProfile: $showProfile)
        .background(ColorTheme.black)
        .zIndex(1)

      ScrollView {
        VStack(spacing: 16) {
          if isLoading {
            ProgressView("Loading training plan...")
              .foregroundColor(ColorTheme.lightGrey)
          } else if let plan = trainingPlan {
            TrainingPlanChart(trainingWeeks: plan.trainingWeekPlans)
            TrainingStatsWidget(trainingWeeks: plan.trainingWeekPlans)
          } else if let error = errorMessage {
            Text("Error: \(error)")
              .foregroundColor(.red)
          }
        }
        .padding()
      }
    }
    .background(ColorTheme.black.edgesIgnoringSafeArea(.all))
    .onAppear {
      fetchTrainingPlanData()
    }
    .navigationBarHidden(true)

    if showProfile {
      ProfileView(
        isPresented: $showProfile,
        showProfile: $showProfile
      )
      .transition(.move(edge: .trailing))
      .zIndex(2)
    }
  }

  private func handleLogout() {
    appState.status = .loggedOut
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
  }

  private func fetchTrainingPlanData() {
    guard let token = appState.jwtToken else {
      errorMessage = "No valid token"
      isLoading = false
      return
    }

    APIManager.shared.fetchTrainingPlan(token: token) { result in
      DispatchQueue.main.async {
        switch result {
        case .success(let plan):
          for week in plan.trainingWeekPlans {
            print(
              "Week \(week.weekNumber): Total=\(week.totalDistance), Long=\(week.longRunDistance)")
          }

          withAnimation {
            self.trainingPlan = plan
          }
        case .failure(let error):
          self.errorMessage = error.localizedDescription
        }
        self.isLoading = false
      }
    }
  }
}

struct TrainingPlanChart: View {
  let trainingWeeks: [TrainingPlanWeek]
  @State private var selectedWeek: TrainingPlanWeek
  @State private var selectedX: Int

  init(trainingWeeks: [TrainingPlanWeek]) {
    self.trainingWeeks = trainingWeeks
    _selectedWeek = State(initialValue: trainingWeeks[0])
    _selectedX = State(initialValue: trainingWeeks[0].weekNumber)
  }

  private var weekRange: ClosedRange<Int> {
    guard let firstWeek = trainingWeeks.first?.weekNumber,
      let lastWeek = trainingWeeks.last?.weekNumber
    else {
      return 1...1
    }
    return firstWeek...lastWeek
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 8) {
      VStack(alignment: .leading, spacing: 4) {
        HStack(alignment: .firstTextBaseline) {
          Text("\(trainingWeeks.count)")
            .font(.system(size: 32, weight: .bold))
            .foregroundColor(ColorTheme.primary)
          Text("Weeks Out From Race Day")
            .font(.system(size: 24, weight: .bold))
            .foregroundColor(ColorTheme.white)
        }
        .padding(.bottom, 12)

        Text("Weekly Mileage Progression")
          .font(.headline)
          .foregroundColor(ColorTheme.lightGrey)
      }
      .padding(.bottom, 8)

      Chart {
        ForEach(trainingWeeks) { week in
          LineMark(
            x: .value("Week", week.weekNumber),
            y: .value("Miles", week.totalDistance)
          )
          .foregroundStyle(by: .value("Type", "Total Weekly"))
          .lineStyle(StrokeStyle(lineWidth: 2))
          .symbol(.circle)
        }

        ForEach(trainingWeeks) { week in
          LineMark(
            x: .value("Week", week.weekNumber),
            y: .value("Miles", week.longRunDistance)
          )
          .foregroundStyle(by: .value("Type", "Long Run"))
          .lineStyle(StrokeStyle(lineWidth: 2, dash: [5, 5]))
          .symbol(.square)
        }

        RuleMark(
          x: .value("Week", selectedX)
        )
        .foregroundStyle(ColorTheme.lightGrey.opacity(0.3))
      }
      .chartXScale(domain: weekRange)
      .chartXAxis {
        AxisMarks(values: .stride(by: 1))
      }
      .chartForegroundStyleScale([
        "Total Weekly": ColorTheme.primary,
        "Long Run": ColorTheme.redPink,
      ])
      .frame(height: 250)
      .chartOverlay { proxy in
        GeometryReader { geometry in
          Rectangle()
            .fill(.clear)
            .contentShape(Rectangle())
            .onTapGesture { location in
              let x = location.x - geometry[proxy.plotFrame!].origin.x
              let relativeX = x / geometry[proxy.plotFrame!].width

              let weekSpan = Double(weekRange.upperBound - weekRange.lowerBound)
              let week = Int(round(relativeX * weekSpan)) + weekRange.lowerBound

              if weekRange.contains(week),
                let tappedWeek = trainingWeeks.first(where: { $0.weekNumber == week })
              {
                withAnimation {
                  selectedWeek = tappedWeek
                  selectedX = week
                }
              }
            }
        }
      }

      VStack(alignment: .leading, spacing: 8) {
        Text("Week \(selectedWeek.weekNumber)")
          .font(.headline)
          .foregroundColor(ColorTheme.lightGrey)
        
        Text("Total: \(selectedWeek.totalDistance, specifier: "%.1f") miles")
          .foregroundColor(ColorTheme.primary)
        
        Text("Long Run: \(selectedWeek.longRunDistance, specifier: "%.1f") miles")
          .foregroundColor(ColorTheme.redPink)
        
        if !selectedWeek.notes.isEmpty {
          Text(selectedWeek.notes)
            .foregroundColor(ColorTheme.lightGrey)
            .font(.subheadline)
            .padding(.top, 4)
        }
      }
      .padding(.top, 8)
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}

struct TrainingStatsWidget: View {
  let trainingWeeks: [TrainingPlanWeek]

  var body: some View {
    HStack {
      VStack {
        Text("Remaining Mileage")
          .font(.headline)
          .foregroundColor(ColorTheme.lightGrey)
        Text("\(trainingWeeks.reduce(0) { $0 + $1.totalDistance }, specifier: "%.1f") miles")
          .font(.title)
          .foregroundColor(ColorTheme.primary)
      }
      .padding()
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(12)

      VStack {
        Text("Avg Long Run")
          .font(.headline)
          .foregroundColor(ColorTheme.lightGrey)
        Text(
          "\(trainingWeeks.reduce(0) { $0 + $1.longRunDistance } / Double(trainingWeeks.count), specifier: "%.1f") miles"
        )
        .font(.title)
        .foregroundColor(ColorTheme.redPink)
      }
      .padding()
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(12)
    }
  }
}
