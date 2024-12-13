import SwiftUI

struct TrainingPlanChartSkeleton: View {
    var body: some View {
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
}
