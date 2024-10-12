import Foundation

struct ProfileData: Codable {
  var firstname: String
  var lastname: String
  var email: String
  var profile: String
  var isActive: Bool
  var preferences: String?

  enum CodingKeys: String, CodingKey {
    case firstname, lastname, email, profile, preferences
    case isActive = "is_active"
  }
}

enum Day: String, CaseIterable, Codable {
  case mon = "Mon"
  case tues = "Tues"
  case wed = "Wed"
  case thurs = "Thurs"
  case fri = "Fri"
  case sat = "Sat"
  case sun = "Sun"
}

struct TrainingDay: Codable {
  let day: Day
  let sessionType: String

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

struct TrainingWeekData: Codable {
  let sessions: [TrainingSession]
}

struct TrainingSession: Codable, Identifiable {
  let id: UUID
  let day: String
  let sessionType: String
  let distance: Double
  let notes: String
  let completed: Bool

  enum CodingKeys: String, CodingKey {
    case day, distance, notes, completed
    case sessionType = "session_type"
  }

  init(from decoder: Decoder) throws {
    let container = try decoder.container(keyedBy: CodingKeys.self)
    id = UUID()
    day = try container.decode(String.self, forKey: .day)
    sessionType = try container.decode(String.self, forKey: .sessionType)
    distance = try container.decode(Double.self, forKey: .distance)
    notes = try container.decode(String.self, forKey: .notes)
    completed = try container.decode(Bool.self, forKey: .completed)
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
