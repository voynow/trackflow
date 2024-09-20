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
          .foregroundColor(ColorTheme.t0)
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
            .foregroundColor(ColorTheme.t0)
        }
      }
      .padding()
    }
    .background(ColorTheme.bg1)
  }
}
