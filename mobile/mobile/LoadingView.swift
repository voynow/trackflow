import SwiftUI

struct LoadingView: View {
    @State private var showWaitMessage: Bool = false
    var loadingText: String = "Loading..."
    var showError: Bool = false
    var errorMessage: String = "An error occurred"
    
    var body: some View {
        ZStack {
            ColorTheme.bg0
                .edgesIgnoringSafeArea(.all)
            
            VStack(spacing: 20) {
                ProgressView()
                    .scaleEffect(2.0)
                    .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.t0))
                
                Text(loadingText)
                    .font(.caption)
                    .foregroundColor(ColorTheme.t1)
                
                if showError {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(ColorTheme.t1)
                        .multilineTextAlignment(.center)
                        .padding()
                }
            }
            .padding()
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 10) {
                showWaitMessage = true
            }
        }
    }
}
