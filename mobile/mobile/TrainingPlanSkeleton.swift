import SwiftUI

struct TrainingPlanSkeleton: View {
  var body: some View {
    VStack(spacing: 16) {
      // Race Details Skeleton
      VStack(alignment: .leading, spacing: 8) {
        HStack(alignment: .firstTextBaseline) {
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 80, height: 48)
            .cornerRadius(4)
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(width: 200, height: 24)
            .cornerRadius(4)
        }
        .padding(.bottom, 16)

        HStack(spacing: 24) {
          VStack(alignment: .leading) {
            Text("Distance")
              .font(.subheadline)
              .foregroundColor(ColorTheme.midLightGrey)
            Rectangle()
              .fill(ColorTheme.darkGrey)
              .frame(width: 100, height: 24)
              .cornerRadius(4)
          }

          VStack(alignment: .leading) {
            Text("Date")
              .font(.subheadline)
              .foregroundColor(ColorTheme.midLightGrey)
            Rectangle()
              .fill(ColorTheme.darkGrey)
              .frame(width: 160, height: 24)
              .cornerRadius(4)
          }
        }
      }
      .padding(16)
      .frame(maxWidth: .infinity, alignment: .leading)
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(12)

      // Training Plan Chart Skeleton
      VStack(alignment: .leading, spacing: 8) {
        Text("Weekly Training Progression")
          .font(.headline)
          .foregroundColor(ColorTheme.lightGrey)
          .padding(.bottom, 8)

        Rectangle()
          .fill(ColorTheme.darkGrey)
          .frame(height: 250)
          .cornerRadius(8)

        VStack(alignment: .leading, spacing: 8) {
          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(height: 24)
            .frame(maxWidth: 200)
            .cornerRadius(4)

          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(height: 20)
            .frame(maxWidth: 150)
            .cornerRadius(4)

          Rectangle()
            .fill(ColorTheme.darkGrey)
            .frame(height: 20)
            .frame(maxWidth: 160)
            .cornerRadius(4)
        }
        .padding(.top, 8)
      }
      .padding(16)
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(12)
    }
    .padding()
  }
}
