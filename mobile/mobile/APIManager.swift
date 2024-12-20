import Foundation

class APIManager {
  static let shared = APIManager()
  private init() {
    let config = URLSessionConfiguration.default
    config.timeoutIntervalForRequest = 30
    config.timeoutIntervalForResource = 300
    config.httpMaximumConnectionsPerHost = 6
    config.waitsForConnectivity = true
    session = URLSession(configuration: config)
  }

  internal let session: URLSession
  internal let apiURL = "http://trackflow-alb-499532887.us-east-1.elb.amazonaws.com"

  private struct ProfileCache {
    static var data: ProfileData?
    static var lastFetchTime: Date?
    static let cacheTimeout: TimeInterval = 300  // 5 minutes

    static func shouldRefetch() -> Bool {
      guard let lastFetch = lastFetchTime else { return true }
      return Date().timeIntervalSince(lastFetch) > cacheTimeout
    }

    static func update(_ profile: ProfileData) {
      data = profile
      lastFetchTime = Date()
    }
  }

  func fetchProfileData(token: String, completion: @escaping (Result<ProfileData, Error>) -> Void) {
    if !ProfileCache.shouldRefetch(), let cachedData = ProfileCache.data {
      completion(.success(cachedData))
      return
    }

    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/profile/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: fetchProfileData took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        completion(
          .failure(
            NSError(
              domain: "",
              code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: "Failed to fetch profile"]
            )))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      guard let data = data else {
        completion(
          .failure(
            NSError(
              domain: "",
              code: 0,
              userInfo: [NSLocalizedDescriptionKey: "No data received"]
            )))
        return
      }

