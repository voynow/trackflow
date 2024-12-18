import SwiftUI
import Combine

struct WaitingForGenerationView: View {
  @State private var progress: Double = 0
  @State private var currentStage: Int = 0
  @State private var showExtendedWaitMessage: Bool = false
  @State private var timer: Timer.TimerPublisher = Timer.publish(every: 0.25, on: .main, in: .common)
  @State private var timerCancellable: AnyCancellable?

  let stages: [String]
  let title: String
  let subtitle: String
  let onComplete: () -> Void

  var calculatedProgressIncrement: Double {
    return 0.01  // 1% per tick, 100 ticks total
  }

  var body: some View {
    GeometryReader { geometry in
      ZStack {
        ColorTheme.black.edgesIgnoringSafeArea(.all)

        VStack(spacing: 20) {
          Spacer()

          Text(title)
            .font(.system(size: 28, weight: .bold))
            .foregroundColor(ColorTheme.white)

          Text(subtitle)
            .font(.system(size: 16, weight: .light))
            .foregroundColor(ColorTheme.lightGrey)
            .multilineTextAlignment(.center)

          Spacer()

          Text(stages[currentStage])
            .font(.system(size: 18, weight: .bold))
            .foregroundColor(ColorTheme.primaryLight)
            .transition(.opacity)
            .id(currentStage)
            .multilineTextAlignment(.center)

          ProgressView(value: progress)
            .progressViewStyle(LinearProgressViewStyle(tint: ColorTheme.primary))
            .frame(height: 4)

          Spacer()
        }
        .padding(.horizontal, 40)
      }
    }
    .onAppear {
      timerCancellable = AnyCancellable(timer.connect())
    }
    .onDisappear {
      timerCancellable?.cancel()
    }
    .onReceive(timer) { _ in
      updateProgress()
    }
  }

  private func updateProgress() {
    if progress < 1.0 {
      progress = min(progress + calculatedProgressIncrement, 1.0)
      let newStage = min(Int(progress * Double(stages.count)), stages.count - 1)
      if newStage != currentStage {
        withAnimation(.easeInOut(duration: 0.5)) {
          currentStage = newStage
        }
      }
    } else if progress >= 1.0 {
      timerCancellable?.cancel()
      onComplete()
    }
  }
}
