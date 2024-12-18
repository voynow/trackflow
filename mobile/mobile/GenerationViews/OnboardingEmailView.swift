import SwiftUI

struct OnboardingEmailView: View {
  @Binding var email: String
  @State private var isValid: Bool = true
  let onSubmit: (String) -> Void

  var body: some View {
    VStack(spacing: 32) {
      Spacer()
      
      VStack(spacing: 24) {
        Text("Welcome to TrackFlow!")
          .font(.system(size: 32, weight: .bold))
          .foregroundColor(ColorTheme.white)
        
        Text("Please enter your email to complete setup")
          .font(.system(size: 18))
          .foregroundColor(ColorTheme.lightGrey)
        
        VStack(spacing: 16) {
          TextField("Email", text: $email)
            .textFieldStyle(RoundedBorderTextFieldStyle())
            .keyboardType(.emailAddress)
            .autocapitalization(.none)
            .padding()
            .background(ColorTheme.darkGrey)
            .cornerRadius(12)
            .overlay(
              RoundedRectangle(cornerRadius: 12)
                .stroke(ColorTheme.darkGrey, lineWidth: 1)
            )
          
          if !isValid {
            Text("Please enter a valid email")
              .foregroundColor(ColorTheme.redPink)
              .font(.system(size: 14))
          }
        }
        .padding(.horizontal, 24)
        
        Button(action: {
          if isValidEmail(email) {
            isValid = true
            onSubmit(email)
          } else {
            isValid = false
          }
        }) {
          Text("Continue")
            .font(.system(size: 18, weight: .semibold))
            .foregroundColor(ColorTheme.white)
            .frame(maxWidth: .infinity)
            .padding()
            .background(ColorTheme.primary)
            .cornerRadius(12)
        }
        .padding(.horizontal, 24)
      }
      .padding(32)
      .background(ColorTheme.darkDarkGrey)
      .cornerRadius(20)
      .padding(.horizontal, 24)
      
      Spacer()
    }
  }

  private func isValidEmail(_ email: String) -> Bool {
    let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
    let emailPred = NSPredicate(format: "SELF MATCHES %@", emailRegEx)
    return emailPred.evaluate(with: email)
  }
}
