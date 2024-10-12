import SwiftUI

struct DashboardView: View {
  @EnvironmentObject var appState: AppState
  @State private var trainingWeekData: TrainingWeekData?
  @State private var profileData: ProfileData?
  @State private var isLoadingTrainingWeek: Bool = true
  @State private var isLoadingProfile: Bool = true
  @State private var showProfile: Bool = false

  var body: some View {
    NavigationView {
      ZStack {
        VStack(spacing: 0) {
          DashboardNavbar(onLogout: handleLogout, showProfile: $showProfile)
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

        if showProfile {
          if let profileData = profileData {
            ProfileView(
              isPresented: $showProfile,
              profileData: Binding(
                get: { profileData },
                set: { self.profileData = $0 }
              ),
              showProfile: $showProfile
            )
            .transition(.move(edge: .trailing))
            .zIndex(2)
          } else if isLoadingProfile {
            LoadingView()
              .zIndex(2)
          } else {
            Text("Failed to load profile")
              .foregroundColor(ColorTheme.lightGrey)
              .zIndex(2)
          }
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
    fetchTrainingWeekData()
    fetchProfileData()
  }

  private func fetchTrainingWeekData() {
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

  private func fetchProfileData() {
    guard let token = appState.jwtToken else {
      isLoadingProfile = false
      return
    }

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
  }
}
