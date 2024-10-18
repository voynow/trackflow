import SwiftUI

struct DashboardView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingWeekData: TrainingWeekData?
  @State private var isLoadingTrainingWeek: Bool = true
  @State private var showProfile: Bool = false
  @State private var weeklySummaries: [WeekSummary]?

  var body: some View {
    NavigationView {
      ZStack {
        VStack {
          DashboardNavbar(onLogout: handleLogout, showProfile: $showProfile)
            .background(ColorTheme.black)
            .zIndex(1)

          ScrollView {
            if isLoadingTrainingWeek {
              DashboardSkeletonView()
            } else if let data = trainingWeekData, let summaries = weeklySummaries {
              TrainingWeekView(trainingWeekData: data, weeklySummaries: summaries)
            } else {
              Text("No training data available")
                .font(.headline)
                .foregroundColor(ColorTheme.lightGrey)
            }
          }
        }
        .background(ColorTheme.black.edgesIgnoringSafeArea(.all))
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
    }
    .onAppear(perform: fetchData)
  }

  private func handleLogout() {
    appState.isLoggedIn = false
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
  }

  private func fetchData() {
    isLoadingTrainingWeek = true
    fetchWeeklySummaries()
    fetchTrainingWeekData()
  }

  private func fetchTrainingWeekData() {
    guard let token = appState.jwtToken else {
      isLoadingTrainingWeek = false
      return
    }

    APIManager.shared.fetchTrainingWeekData(token: token) { result in
      DispatchQueue.main.async {
        switch result {
        case .success(let trainingWeek):
          self.trainingWeekData = trainingWeek
        case .failure(let error):
          print("Error fetching training data: \(error)")
          self.trainingWeekData = nil
        }
        self.checkLoadingComplete()
      }
    }
  }

  private func fetchWeeklySummaries() {
    guard let token = appState.jwtToken else {
      isLoadingTrainingWeek = false
      return
    }
    APIManager.shared.fetchWeeklySummaries(token: token) { result in
      DispatchQueue.main.async {
        switch result {
        case .success(let summaries):
          self.weeklySummaries = summaries
        case .failure(let error):
          print("Error fetching weekly summaries: \(error)")
          self.weeklySummaries = []
        }
        self.checkLoadingComplete()
      }
    }
  }

  private func checkLoadingComplete() {
    if trainingWeekData != nil && weeklySummaries != nil {
      isLoadingTrainingWeek = false
    }
  }
}
