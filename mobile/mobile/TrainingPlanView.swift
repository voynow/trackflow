import Charts
import SwiftUI

struct TrainingPlanView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingPlan: TrainingPlan?
  @State private var profileData: ProfileData?
  @State private var isLoading = true
  @State private var errorMessage: String?
  @State private var showProfile: Bool = false
  let historicalWeeks: [WeekSummary]

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
            if let preferences = decodePreferences() {
              RaceDetailsWidget(
                preferences: preferences,
                weeksCount: plan.trainingWeekPlans.map(\.nWeeksUntilRace).max() ?? 0
              )
              .padding(.bottom, 8)
            }

            TrainingPlanChart(
              trainingWeeks: plan.trainingWeekPlans,
              historicalWeeks: historicalWeeks
            )
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
      if trainingPlan == nil {
        fetchTrainingPlanData()
      }
      if profileData == nil {
        fetchProfileData()
      }
    }
    .refreshable {
      fetchTrainingPlanData()
      fetchProfileData()
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

  private func decodePreferences() -> Preferences? {
    guard let preferencesString = profileData?.preferences,
      let jsonData = preferencesString.data(using: .utf8)
    else {
      return nil
    }

    do {
      let decoder = JSONDecoder()
      decoder.dateDecodingStrategy = .iso8601
      return try decoder.decode(Preferences.self, from: jsonData)
    } catch {
      print("Failed to decode preferences: \(error)")
      return nil
    }
  }

  private func fetchProfileData() {
    guard let token = appState.jwtToken else { return }

    APIManager.shared.fetchProfileData(token: token) { result in
      DispatchQueue.main.async {
        if case .success(let profile) = result {
          self.profileData = profile
        }
      }
    }
  }
}

struct TrainingPlanChart: View {
  let trainingWeeks: [TrainingPlanWeek]
  let historicalWeeks: [WeekSummary]
  @State private var selectedWeek: WeekOrHistoricalWeek
  @State private var selectedX: Int

  enum WeekOrHistoricalWeek {
    case future(TrainingPlanWeek)
    case past(WeekSummary)
    
    var date: Date {
      switch self {
      case .future(let week): return week.weekStartDate
      case .past(let summary): 
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.date(from: summary.weekStartDate) ?? Date()
      }
    }
    
    var weekNumber: Int {
      switch self {
      case .future(let week): return week.weekNumber
      case .past(let summary): return -summary.weekOfYear
      }
    }
    
    var totalDistance: Double {
      switch self {
      case .future(let week): return week.totalDistance
      case .past(let summary): return summary.totalDistance
      }
    }
    
    var longRunDistance: Double {
      switch self {
      case .future(let week): return week.longRunDistance
      case .past(let summary): return summary.longestRun
      }
    }
  }

  private var dateRange: ClosedRange<Date> {
    let historicalDates = historicalWeeks.compactMap { week -> Date? in
      let formatter = DateFormatter()
      formatter.dateFormat = "yyyy-MM-dd"
      return formatter.date(from: week.weekStartDate)
    }
    
    let startDate = historicalDates.min() ?? trainingWeeks.first!.weekStartDate
    let endDate = trainingWeeks.last?.weekStartDate ?? Date()
    
    return startDate...endDate
  }

  init(trainingWeeks: [TrainingPlanWeek], historicalWeeks: [WeekSummary] = []) {
    self.trainingWeeks = trainingWeeks
    self.historicalWeeks = historicalWeeks
    _selectedWeek = State(initialValue: .future(trainingWeeks[0]))
    _selectedX = State(initialValue: trainingWeeks[0].weekNumber)
  }

  private var historicalVolumePlot: some ChartContent {
    ForEach(historicalWeeks, id: \.weekStartDate) { week in
      LineMark(
        x: .value("Week", week.parsedWeekStartDate ?? Date()),
        y: .value("Miles", week.totalDistance)
      )
      .foregroundStyle(by: .value("Type", "Past Volume"))
      .lineStyle(StrokeStyle(lineWidth: 2))
      .symbol(.square)
    }
  }

