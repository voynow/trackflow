import SwiftUI
import Charts

struct TrainingPlanView: View {
    @EnvironmentObject var appState: AppState
    @State private var trainingPlan: TrainingPlan?
    @State private var isLoading = true
    @State private var errorMessage: String?

    var body: some View {
        ZStack {
            ColorTheme.black.edgesIgnoringSafeArea(.all)
            
            if isLoading {
                ProgressView("Loading training plan...")
                    .foregroundColor(ColorTheme.lightGrey)
            } else if let plan = trainingPlan {
                ScrollView {
                    VStack(spacing: 16) {
                        TrainingPlanChart(trainingWeeks: plan.trainingWeekPlans)
                        TrainingStatsWidget(trainingWeeks: plan.trainingWeekPlans)
                    }
                    .padding()
                }
            } else if let error = errorMessage {
                Text("Error: \(error)")
                    .foregroundColor(.red)
            }
        }
        .onAppear {
            fetchTrainingPlanData()
        }
        .navigationTitle("Training Plan")
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
}

struct TrainingPlanChart: View {
    let trainingWeeks: [TrainingPlanWeek]

    var body: some View {
        Chart {
            ForEach(trainingWeeks) { week in
                LineMark(
                    x: .value("Week", week.weekNumber),
                    y: .value("Total Distance", week.totalDistance)
                )
                .foregroundStyle(ColorTheme.primary)
                
                LineMark(
                    x: .value("Week", week.weekNumber),
                    y: .value("Long Run Distance", week.longRunDistance)
                )
                .foregroundStyle(ColorTheme.redPink)
            }
        }
        .frame(height: 200)
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
                Text("Total Mileage")
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
                Text("Average Long Run")
                    .font(.headline)
                    .foregroundColor(ColorTheme.lightGrey)
                Text("\(trainingWeeks.reduce(0) { $0 + $1.longRunDistance } / Double(trainingWeeks.count), specifier: "%.1f") miles")
                    .font(.title)
                    .foregroundColor(ColorTheme.redPink)
            }
            .padding()
            .background(ColorTheme.darkDarkGrey)
            .cornerRadius(12)
        }
    }
}
