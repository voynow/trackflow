import Foundation

struct ProfileData: Codable {
  var firstname: String
  var lastname: String
  var email: String?
  var profile: String
  var preferences: String?

  enum CodingKeys: String, CodingKey {
    case firstname, lastname, email, profile, preferences
  }
}

enum Day: String, CaseIterable, Codable {
  case mon = "Mon"
  case tues = "Tue"
  case wed = "Wed"
  case thurs = "Thu"
  case fri = "Fri"
  case sat = "Sat"
  case sun = "Sun"

  init(from decoder: Decoder) throws {
    let container = try decoder.singleValueContainer()
    let value = try container.decode(String.self)
    
    // Normalize variations
    let normalizedValue = value
      .replacingOccurrences(of: "Tues", with: "Tue")
      .replacingOccurrences(of: "Thurs", with: "Thu")
      .capitalized
    
    guard let day = Day(rawValue: normalizedValue) else {
      throw DecodingError.dataCorruptedError(
        in: container,
        debugDescription: "Cannot initialize Day from invalid String value \(value)"
      )
    }
    self = day
  }

  var fullName: String {
    switch self {
    case .mon: return "Monday"
    case .tues: return "Tuesday"
    case .wed: return "Wednesday"
    case .thurs: return "Thursday"
    case .fri: return "Friday"
    case .sat: return "Saturday"
    case .sun: return "Sunday"
    }
  }

  var displayText: String {
    rawValue.uppercased()
  }
}

struct TrainingDay: Codable {
  let day: Day
  var sessionType: String

  enum CodingKeys: String, CodingKey {
    case day
    case sessionType = "session_type"
  }
}

struct Preferences: Codable {
  var raceDistance: String?
  var idealTrainingWeek: [TrainingDay]?

  enum CodingKeys: String, CodingKey {
    case raceDistance = "race_distance"
    case idealTrainingWeek = "ideal_training_week"
  }

  func toJSON() -> String {
    let encoder = JSONEncoder()
    encoder.outputFormatting = .prettyPrinted
    do {
      let jsonData = try encoder.encode(self)
      return String(data: jsonData, encoding: .utf8) ?? "{}"
    } catch {
      print("Error encoding preferences: \(error)")
      return "{}"
    }
  }

  init(fromJSON json: String) {
    let decoder = JSONDecoder()
    if let jsonData = json.data(using: .utf8),
      let decoded = try? decoder.decode(Preferences.self, from: jsonData)
    {
      self = decoded
    } else {
      self.raceDistance = nil
      self.idealTrainingWeek = nil
    }
  }
}

struct SavePreferencesResponse: Codable {
  let success: Bool
  let error: String?
}

struct TrainingWeekData: Codable {
  let sessions: [TrainingSession]
}

enum SessionType: String, Codable {
  case easy = "easy run"
  case long = "long run"
  case speed = "speed workout"
  case rest = "rest day"
}

struct DailyMetrics: Codable {
  let date: String
  let dayOfWeek: Day
  let weekOfYear: Int
  let year: Int
  let distanceInMiles: Double
  let elevationGainInFeet: Double
  let movingTimeInMinutes: Double
  let paceMinutesPerMile: Double?
  let activityCount: Int

  enum CodingKeys: String, CodingKey {
    case date
    case dayOfWeek = "day_of_week"
    case weekOfYear = "week_of_year"
    case year
    case distanceInMiles = "distance_in_miles"
    case elevationGainInFeet = "elevation_gain_in_feet"
    case movingTimeInMinutes = "moving_time_in_minutes"
    case paceMinutesPerMile = "pace_minutes_per_mile"
    case activityCount = "activity_count"
  }
}

struct TrainingSession: Codable, Identifiable {
  let id: UUID
  let day: Day
  let sessionType: SessionType
  let distance: Double
  let notes: String

  init(id: UUID = UUID(), day: Day, sessionType: SessionType, distance: Double, notes: String) {
    self.id = id
    self.day = day
    self.sessionType = sessionType
    self.distance = distance
    self.notes = notes
  }

  enum CodingKeys: String, CodingKey {
    case day
    case sessionType = "session_type"
    case distance, notes
  }

  init(from decoder: Decoder) throws {
    let container = try decoder.container(keyedBy: CodingKeys.self)
    id = UUID()
    day = try container.decode(Day.self, forKey: .day)
    sessionType = try container.decode(SessionType.self, forKey: .sessionType)
    distance = try container.decode(Double.self, forKey: .distance)
    notes = try container.decode(String.self, forKey: .notes)
  }
}

struct TrainingWeek: Codable {
  let sessions: [TrainingSession]
}

struct FullTrainingWeek: Codable {
  let pastTrainingWeek: [DailyMetrics]
  let futureTrainingWeek: TrainingWeek

  enum CodingKeys: String, CodingKey {
    case pastTrainingWeek = "past_training_week"
    case futureTrainingWeek = "future_training_week"
  }
}

struct ProfileResponse: Codable {
  let success: Bool
  let message: String?
  let profile: ProfileData?
}

struct TrainingWeekResponse: Codable {
  let success: Bool
  let message: String?
  let trainingWeek: String?

  enum CodingKeys: String, CodingKey {
    case success, message
    case trainingWeek = "training_week"
  }
}

struct SignupResponse: Codable {
  let success: Bool
  let jwt_token: String
  let is_new_user: Bool?
}

struct RefreshTokenResponse: Codable {
  let success: Bool
  let message: String?
  let jwt_token: String?
}

struct WeekSummary: Codable {
  var year: Int
  var weekOfYear: Int
  var weekStartDate: String
  var longestRun: Double
  var totalDistance: Double

  enum CodingKeys: String, CodingKey {
    case year
    case weekOfYear = "week_of_year"
    case weekStartDate = "week_start_date"
    case longestRun = "longest_run"
    case totalDistance = "total_distance"
  }

  var parsedWeekStartDate: Date? {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd"
    return formatter.date(from: weekStartDate.prefix(10).description)
  }
}

struct WeeklySummariesResponse: Codable {
  let success: Bool
  let message: String?
  let weekly_summaries: [String]?
}

struct GenerateTrainingPlanResponse: Codable {
  let success: Bool
}

enum AppStateStatus {
  case loading
  case loggedOut
  case loggedIn
  case newUser
}

struct GenericResponse: Codable {
  let success: Bool
  let message: String?
}
