import SwiftUI

struct OnboardingCarousel: View {
  @Environment(\.dismiss) private var dismiss
  @State private var currentPage: Int = 0
  let showCloseButton: Bool

  let pages: [(image: String, title: String, subtitle: String)] = [
    ("AppDashboard", "Train Smarter", "AI-powered plans that adapt to your progress"),
    ("AppDashboardAlt", "Connect with Strava", "Seamless integration with your activities"),
    ("AppProfile", "Achieve Your Goals", "From 5K to marathon, we've got you covered"),
  ]

  var body: some View {
    ZStack {
      ColorTheme.black.edgesIgnoringSafeArea(.all)

      VStack(spacing: 0) {
        if showCloseButton {
          closeButton
            .padding(.top, 8)
        }

        TabView(selection: $currentPage) {
          ForEach(0..<pages.count, id: \.self) { index in
            OnboardingPage(
              image: pages[index].image,
              title: pages[index].title,
              subtitle: pages[index].subtitle
            )
            .tag(index)
          }
        }
        .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))

        pageControl
          .padding(.bottom, 16)
      }
    }
  }

  private var closeButton: some View {
    HStack {
      Spacer()
      Button(action: { dismiss() }) {
        Image(systemName: "xmark.circle.fill")
          .font(.system(size: 28))
          .foregroundColor(ColorTheme.midLightGrey2)
      }
      .padding(.trailing, 24)
    }
  }

  private var pageControl: some View {
    HStack(spacing: 8) {
      ForEach(0..<pages.count, id: \.self) { index in
        Circle()
          .fill(currentPage == index ? ColorTheme.primary : ColorTheme.darkGrey)
          .frame(width: 8, height: 8)
          .animation(.easeInOut, value: currentPage)
      }
    }
  }
}

struct OnboardingPage: View {
  let image: String
  let title: String
  let subtitle: String

  var body: some View {
    VStack(spacing: 8) {
      Image(image)
        .resizable()
        .aspectRatio(contentMode: .fit)
        .frame(maxHeight: UIScreen.main.bounds.height * 0.65)
        .clipShape(RoundedRectangle(cornerRadius: 24))
        .padding(.horizontal, 16)
        .shadow(
          color: Color.black.opacity(0.12),
          radius: 25,
          x: 0,
          y: 10
        )
        .overlay(
          LinearGradient(
            gradient: Gradient(
              colors: [
                .clear,
                .black.opacity(0.15),
              ]
            ),
            startPoint: .center,
            endPoint: .bottom
          )
          .clipShape(RoundedRectangle(cornerRadius: 24))
        )

      VStack(spacing: 4) {
        Text(title)
          .font(.system(size: 28, weight: .bold))
          .foregroundColor(ColorTheme.white)

        Text(subtitle)
          .font(.system(size: 14))
          .foregroundColor(ColorTheme.lightGrey)
          .multilineTextAlignment(.center)
          .padding(.horizontal)
      }
    }
  }
}
