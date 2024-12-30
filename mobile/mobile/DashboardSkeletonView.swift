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
  }
}

struct WeeklyProgressSkeletonView: View {
  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      Rectangle()
        .fill(ColorTheme.darkGrey.opacity(0.3))
        .frame(width: 120, height: 20)

      HStack {
        Rectangle()
          .fill(ColorTheme.darkGrey.opacity(0.3))
          .frame(width: 80, height: 40)

        Spacer()

        Rectangle()
          .fill(ColorTheme.darkGrey.opacity(0.3))
          .frame(width: 150, height: 20)
      }

      Rectangle()
        .fill(ColorTheme.darkGrey.opacity(0.3))
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
          .fill(ColorTheme.darkGrey.opacity(0.3))
          .frame(width: 40, height: 20)

        VStack(alignment: .leading, spacing: 4) {
          Rectangle()
            .fill(ColorTheme.darkGrey.opacity(0.3))
            .frame(width: 120, height: 18)
          Rectangle()
            .fill(ColorTheme.darkGrey.opacity(0.3))
            .frame(width: 80, height: 14)
        }

        Spacer()

        Circle()
          .fill(ColorTheme.darkGrey.opacity(0.3))
          .frame(width: 16, height: 16)
      }
    }
    .padding(.horizontal, 30)
    .padding(.vertical, 20)
    .overlay(
      RoundedRectangle(cornerRadius: 12).stroke(ColorTheme.darkGrey.opacity(0.3), lineWidth: 1)
    )
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}

#Preview {
  DashboardSkeletonView()
    .background(ColorTheme.black)
}