  private var historicalLongRunPlot: some ChartContent {
    ForEach(historicalWeeks, id: \.weekStartDate) { week in
      LineMark(
        x: .value("Week", week.parsedWeekStartDate ?? Date()),
        y: .value("Miles", week.longestRun)
      )
      .foregroundStyle(by: .value("Type", "Past Long Run"))
      .lineStyle(StrokeStyle(lineWidth: 2))
      .symbol(.square)
    }
  }

  private var futureTotalVolumePlot: some ChartContent {
    ForEach(trainingWeeks) { week in
      LineMark(
        x: .value("Week", week.weekStartDate),
        y: .value("Miles", week.totalDistance)
      )
      .foregroundStyle(by: .value("Type", "Volume"))
      .lineStyle(StrokeStyle(lineWidth: 2))
      .symbol(.circle)
    }
  }

  private var futureLongRunPlot: some ChartContent {
    ForEach(trainingWeeks) { week in
      LineMark(
        x: .value("Week", week.weekStartDate),
        y: .value("Miles", week.longRunDistance)
      )
      .foregroundStyle(by: .value("Type", "Long Run"))
      .lineStyle(StrokeStyle(lineWidth: 2))
      .symbol(.circle)
    }
  }

  private var chartTitle: some View {
    Text("Weekly Training Progression")
      .font(.headline)
      .foregroundColor(ColorTheme.lightGrey)
      .padding(.bottom, 8)
  }

  private var mainChart: some View {
    Chart {
      historicalVolumePlot
      historicalLongRunPlot
      futureTotalVolumePlot
      futureLongRunPlot

      RuleMark(
        x: .value("Week", selectedWeek.date)
      )
      .foregroundStyle(ColorTheme.lightGrey.opacity(0.3))
    }
    .chartXScale(domain: dateRange)
    .chartXAxis {
      AxisMarks(values: .stride(by: .weekOfYear)) { value in
        AxisGridLine()
        AxisTick()
        AxisValueLabel(format: .dateTime.month().day())
      }
    }
    .chartForegroundStyleScale([
      "Past Volume": ColorTheme.primaryDark,
      "Past Long Run": ColorTheme.indigoDark,
      "Volume": ColorTheme.primary,
      "Long Run": ColorTheme.indigo
    ])
    .chartLegend(position: .bottom) {
      HStack {
        LegendItem(label: "Past Volume", symbol: .square, color: ColorTheme.primaryDark)
        LegendItem(label: "Past Long Run", symbol: .square, color: ColorTheme.indigoDark)
        LegendItem(label: "Volume", symbol: .circle, color: ColorTheme.primary)
        LegendItem(label: "Long Run", symbol: .circle, color: ColorTheme.indigo)
      }
    }
    .frame(height: 250)
    .chartOverlay { proxy in
      GeometryReader { geometry in
        Rectangle()
          .fill(.clear)
          .contentShape(Rectangle())
          .gesture(
            DragGesture(minimumDistance: 0)
              .onChanged { value in
                let x = value.location.x
                if let date = proxy.value(atX: x, as: Date.self) {
                  if let historicalWeek = historicalWeeks
                    .min(by: { abs($0.parsedWeekStartDate?.timeIntervalSince(date) ?? .infinity) < abs($1.parsedWeekStartDate?.timeIntervalSince(date) ?? .infinity) }),
                     let historicalDate = historicalWeek.parsedWeekStartDate,
                     let futureWeek = trainingWeeks
                      .min(by: { abs($0.weekStartDate.timeIntervalSince(date) ?? .infinity) < abs($1.weekStartDate.timeIntervalSince(date) ?? .infinity) })
                  {
                    let historicalDiff = abs(historicalDate.timeIntervalSince(date))
                    let futureDiff = abs(futureWeek.weekStartDate.timeIntervalSince(date))
                    
                    selectedWeek = historicalDiff < futureDiff ? 
                      .past(historicalWeek) : 
                      .future(futureWeek)
                  }
                }
              }
          )
      }
    }
  }

