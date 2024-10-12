import SwiftUI

struct DashboardNavbar: View {
  var onLogout: () -> Void

  var body: some View {
    HStack {
      Text("Track")
        .font(.title)
        .fontWeight(.semibold)
        .foregroundColor(ColorTheme.white)
      + Text("Flow")
        .font(.title)
        .fontWeight(.semibold)
        .foregroundColor(ColorTheme.primary)

      Spacer()

      Menu {
        Button("Logout", action: onLogout)
      } label: {
        Image(systemName: "person.circle")
          .resizable()
          .frame(width: 30, height: 30)
          .foregroundColor(ColorTheme.white)
      }
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(12)
  }
}
