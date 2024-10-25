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
              InitialLoadingView(onGeneratePlan: generateInitialTrainingPlan)
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
    .alert(isPresented: $showErrorAlert) {
      Alert(
        title: Text("Error"),
        message: Text(errorMessage),
        dismissButton: .default(Text("OK"))
      )
    }
  }

  private func handleLogout() {
    appState.isLoggedIn = false
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

  private func generateInitialTrainingPlan() {
    guard let token = appState.jwtToken else { return }
    
    isLoadingTrainingWeek = true
    APIManager.shared.generateInitialTrainingPlan(token: token) { result in
      DispatchQueue.main.async {
        self.isLoadingTrainingWeek = false
        switch result {
        case .success:
          self.fetchData()
        case .failure(let error):
          print("Error generating initial training plan: \(error)")
          self.showErrorAlert(message: "Failed to generate initial training plan. Please try again.")
        }
      }
    }
  }

  private func showErrorAlert(message: String) {
    self.errorMessage = message
    self.showErrorAlert = true
  }
}


struct InitialLoadingView: View {
  let onGeneratePlan: () -> Void
  @State private var isGenerating: Bool = false
  @State private var progress: Double = 0
  
  var body: some View {
    VStack(spacing: 40) {
      Text("Welcome to TrackFlow")
        .font(.system(size: 28, weight: .bold))
        .foregroundColor(ColorTheme.white)
      
      Text("We're creating your personalized training plan")
        .font(.system(size: 18))
        .foregroundColor(ColorTheme.lightGrey)
        .multilineTextAlignment(.center)
      
      ZStack {
        Circle()
          .stroke(lineWidth: 8.0)
          .opacity(0.3)
          .foregroundColor(ColorTheme.primary)
        
        Circle()
          .trim(from: 0.0, to: CGFloat(min(self.progress, 1.0)))
          .stroke(style: StrokeStyle(lineWidth: 8.0, lineCap: .round, lineJoin: .round))
          .foregroundColor(ColorTheme.primary)
          .rotationEffect(Angle(degrees: 270.0))
          .animation(.linear(duration: 1.0), value: progress)

        Text("\(Int(progress * 100))%")
          .font(.system(size: 24, weight: .bold))
          .foregroundColor(ColorTheme.white)
      }
      .frame(width: 150, height: 150)
      
      Text("This may take a few moments")
        .font(.system(size: 16))
        .foregroundColor(ColorTheme.midLightGrey)
    }
    .padding()
    .frame(maxWidth: .infinity, maxHeight: .infinity)
    .background(ColorTheme.black)
    .onAppear {
      startGeneratingPlan()
    }
  }
  
  private func startGeneratingPlan() {
    isGenerating = true
    onGeneratePlan()
    
    // Simulate progress
    Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { timer in
      if self.progress < 1.0 {
        self.progress += 0.1
      } else {
        timer.invalidate()
      }
    }
  }
}
