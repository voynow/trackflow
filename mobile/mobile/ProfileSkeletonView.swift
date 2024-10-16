//
//  ProfileSkeletonView.swift
//  mobile
//
//  Created by jamie voynow on 10/16/24.
//

import SwiftUI

struct ProfileSkeletonView: View {
  var body: some View {
    ScrollView {
      VStack {
        // Profile Header Skeleton
        HStack(spacing: 16) {
          Circle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 70, height: 70)

          VStack(alignment: .leading, spacing: 8) {
            Rectangle()
              .fill(ColorTheme.darkGrey)
              .frame(width: 150, height: 20)
            Rectangle()
              .fill(ColorTheme.darkGrey)
              .frame(width: 120, height: 16)
            Rectangle()
              .fill(ColorTheme.darkGrey)
              .frame(width: 80, height: 12)
          }
          Spacer()
        }
        .padding()
        .background(ColorTheme.darkDarkGrey)
        .cornerRadius(12)

        // Preferences Skeleton
        VStack(alignment: .leading, spacing: 24) {
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 100, height: 24)

          ForEach(0..<10) { _ in
            Rectangle()
              .fill(ColorTheme.darkGrey)
              .frame(width: .infinity, height: 16)
          }
        }
        .padding()
        .background(ColorTheme.darkDarkGrey)
        .cornerRadius(12)
      }
      .padding()
    }
    .profileShimmering()
  }
}

extension View {
  func profileShimmering() -> some View {
    self.modifier(ProfileShimmeringEffect())
  }
}

struct ProfileShimmeringEffect: ViewModifier {
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
  ProfileSkeletonView()
    .background(ColorTheme.black)
}
