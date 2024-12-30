import SwiftUI

struct ProfileSkeletonView: View {
  var body: some View {
    VStack(spacing: 24) {
      // Profile Info Card
      VStack(alignment: .leading, spacing: 16) {
        HStack(spacing: 16) {
          Circle()
            .foregroundColor(ColorTheme.darkGrey.opacity(0.3))
            .frame(width: 80, height: 80)
          
          VStack(alignment: .leading, spacing: 4) {
            Rectangle()
              .foregroundColor(ColorTheme.darkGrey.opacity(0.3))
              .frame(width: 180, height: 24)
              .cornerRadius(4)
            Rectangle()
              .foregroundColor(ColorTheme.darkGrey.opacity(0.3))
              .frame(width: 140, height: 14)
              .cornerRadius(4)
            Rectangle()
              .foregroundColor(ColorTheme.darkGrey.opacity(0.3))
              .frame(width: 120, height: 14)
              .cornerRadius(4)
          }
          Spacer()
        }
      }
      .padding(.vertical, 24)
      .padding(.horizontal, 36)
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(20)
      
      VStack(spacing: 24) {
        skeletonSection(rowCount: 2)
        skeletonSection(rowCount: 7)
        
        Rectangle()
          .foregroundColor(ColorTheme.darkGrey.opacity(0.3))
          .frame(height: 50)
          .cornerRadius(12)
      }
    }
    .padding()
    .frame(maxHeight: .infinity, alignment: .top)
  }
  
  private func skeletonSection(rowCount: Int) -> some View {
    VStack(alignment: .leading, spacing: 16) {
      ForEach(0..<rowCount, id: \.self) { _ in
        Rectangle()
          .foregroundColor(ColorTheme.darkGrey.opacity(0.3))
          .frame(height: 16)
          .cornerRadius(4)
      }
    }
    .padding(24)
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}