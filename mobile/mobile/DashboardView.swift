// mobile/DashboardView.swift
import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var appState: AppState
    @State private var trainingWeekData: TrainingWeekData?
    @State private var isLoading: Bool = true
    
    var body: some View {
        NavigationView {
            ZStack(alignment: .top) {
                ColorTheme.bg0.edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 0) {
                    DashboardNavbar(onLogout: handleLogout)
                    
                    ScrollView {
                        VStack {
                            if isLoading {
                                LoadingView()
                            } else if let data = trainingWeekData {
                                TrainingWeek(data: data)
                            } else {
                                Text("No training data available")
                                    .font(.headline)
                                    .foregroundColor(ColorTheme.t1)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationBarHidden(true)
        }
        .onAppear(perform: fetchTrainingWeekData)
    }
    
    private func handleLogout() {
        appState.isLoggedIn = false
        appState.jwtToken = nil
        UserDefaults.standard.removeObject(forKey: "jwt_token")
    }
    
    private func fetchTrainingWeekData() {
        guard let token = appState.jwtToken else {
            isLoading = false
            return
        }
        
        let url = URL(string: "https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "jwt_token": token,
            "method": "get_training_week"
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            DispatchQueue.main.async {
                self.isLoading = false
                
                if let error = error {
                    print("Error fetching training data:", error)
                    return
                }
                
                guard let data = data else {
                    print("No data received")
                    return
                }
                
                do {
                    if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                       let success = json["success"] as? Bool,
                       success,
                       let trainingWeekString = json["training_week"] as? String,
                       let trainingWeekData = trainingWeekString.data(using: .utf8) {
                        
                        let decoder = JSONDecoder()
                        let parsedData = try decoder.decode(TrainingWeekData.self, from: trainingWeekData)
                        self.trainingWeekData = parsedData
                    } else {
                        print("Invalid response format")
                    }
                } catch {
                    print("Error parsing response:", error)
                }
            }
        }.resume()
    }
}
