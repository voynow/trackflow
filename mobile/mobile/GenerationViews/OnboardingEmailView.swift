import SwiftUI

struct OnboardingEmailView: View {
  @Binding var email: String
  @State private var isValid: Bool = true
  let onSubmit: (String) -> Void

  var body: some View {
    VStack(spacing: 40) {
      Spacer()

      VStack(spacing: 32) {

        VStack(spacing: 16) {
          Spacer()
            .frame(height: 20)
          HStack(spacing: 0) {
            Text("Crush ")
              .font(.system(size: 40, weight: .black))
              .foregroundColor(ColorTheme.primaryLight)
            Text("Your Race")
              .font(.system(size: 40, weight: .black))
              .foregroundColor(ColorTheme.primary)
          }
        }
        // Email input section
        VStack(spacing: 24) {
          Text("Welcome! Let's get started")
            .font(.system(size: 18))
            .foregroundColor(ColorTheme.lightGrey)
          VStack(spacing: 8) {
            TextField("Enter your email", text: $email)
              .textFieldStyle(PlainTextFieldStyle())
              .keyboardType(.emailAddress)
              .autocapitalization(.none)
              .padding()
              .background(ColorTheme.darkDarkGrey)
              .cornerRadius(12)
              .overlay(
                RoundedRectangle(cornerRadius: 12)
                  .stroke(isValid ? ColorTheme.primary : ColorTheme.redPink, lineWidth: 1)
              )
            if !isValid {
              Text("Please enter a valid email")
                .foregroundColor(ColorTheme.redPink)
                .font(.system(size: 14))
                .transition(.opacity)
            }
          }
          Button(action: {
            if isValidEmail(email) {
              isValid = true
              onSubmit(email)
            } else {
              withAnimation {
                isValid = false
              }
            }
          }) {
            Text("Continue")
              .font(.system(size: 18, weight: .semibold))
              .foregroundColor(ColorTheme.white)
              .frame(maxWidth: .infinity)
              .padding()
              .background(ColorTheme.primary)
              .cornerRadius(12)
              .shadow(color: ColorTheme.primary.opacity(0.3), radius: 8, x: 0, y: 4)
          }
          .disabled(email.isEmpty)
          .opacity(email.isEmpty ? 0.6 : 1)
        }
      }
      .padding(32)
      Spacer()
    }
    .background(
      LinearGradient(
        gradient: Gradient(colors: [ColorTheme.black, ColorTheme.darkDarkGrey]),
        startPoint: .top,
        endPoint: .bottom
      )
    )
    .ignoresSafeArea()
  }

  private func isValidEmail(_ email: String) -> Bool {
    let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
    let emailPred = NSPredicate(format: "SELF MATCHES %@", emailRegEx)
    return emailPred.evaluate(with: email)
  }
}
