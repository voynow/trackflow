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
      VStack(spacing: 24) {
        // Profile Header Skeleton
        profileHeaderSkeleton
        
        // Preferences Container Skeleton
        VStack(spacing: 24) {
          // Race Details Section
          preferenceSectionSkeleton(rowCount: 1)
          
          // Ideal Training Week Section
          preferenceSectionSkeleton(rowCount: 7)
          
          // Sign Out Button Skeleton
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(height: 50)
            .cornerRadius(12)
        }
        .padding(.horizontal)
      }
      .padding(.top, 16)
    }
    .profileShimmering()
  }
  
  private var profileHeaderSkeleton: some View {
    HStack(spacing: 16) {
      Circle()
        .fill(ColorTheme.darkGrey)
        .frame(width: 80, height: 80)
      
      VStack(alignment: .leading, spacing: 8) {
        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 150, height: 24)
        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 120, height: 14)
        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(width: 100, height: 14)
      }
      Spacer()
    }
    .padding(24)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(20)
    .padding(.horizontal)
  }
  
  private func preferenceSectionSkeleton(rowCount: Int) -> some View {
    VStack(alignment: .leading, spacing: 16) {
      Rectangle()
        .fill(ColorTheme.darkGrey)
        .frame(width: 120, height: 20)
      
      ForEach(0..<rowCount, id: \.self) { _ in
        HStack {
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 100, height: 16)
          Spacer()
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 80, height: 16)
        }
      }
    }
    .padding(24)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
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