      do {
        // Create a container struct for the response
        struct ProfileResponse: Decodable {
          let success: Bool
          let profile: ProfileData
        }

        let response = try JSONDecoder().decode(ProfileResponse.self, from: data)
        ProfileCache.update(response.profile)  // Update cache
        completion(.success(response.profile))
      } catch {
        print("Decoding error: \(error)")
        completion(.failure(error))
      }
    }.resume()
  }

  func fetchTrainingWeekData(
    token: String,
    completion: @escaping (Result<FullTrainingWeek, Error>) -> Void
  ) {
    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/training_week/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: fetchTrainingWeekData took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        let message: String
        switch httpResponse.statusCode {
        case 401: message = "Invalid or expired token"
        case 403: message = "Access forbidden"
        case 404: message = "Training week not found"
        default: message = "Server error"
        }
        completion(
          .failure(
            NSError(
              domain: "", code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: message])))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      guard let data = data else {
        completion(
          .failure(
            NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "No data received"]))
        )
        return
      }

      do {
        let trainingWeek = try JSONDecoder().decode(FullTrainingWeek.self, from: data)
        completion(.success(trainingWeek))
      } catch {
        print("Decoding error: \(error)")
        completion(.failure(error))
      }
    }.resume()
  }

  func savePreferences(
    token: String,
    preferences: Preferences,
    completion: @escaping (Result<Void, Error>) -> Void
  ) {
    guard let url = URL(string: "\(apiURL)/preferences/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    let encoder = JSONEncoder()
    encoder.dateEncodingStrategy = .iso8601

    do {
      let jsonData = try encoder.encode(preferences)
      request.httpBody = jsonData
    } catch {
      completion(.failure(error))
      return
    }

    session.dataTask(with: request) { [weak self] data, response, error in
      if let error = error {
        completion(.failure(error))
        return
      }

      // Update cache with new preferences
      if let cachedProfile = ProfileCache.data {
        do {
          let encoder = JSONEncoder()
          encoder.dateEncodingStrategy = .iso8601
          encoder.outputFormatting = .prettyPrinted
          let preferencesJSON = try encoder.encode(preferences)
          if let preferencesString = String(data: preferencesJSON, encoding: .utf8) {
            var updatedProfile = cachedProfile
            updatedProfile.preferences = preferencesString
            ProfileCache.update(updatedProfile)
          }
        } catch {
          print("Failed to update preferences cache: \(error)")
        }
      }

      completion(.success(()))
    }.resume()
  }

  func refreshToken(token: String, completion: @escaping (Result<String, Error>) -> Void) {
    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/refresh_token/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: refreshToken took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        completion(
          .failure(
            NSError(
              domain: "",
              code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: "Failed to refresh token"]
            )))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      guard let data = data else {
        completion(
          .failure(
            NSError(
              domain: "",
              code: 0,
              userInfo: [NSLocalizedDescriptionKey: "No data received"]
            )))
        return
      }

      do {
        let response = try JSONDecoder().decode(RefreshTokenResponse.self, from: data)
        if let newToken = response.jwt_token {
          completion(.success(newToken))
        } else {
          completion(
            .failure(
              NSError(
                domain: "",
                code: 0,
                userInfo: [NSLocalizedDescriptionKey: response.message ?? "Token refresh failed"]
              )))
        }
      } catch {
        print("Decoding error: \(error)")
        completion(.failure(error))
      }
    }.resume()
  }

  func fetchWeeklySummaries(
    token: String, completion: @escaping (Result<[WeekSummary], Error>) -> Void
  ) {
    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/weekly_summaries/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: fetchWeeklySummaries took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        completion(
          .failure(
            NSError(
              domain: "",
              code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: "Failed to fetch weekly summaries"]
            )))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      guard let data = data else {
        completion(
          .failure(
            NSError(
              domain: "",
              code: 0,
              userInfo: [NSLocalizedDescriptionKey: "No data received"]
            )))
        return
      }

      do {
        struct WeeklySummariesResponse: Decodable {
          let success: Bool
          let weekly_summaries: [String]
        }

        let response = try JSONDecoder().decode(WeeklySummariesResponse.self, from: data)

        // Then parse each string into a WeekSummary
        let summaries = try response.weekly_summaries.map { summaryString in
          guard let summaryData = summaryString.data(using: .utf8) else {
            throw NSError(
              domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid summary string"])
          }
          return try JSONDecoder().decode(WeekSummary.self, from: summaryData)
        }

        completion(.success(summaries))
      } catch {
        print("Decoding error: \(error)")
        completion(.failure(error))
      }
    }.resume()
  }

  func refreshUser(token: String, completion: @escaping (Result<Void, Error>) -> Void) {
    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/refresh/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: refresh took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        completion(
          .failure(
            NSError(
              domain: "",
              code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: "Failed to start onboarding"]
            )))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      completion(.success(()))
    }.resume()
  }

  func updateDeviceToken(
    token: String,
    deviceToken: String,
    completion: @escaping (Result<Void, Error>) -> Void
  ) {
    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/device_token/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    let payload = ["device_token": deviceToken]
    request.httpBody = try? JSONSerialization.data(withJSONObject: payload)

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: updateDeviceToken took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        let message = "Failed to update device token"
        completion(
          .failure(
            NSError(
              domain: "", code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: message])))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      completion(.success(()))
    }.resume()
  }

  func fetchTrainingPlan(token: String, completion: @escaping (Result<TrainingPlan, Error>) -> Void)
  {
    let startTime = CFAbsoluteTimeGetCurrent()
    guard let url = URL(string: "\(apiURL)/training-plan/") else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

    session.dataTask(with: request) { data, response, error in
      let timeElapsed = CFAbsoluteTimeGetCurrent() - startTime
      print("APIManager: fetchTrainingPlan took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse,
        !(200..<300).contains(httpResponse.statusCode)
      {
        completion(
          .failure(
            NSError(
              domain: "",
              code: httpResponse.statusCode,
              userInfo: [NSLocalizedDescriptionKey: "Failed to fetch training plan"]
            )))
        return
      }

      if let error = error {
        completion(.failure(error))
        return
      }

      guard let data = data else {
        completion(
          .failure(
            NSError(
              domain: "",
              code: 0,
              userInfo: [NSLocalizedDescriptionKey: "No data received"]
            )))
        return
      }

      do {
        // Create a direct mapping to the API response structure
        let decoder = JSONDecoder()
        let response = try decoder.decode(TrainingPlan.self, from: data)
        completion(.success(response))
      } catch {
        print("Decoding error: \(error)")
        completion(.failure(error))
      }
    }.resume()
  }

  func updateEmail(
    token: String,
    email: String,
    completion: @escaping (Result<Void, Error>) -> Void
  ) {
    guard let url = URL(string: "\(apiURL)/email/") else {
      completion(.failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"])))
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")

    let jsonString = "\"\(email)\""
    request.httpBody = jsonString.data(using: .utf8)

    session.dataTask(with: request) { data, response, error in
      if let error = error {
        completion(.failure(error))
        return
      }

      if let httpResponse = response as? HTTPURLResponse {
        if !(200..<300).contains(httpResponse.statusCode) {
          if let data = data, let responseStr = String(data: data, encoding: .utf8) {
            print("Email update error response: \(responseStr)")
          }
          completion(.failure(NSError(
            domain: "",
            code: httpResponse.statusCode,
            userInfo: [NSLocalizedDescriptionKey: "Failed to update email (Status: \(httpResponse.statusCode))"]
          )))
          return
        }
      }

      completion(.success(()))
    }.resume()
  }

}
