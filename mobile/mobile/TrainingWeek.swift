import SwiftUI
import SwiftUICharts

struct TrainingWeekView: View {
  let trainingWeekData: TrainingWeekData
  let weeklySummaries: [WeekSummary]

  var body: some View {
    VStack(spacing: 16) {
      WeeklyProgressView(sessions: trainingWeekData.sessions, weeklySummaries: weeklySummaries)
      SessionListView(sessions: trainingWeekData.sessions)
    }
    .padding(20)
    .background(ColorTheme.black)
    .cornerRadius(16)
  }
}

struct WeeklyProgressView: View {
  let sessions: [TrainingSession]
  let weeklySummaries: [WeekSummary]
  @State private var showingMultiWeek: Bool = false

  private var completedMileage: Double {
    sessions.reduce(0) { $0 + ($1.completed ? $1.distance : 0) }
  }

  private var totalMileage: Double {
    sessions.reduce(0) { $0 + $1.distance }
  }

  var body: some View {
    VStack {
      ZStack(alignment: .top) {
        WeeklyProgressContent(completedMileage: completedMileage, totalMileage: totalMileage)
          .opacity(showingMultiWeek ? 0 : 1)
          .zIndex(showingMultiWeek ? 0 : 1)

        MultiWeekProgressView(weeklySummaries: weeklySummaries, numberOfWeeks: 8)
          .opacity(showingMultiWeek ? 1 : 0)
          .frame(height: showingMultiWeek ? nil : 0, alignment: .top)
          .clipped()
          .zIndex(showingMultiWeek ? 1 : 0)
      }
      .animation(.easeInOut(duration: 0.3), value: showingMultiWeek)
    }
    .padding()
    .background(ColorTheme.darkDarkGrey)
    .cornerRadius(16)
    .onTapGesture {
      showingMultiWeek.toggle()
    }
  }
}

struct WeeklyProgressContent: View {
  let completedMileage: Double
  let totalMileage: Double

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
          .foregroundColor(ColorTheme.midLightGrey)
      }
      .padding(.top, 6)

      ProgressBar(progress: completedMileage / totalMileage)
        .frame(height: 10)
        .animation(.easeOut(duration: 1.0), value: completedMileage)
    }
  }
}

struct MultiWeekProgressView: View {
  let weeklySummaries: [WeekSummary]
  let numberOfWeeks: Int

  private var displayedSummaries: [WeekSummary] {
    Array(weeklySummaries.prefix(numberOfWeeks).reversed())
  }

  private var chartData: [(String, Double)] {
    displayedSummaries.map { (weekLabel(for: $0.parsedWeekStartDate), $0.totalDistance) }
  }

  var body: some View {
    VStack(spacing: 8) {
      Text("Last \(numberOfWeeks) Weeks")
        .font(.headline)
        .foregroundColor(ColorTheme.white)
        .frame(maxWidth: .infinity, alignment: .leading)
      LineView(
        data: chartData.map { $0.1 },
        title: "Weekly Distance",
        legend: "Miles",
        style: ChartStyle(
          backgroundColor: Color.clear,
          accentColor: ColorTheme.primary,
          gradientColor: GradientColors.blue,
          textColor: ColorTheme.lightGrey,
          legendTextColor: ColorTheme.lightGrey,
          dropShadowColor: Color.clear
        ),
        valueSpecifier: "%.1f"
      )
      .frame(height: 350)
      HStack {
        Text(
          "Total: \(String(format: "%.1f mi", displayedSummaries.reduce(0) { $0 + $1.totalDistance }))"
        )
        .font(.headline)
        .foregroundColor(ColorTheme.white)
        Spacer()
        Text("Max: \(String(format: "%.1f mi", chartData.map { $0.1 }.max() ?? 0))")
          .font(.subheadline)
          .foregroundColor(ColorTheme.lightGrey)
      }
    }
  }

  private func weekLabel(for date: Date?) -> String {
    guard let date = date else { return "" }
    let formatter = DateFormatter()
    formatter.dateFormat = "MM/dd"
    return formatter.string(from: date)
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
  @State private var isExpanded: Bool = false

  var body: some View {
    VStack(alignment: .leading, spacing: 24) {
      HStack(alignment: .center, spacing: 16) {
        Text(session.day.prefix(3).uppercased())
          .font(.system(size: 14, weight: .bold))
          .foregroundColor(ColorTheme.primaryLight)
          .frame(width: 40, alignment: .leading)

        VStack(alignment: .leading, spacing: 4) {
          Text(session.sessionType)
            .font(.system(size: 18, weight: .semibold))
            .foregroundColor(ColorTheme.white)
          Text(String(format: "%.1f mi", session.distance))
            .font(.system(size: 14, weight: .regular))
            .foregroundColor(ColorTheme.lightGrey)
        }

        Spacer()

        Circle()
          .fill(session.completed ? ColorTheme.green : ColorTheme.darkGrey)
          .frame(width: 16, height: 16)
      }

      if isExpanded {
        VStack(alignment: .leading, spacing: 4) {
          Text("\(session.completed ? "Completed" : "Upcoming")")
            .font(.system(size: 14, weight: .medium))
            .foregroundColor(session.completed ? ColorTheme.green : ColorTheme.yellow)

          if !session.notes.isEmpty {
            Text(session.notes)
              .font(.system(size: 14, weight: .regular))
              .foregroundColor(ColorTheme.lightGrey)
              .lineSpacing(4)
          }
        }
        .transition(.opacity.combined(with: .move(edge: .top)))
      }
    }
    .padding(.horizontal, 30)
    .padding(.vertical, 20)
    .overlay(RoundedRectangle(cornerRadius: 12).stroke(ColorTheme.darkGrey, lineWidth: 1))
    .background(ColorTheme.black)
    .cornerRadius(12)
    .animation(.spring(response: 0.5, dampingFraction: 0.7), value: isExpanded)
    .onTapGesture {
      withAnimation {
        isExpanded.toggle()
      }
    }
  }
}
