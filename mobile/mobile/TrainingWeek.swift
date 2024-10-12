import SwiftUI

struct TrainingWeekView: View {
  let data: TrainingWeekData

  var body: some View {
    VStack(spacing: 24) {
      WeeklyProgressView(sessions: data.sessions)
      SessionListView(sessions: data.sessions)
    }
    .padding(20)
    .background(ColorTheme.superDarkGrey)
    .cornerRadius(16)
  }
}

struct WeeklyProgressView: View {
  let sessions: [TrainingSession]

  private var completedMileage: Double {
    sessions.reduce(0) { $0 + ($1.completed ? $1.distance : 0) }
  }

  private var totalMileage: Double {
    sessions.reduce(0) { $0 + $1.distance }
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      Text("Weekly Progress")
        .font(.headline)
        .foregroundColor(ColorTheme.white)

      HStack {
        Text("\(Int((completedMileage / totalMileage) * 100))%")
          .font(.system(size: 40, weight: .bold))
          .foregroundColor(ColorTheme.white)

        Spacer()

        Text("Completed \(Int(completedMileage)) of \(Int(totalMileage)) mi")
          .font(.subheadline)
          .foregroundColor(ColorTheme.lightGrey)
      }

      ProgressBar(progress: completedMileage / totalMileage)
        .frame(height: 10)
        .animation(.easeOut(duration: 1.0), value: completedMileage)

    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(16)
  }
}

struct ProgressBar: View {
  let progress: Double

  @State private var animatedProgress: CGFloat = 0

  var body: some View {
    GeometryReader { geometry in
      ZStack(alignment: .leading) {
        Rectangle()
          .fill(ColorTheme.darkGrey)
        Rectangle()
          .fill(ColorTheme.primary)
          .frame(width: geometry.size.width * animatedProgress)
      }
    }
    .frame(height: 8)
    .cornerRadius(4)
    .onAppear {
      withAnimation(.easeOut(duration: 1.0)) {
        animatedProgress = CGFloat(progress)
      }
    }
  }
}

struct SessionListView: View {
  let sessions: [TrainingSession]

  var body: some View {
    VStack(spacing: 16) {
      ForEach(sessions) { session in
        SessionView(session: session)
      }
    }
  }
}

struct SessionView: View {
  let session: TrainingSession

  var body: some View {
    HStack(alignment: .top, spacing: 10) {
      Text(session.day.prefix(3).uppercased())
        .font(.subheadline)
        .foregroundColor(ColorTheme.lightGrey)
        .frame(width: 40, alignment: .leading)

      VStack(alignment: .leading, spacing: 4) {
        Text(session.sessionType)
          .font(.headline)
          .foregroundColor(ColorTheme.white)

        if !session.notes.isEmpty {
          Text(session.notes)
            .font(.caption)
            .foregroundColor(ColorTheme.lightGrey)
            .lineLimit(2)
        }
      }

      Spacer()

      VStack(alignment: .trailing, spacing: 4) {
        Text(String(format: "%.1f mi", session.distance))
          .font(.subheadline)
          .foregroundColor(ColorTheme.lightGrey)

        Circle()
          .fill(session.completed ? ColorTheme.green : ColorTheme.darkGrey)
          .frame(width: 12, height: 12)
      }
    }
    .padding()
    .cornerRadius(8)
    .overlay(RoundedRectangle(cornerRadius: 8).stroke(ColorTheme.darkDarkGrey, lineWidth: 1))
  }
}
