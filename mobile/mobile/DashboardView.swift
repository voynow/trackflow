import SwiftUI

struct DashboardView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingWeekData: TrainingWeekData?
  @State private var isLoadingTrainingWeek: Bool = true
  @State private var showProfile: Bool = false
  @State private var weeklySummaries: [WeekSummary]?
  @State private var showOnboarding: Bool = false
  @State private var showErrorAlert: Bool = false
  @State private var errorMessage: String = ""

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
              Button(action: handleLogout) {
                Text("Logout")
              }
            }
          }
          .refreshable {
            fetchData()
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
    .alert(isPresented: $showErrorAlert) {
      Alert(
        title: Text("Error"),
        message: Text(errorMessage),
        dismissButton: .default(Text("OK"))
      )
    }
  }

  private func handleLogout() {
    appState.status = .loggedOut
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
  }

  private func fetchData() {
    isLoadingTrainingWeek = true
    let group = DispatchGroup()

    group.enter()
    fetchWeeklySummaries {
      group.leave()
    }

    group.enter()
    fetchTrainingWeekData {
      group.leave()
    }

    group.notify(queue: .main) {
      self.isLoadingTrainingWeek = false
    }
  }

  private func fetchTrainingWeekData(completion: @escaping () -> Void) {
    guard let token = appState.jwtToken else {
      completion()
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
        completion()
      }
    }
  }

  private func fetchWeeklySummaries(completion: @escaping () -> Void) {
    guard let token = appState.jwtToken else {
      completion()
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
        completion()
      }
    }
  }

  private func checkLoadingComplete() {
    if trainingWeekData != nil && weeklySummaries != nil {
      isLoadingTrainingWeek = false
    }
  }

  private func showErrorAlert(message: String) {
    self.errorMessage = message
    self.showErrorAlert = true
  }
}
