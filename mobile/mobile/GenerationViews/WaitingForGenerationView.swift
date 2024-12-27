import SwiftUI

struct WaitingForGenerationView: View {
  let onComplete: (() -> Void)?
  @State private var animationPhase = 0
  @State private var showOnboarding: Bool = false

  init(onComplete: (() -> Void)? = nil) {
    self.onComplete = onComplete
  }

  var body: some View {
    ZStack {
      ColorTheme.black.edgesIgnoringSafeArea(.all)

      // Centered content
      VStack(spacing: 40) {
        Spacer()

        Text("Track")
          .font(.system(size: 28, weight: .black))
          .foregroundColor(ColorTheme.primaryLight)
          + Text("Flow")
          .font(.system(size: 28, weight: .black))
          .foregroundColor(ColorTheme.primary)

        VStack(spacing: 10) {
          Text("We're generating your recommendations")
            .font(.system(size: 16, weight: .bold))
            .foregroundColor(ColorTheme.lightGrey)
            .multilineTextAlignment(.center)

          Text(
            "This typically takes 20-30 seconds but can take as long as one minute. Thank you for your patience!"
          )
          .font(.system(size: 14, weight: .light))
          .foregroundColor(ColorTheme.lightGrey)
          .multilineTextAlignment(.center)
        }

        // AI Thinking Animation
        VStack(spacing: 8) {
          HStack(spacing: 12) {
            ForEach(0..<3) { index in
              Circle()
                .fill(ColorTheme.primary)
                .frame(width: 12, height: 12)
                .scaleEffect(animationPhase == index ? 1.5 : 1.0)
                .opacity(animationPhase == index ? 1 : 0.5)
                .animation(.easeInOut(duration: 0.5), value: animationPhase)
            }
          }
        }
        .padding(.top, 20)

        Spacer()
      }
      .padding(.horizontal, 40)

      VStack {
        Spacer()
        Button(action: { showOnboarding = true }) {
          Text("About TrackFlow")
            .font(.system(size: 16, weight: .medium))
            .foregroundColor(ColorTheme.midLightGrey2)
            .padding(.vertical, 16)
            .frame(maxWidth: .infinity)
            .overlay(
              Rectangle()
                .frame(height: 1)
                .foregroundColor(ColorTheme.darkGrey),
              alignment: .top
            )
            .background(ColorTheme.black)
        }
        .padding(.bottom, 16)
      }
      .edgesIgnoringSafeArea(.bottom)
    }
    .fullScreenCover(isPresented: $showOnboarding) {
      OnboardingCarousel(showCloseButton: true)
    }
    .onAppear {
      withAnimation {
        startAnimation()
      }

      DispatchQueue.main.asyncAfter(deadline: .now() + 25) {
        onComplete?()
      }
    }
  }

  private func startAnimation() {
    Timer.scheduledTimer(withTimeInterval: 0.6, repeats: true) { timer in
      withAnimation {
        animationPhase = (animationPhase + 1) % 3
      }
    }
  }
}
