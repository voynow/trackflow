import SwiftUI

struct DashboardNavbar: View {
  var onLogout: () -> Void
  @Binding var showProfile: Bool

  var body: some View {
    HStack {
      Text("Track")
        .font(.system(size: 24, weight: .black))
        .foregroundColor(ColorTheme.primaryLight)
        + Text("Flow")
        .font(.system(size: 24, weight: .black))
        .foregroundColor(ColorTheme.primary)

      Spacer()

      Button(action: {
        showProfile.toggle()
      }) {
        Image(systemName: "person.circle")
          .resizable()
          .frame(width: 30, height: 30)
          .foregroundColor(ColorTheme.white)
      }
    }
    .padding()
    .background(ColorTheme.superDarkGrey)
    .cornerRadius(12)
  }
}
