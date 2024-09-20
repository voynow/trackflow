import SwiftUI

struct TrainingWeekView: View {
  let data: TrainingWeekData

  var body: some View {
    VStack(alignment: .leading) {

      WeeklyProgressView(sessions: data.sessions)

      ForEach(data.sessions) { session in
        SessionView(session: session)
      }
    }
    .padding()
    .background(ColorTheme.bg1)
  }
}

struct WeeklyProgressView: View {
  let sessions: [TrainingSession]

  var totalMileage: Double {
    sessions.reduce(0) { $0 + $1.distance }
  }

  var completedMileage: Double {
    sessions.reduce(0) { $0 + ($1.completed ? $1.distance : 0) }
  }

  var progressPercentage: Int {
    totalMileage > 0 ? Int((completedMileage / totalMileage) * 100) : 0
  }

  var body: some View {
    VStack(alignment: .leading, spacing: 10) {
      Text("Weekly Progress")
        .font(.headline)
        .foregroundColor(ColorTheme.inverseText)

      HStack {
        Text("\(progressPercentage)%")
          .font(.system(size: 36, weight: .bold))
          .foregroundColor(ColorTheme.inverseText)

        Spacer()

        Text(
          "\(String(format: "%.1f", completedMileage)) of \(String(format: "%.1f", totalMileage)) miles completed"
        )
        .font(.caption)
        .foregroundColor(ColorTheme.inverseText)
      }

      GeometryReader { geometry in
        ZStack(alignment: .leading) {
          Rectangle()
            .fill(ColorTheme.bg1)
            .frame(height: 8)
            .cornerRadius(4)

          Rectangle()
            .fill(
              LinearGradient(
                gradient: Gradient(colors: [.green, .green.opacity(0.5)]), startPoint: .leading,
                endPoint: .trailing)
            )
            .frame(width: geometry.size.width * CGFloat(progressPercentage) / 100, height: 8)
            .cornerRadius(4)
        }
      }
      .frame(height: 8)
    }
    .padding()
    .background(ColorTheme.inverseBackground)
    .cornerRadius(10)
  }
}

struct SessionView: View {
  let session: TrainingSession

  var body: some View {
    HStack(alignment: .top) {
      Text(session.day.prefix(3).uppercased())
        .font(.headline)
        .foregroundColor(ColorTheme.t1)
        .frame(width: 40, alignment: .leading)

      VStack(alignment: .leading, spacing: 4) {
        HStack {
          Text(String(format: "%.1f mi", session.distance))
            .font(.title2)
            .fontWeight(.bold)
            .foregroundColor(ColorTheme.t0)

          Spacer()

          Circle()
            .fill(session.completed ? .green : ColorTheme.bg0)
            .frame(width: 12, height: 12)
        }

        Text(session.sessionType)
          .font(.subheadline)
          .foregroundColor(ColorTheme.t1)

        if !session.notes.isEmpty {
          Text(session.notes)
            .font(.caption)
            .foregroundColor(ColorTheme.t1)
            .padding(.top, 4)
        }
      }
    }
    .padding()
    .background(ColorTheme.bg2)
    .cornerRadius(10)
  }
}
