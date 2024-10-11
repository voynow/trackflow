import SwiftUI

struct DashboardNavbar: View {
  @State private var isDropdownOpen: Bool = false
  var onLogout: () -> Void

  var body: some View {
    VStack(spacing: 0) {
      HStack {
        Text("Track")
          .font(.title)
          .fontWeight(.semibold)
          .foregroundColor(ColorTheme.superDarkGrey)
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
            .foregroundColor(ColorTheme.superDarkGrey)
        }
      }
      .padding()
    }
    .background(ColorTheme.lightLightGrey)
  }
}
