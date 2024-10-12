import SwiftUI

struct DashboardView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingWeekData: TrainingWeekData?
  @State private var isLoadingTrainingWeek: Bool = true

  var body: some View {
    NavigationView {
      VStack(spacing: 0) {
        DashboardNavbar(onLogout: handleLogout)
          .background(ColorTheme.superDarkGrey)
          .zIndex(1)

        ScrollView {
          if isLoadingTrainingWeek {
            LoadingView()
          } else if let data = trainingWeekData {
            TrainingWeekView(data: data)
          } else {
            Text("No training data available")
              .font(.headline)
              .foregroundColor(ColorTheme.lightGrey)
          }
        }
      }
      .background(ColorTheme.superDarkGrey.edgesIgnoringSafeArea(.all))
      .navigationBarHidden(true)
    }
    .onAppear(perform: fetchData)
  }

  private func handleLogout() {
    appState.isLoggedIn = false
    appState.jwtToken = nil
    UserDefaults.standard.removeObject(forKey: "jwt_token")
  }

  private func fetchData() {
    guard let token = appState.jwtToken else {
      isLoadingTrainingWeek = false
      return
    }

    APIManager.shared.fetchTrainingWeekData(token: token) { result in
      DispatchQueue.main.async {
        self.isLoadingTrainingWeek = false
        switch result {
        case .success(let trainingWeek):
          self.trainingWeekData = trainingWeek
        case .failure(let error):
          print("Error fetching training data: \(error)")
        }
      }
    }
  }
}
