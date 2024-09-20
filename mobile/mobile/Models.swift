import Foundation

struct ProfileData: Codable {
  let firstname: String
  let lastname: String
  let email: String
  let profile: String
  let isActive: Bool
  let preferences: String

  enum CodingKeys: String, CodingKey {
    case firstname, lastname, email, profile, preferences
    case isActive = "is_active"
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
