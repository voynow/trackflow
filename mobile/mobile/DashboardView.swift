import Foundation
import SwiftUI

struct DashboardView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingWeekData: TrainingWeekData?
  @State private var profileData: ProfileData?
  @State private var isLoadingProfile: Bool = true
  @State private var isLoadingTrainingWeek: Bool = true

  var body: some View {
    NavigationView {
      ZStack(alignment: .top) {
        ColorTheme.white.edgesIgnoringSafeArea(.all)

        VStack(spacing: 0) {
          DashboardNavbar(onLogout: handleLogout)

          ScrollView {
            VStack(spacing: 20) {
              if isLoadingProfile || isLoadingTrainingWeek {
                LoadingView()
              }

              if let profile = profileData {
                ProfileView(data: profile)
              } else if !isLoadingProfile {
                Text("Error loading profile data")
              }

              if let data = trainingWeekData {
                TrainingWeekView(data: data)
              } else if !isLoadingTrainingWeek {
                Text("No training data available")
                  .font(.headline)
                  .foregroundColor(ColorTheme.darkGrey)
              }
            }
            .padding()
          }
        }
      }
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
      isLoadingProfile = false
      isLoadingTrainingWeek = false
      return
    }

    // Fetch profile data
    APIManager.shared.fetchProfileData(token: token) { result in
      DispatchQueue.main.async {
        self.isLoadingProfile = false
        switch result {
        case .success(let profile):
          self.profileData = profile
        case .failure(let error):
          print("Error fetching profile data: \(error)")
        }
      }
    }

    // Fetch training week data
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
