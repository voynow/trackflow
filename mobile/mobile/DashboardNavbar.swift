import SwiftUI

struct DashboardNavbar: View {
  var onLogout: () -> Void
  @Binding var showProfile: Bool

  var body: some View {
    HStack {
      Button(action: {
        showProfile = false
      }) {
        Text("Crush ")
          .font(.system(size: 28, weight: .black))
          .foregroundColor(ColorTheme.primaryLight)
          + Text("Your Race")
          .font(.system(size: 28, weight: .black))
          .foregroundColor(ColorTheme.primary)
      }
      .buttonStyle(PlainButtonStyle())

      Spacer()

      Button(action: {
        showProfile = true
      }) {
        Image(systemName: "person.crop.circle.fill")
          .resizable()
          .scaledToFit()
          .frame(width: 32, height: 32)
          .foregroundColor(ColorTheme.white)
          .padding(6)
          .background(ColorTheme.black.opacity(0.8))
          .clipShape(Circle())
      }
      .buttonStyle(PlainButtonStyle())
    }
    .background(ColorTheme.black)
    .padding(.horizontal)
  }
}
