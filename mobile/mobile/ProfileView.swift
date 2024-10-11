import SwiftUI

struct ProfileView: View {
  let data: ProfileData

  var body: some View {
    HStack(spacing: 16) {
      AsyncImage(url: URL(string: data.profile)) { image in
        image.resizable()
      } placeholder: {
        Color.gray.opacity(0.3)
      }
      .frame(width: 70, height: 70)
      .clipShape(Circle())

      VStack(alignment: .leading, spacing: 6) {
        Text("\(data.firstname) \(data.lastname)")
          .font(.system(size: 18, weight: .semibold))
          .foregroundColor(ColorTheme.superDarkGrey)

        Text(data.email)
          .font(.system(size: 14))
          .foregroundColor(ColorTheme.darkGrey)

        HStack(spacing: 6) {
          Circle()
            .fill(data.isActive ? Color.green : Color.red)
            .frame(width: 8, height: 8)

          Text(data.isActive ? "Active" : "Inactive")
            .font(.system(size: 12))
            .foregroundColor(ColorTheme.darkGrey)
        }
      }
    }
    .padding(.vertical, 16)
    .cornerRadius(12)
  }
}
