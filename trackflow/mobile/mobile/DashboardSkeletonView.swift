//
//  DashboardSkeletonView.swift
//  mobile
//
//  Created by jamie voynow on 10/16/24.
//

import SwiftUI

struct DashboardSkeletonView: View {
  var body: some View {
    VStack(spacing: 16) {
      WeeklyProgressSkeletonView()
      SessionListSkeletonView()
    }
    .padding(20)
    .background(ColorTheme.black)
    .cornerRadius(16)
    .dashboardShimmering()
  }
}

struct WeeklyProgressSkeletonView: View {
  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      Rectangle()
        .fill(ColorTheme.darkGrey)
        .frame(width: 120, height: 20)

      HStack {
        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 80, height: 40)

        Spacer()

        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 150, height: 20)
      }

      Rectangle()
        .fill(ColorTheme.darkGrey)
        .frame(height: 10)
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(16)
  }
}

struct SessionListSkeletonView: View {
  var body: some View {
    VStack(spacing: 24) {
      ForEach(0..<5) { _ in
        SessionSkeletonView()
      }
    }
  }
}

struct SessionSkeletonView: View {
  var body: some View {
    VStack(alignment: .leading, spacing: 24) {
      HStack(alignment: .center, spacing: 16) {
        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 40, height: 20)

        VStack(alignment: .leading, spacing: 4) {
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 120, height: 18)
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 80, height: 14)
        }

        Spacer()

        Circle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 16, height: 16)
      }
    }
    .padding(.horizontal, 30)
    .padding(.vertical, 20)
    .overlay(RoundedRectangle(cornerRadius: 12).stroke(ColorTheme.darkGrey, lineWidth: 1))
    .background(ColorTheme.black)
    .cornerRadius(12)
  }
}

extension View {
  func dashboardShimmering() -> some View {
    self.modifier(DashboardShimmeringEffect())
  }
}

struct DashboardShimmeringEffect: ViewModifier {
  @State private var phase: CGFloat = 0

  func body(content: Content) -> some View {
    content
      .overlay(
        GeometryReader { geometry in
          LinearGradient(
            gradient: Gradient(colors: [
              .clear,
              Color.white.opacity(0.1),
              .clear,
            ]),
            startPoint: .leading,
            endPoint: .trailing
          )
          .frame(width: geometry.size.width * 3)
          .offset(x: -geometry.size.width + (geometry.size.width * 3) * phase)
          .animation(
            Animation.linear(duration: 1.5)
              .repeatForever(autoreverses: false),
            value: phase
          )
        }
      )
      .onAppear {
        phase = 1
      }
      .mask(content)
  }
}

#Preview {
  DashboardSkeletonView()
    .background(ColorTheme.black)
}