  private var weekDetails: some View {
    VStack(alignment: .leading, spacing: 8) {
        switch selectedWeek {
        case .future(let week):
            HStack {
                Text(week.weekStartDate.formatted(date: .long, time: .omitted))
                    .font(.title3)
                    .foregroundColor(ColorTheme.lightGrey)
                Spacer()
                Text("\(week.weekType.rawValue.capitalized) Week")
                    .padding(4)
                    .background(week.weekType.color)
                    .cornerRadius(4)
                    .foregroundColor(ColorTheme.black)
            }

            Text("Total: \(week.totalDistance, specifier: "%.1f") miles")
                .foregroundColor(ColorTheme.primary)

            Text("Long Run: \(week.longRunDistance, specifier: "%.1f") miles")
                .foregroundColor(ColorTheme.indigo)

            if !week.notes.isEmpty {
                Text(week.notes)
                    .foregroundColor(ColorTheme.lightGrey)
                    .font(.subheadline)
                    .padding(.top, 4)
            }
            
        case .past(let week):
            HStack {
                Text(week.parsedWeekStartDate?.formatted(date: .long, time: .omitted) ?? week.weekStartDate)
                    .font(.title3)
                    .foregroundColor(ColorTheme.lightGrey)
                Spacer()
                Text("Past Week")
                    .padding(4)
                    .background(ColorTheme.midLightGrey)
                    .cornerRadius(4)
                    .foregroundColor(ColorTheme.black)
            }
            
            Text("Total: \(week.totalDistance, specifier: "%.1f") miles")
                .foregroundColor(ColorTheme.primary)
            
            Text("Long Run: \(week.longestRun, specifier: "%.1f") miles")
                .foregroundColor(ColorTheme.indigo)
        }
    }
    .padding(.top, 8)
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 8) {
      chartTitle
      mainChart
      weekDetails
    }
    .padding(16)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}

struct RaceDetailsWidget: View {
  let preferences: Preferences
  let weeksCount: Int

  var body: some View {
    VStack(alignment: .leading, spacing: 8) {
      HStack(alignment: .firstTextBaseline) {
        Text("\(weeksCount)")
          .font(.system(size: 48, weight: .bold))
          .foregroundColor(ColorTheme.lightGrey)
        Text("Weeks Out From Race Day")
          .font(.system(size: 24, weight: .bold))
          .foregroundColor(ColorTheme.white)
      }
      .padding(.bottom, 16)

      HStack(spacing: 24) {
        VStack(alignment: .leading) {
          Text("Distance")
            .font(.subheadline)
            .foregroundColor(ColorTheme.midLightGrey)
          Text(preferences.raceDistance ?? "")
            .font(.title3)
            .foregroundColor(ColorTheme.primaryLight)
        }

        VStack(alignment: .leading) {
          Text("Date")
            .font(.subheadline)
            .foregroundColor(ColorTheme.midLightGrey)
          Text(preferences.raceDate?.formatted(date: .long, time: .omitted) ?? "")
            .font(.title3)
            .foregroundColor(ColorTheme.primaryLight)
        }
      }
    }
    .padding(16)
    .frame(maxWidth: .infinity, alignment: .leading)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}

struct LegendItem: View {
  let label: String
  let symbol: Symbol
  let color: Color
  
  enum Symbol {
    case circle, square
  }
  
  var body: some View {
    HStack(spacing: 4) {
      switch symbol {
      case .circle:
        Circle()
          .fill(color)
          .frame(width: 8, height: 8)
      case .square:
        Rectangle()
          .fill(color)
          .frame(width: 8, height: 8)
      }
      Text(label)
        .font(.caption)
        .foregroundColor(ColorTheme.lightGrey)
    }
  }
}