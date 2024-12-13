import SwiftUI

struct RaceDetailsWidgetSkeleton: View {
    let weeksCount: Int
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .firstTextBaseline) {
                Text("\(weeksCount)")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(ColorTheme.lightGrey)
                Text("Weeks Out From Race Day")
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(ColorTheme.white)
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
    }
}
