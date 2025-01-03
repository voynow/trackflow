import SwiftUI

struct LoadingView: View {
  @State private var showWaitMessage: Bool = false
  var loadingText: String = "Loading..."
  var showError: Bool = false
  var errorMessage: String = "An error occurred"

  var body: some View {
    ZStack {
      ColorTheme.black
        .edgesIgnoringSafeArea(.all)

      VStack(spacing: 40) {
        brandingView

        VStack(spacing: 30) {
          ProgressView()
            .scaleEffect(1.5)
            .progressViewStyle(CircularProgressViewStyle(tint: ColorTheme.primary))

          Text(loadingText)
            .font(.system(size: 16, weight: .light, design: .monospaced))
            .foregroundColor(ColorTheme.primaryLight)

          if showError {
            Text(errorMessage)
              .font(.system(size: 14, weight: .regular, design: .monospaced))
              .foregroundColor(ColorTheme.indigo)
              .multilineTextAlignment(.center)
              .padding()
          }
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

  private var brandingView: some View {
    VStack(spacing: 16) {
      Spacer()
        .frame(height: 20)
      HStack(spacing: 0) {
        Text("Crush ")
          .font(.system(size: 40, weight: .black))
          .foregroundColor(ColorTheme.primaryLight)
        Text("Your Race")
          .font(.system(size: 40, weight: .black))
          .foregroundColor(ColorTheme.primary)
      }

      Text("Step into the Next Generation of Training")
        .font(.system(size: 16, weight: .light))
        .foregroundColor(ColorTheme.lightGrey)
        .multilineTextAlignment(.center)
    }
  }
}
