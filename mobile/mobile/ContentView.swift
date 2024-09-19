import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var authManager: StravaAuthManager

    init(appState: AppState) {
        _authManager = StateObject(wrappedValue: StravaAuthManager(appState: appState))
    }

    var body: some View {
        ZStack {
            if appState.isLoggedIn {
                DashboardView()
            } else {
                LandingPageView(authManager: authManager)
            }
            
            if appState.isLoading {
                LoadingView()
            }
        }
    }
}

struct IsLoadingView: View {
    var body: some View {
        ColorTheme.bg0
            .edgesIgnoringSafeArea(.all)
    
        ProgressView("Loading...")
            .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.t0))
            .padding(20)
            .background(ColorTheme.bg0)
            .cornerRadius(10)
    }
}

struct ContentView_Previews: PreviewProvider {
  @StateObject private var appState = AppState()
  
    static var previews: some View {
        ContentView(appState: AppState()).environmentObject(AppState())
    }
}
