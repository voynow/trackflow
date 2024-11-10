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

  private let session: URLSession
  private let baseURL = "https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup"
  private let apiURL = "http://trackflow-alb-499532887.us-east-1.elb.amazonaws.com"

  func fetchProfileData(token: String, completion: @escaping (Result<ProfileData, Error>) -> Void) {
    let body: [String: Any] = ["jwt_token": token, "method": "get_profile"]
    performRequest(body: body, responseType: ProfileResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success, let profile = response.profile {
          completion(.success(profile))
        } else {
          completion(
            .failure(
              NSError(
                domain: "", code: 0,
                userInfo: [NSLocalizedDescriptionKey: response.message ?? "Unknown error"])))
        }
      case .failure(let error):
        completion(.failure(error))
      }
    }
  }

  func fetchTrainingWeekData(
    token: String,
    completion: @escaping (Result<TrainingWeekData, Error>) -> Void
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
      print("fetchTrainingWeekData took \(timeElapsed) seconds")

      if let httpResponse = response as? HTTPURLResponse {
        switch httpResponse.statusCode {
        case 401:
          completion(
            .failure(
              NSError(
                domain: "",
                code: 401,
                userInfo: [NSLocalizedDescriptionKey: "Invalid or expired token"]
              )))
          return
        case 403:
          completion(
            .failure(
              NSError(
                domain: "",
                code: 403,
                userInfo: [
                  NSLocalizedDescriptionKey:
                    "Access forbidden - you don't have permission to access this resource"
                ]
              )))
          return
        case 404:
          completion(
            .failure(
              NSError(
                domain: "",
                code: 404,
                userInfo: [NSLocalizedDescriptionKey: "Training week not found"]
              )))
          return
        case 200..<300:
          break
        default:
          completion(
            .failure(
              NSError(
                domain: "",
                code: httpResponse.statusCode,
                userInfo: [NSLocalizedDescriptionKey: "Server error"]
              )))
          return
        }
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
        let trainingWeek = try JSONDecoder().decode(TrainingWeekData.self, from: data)
        completion(.success(trainingWeek))
      } catch {
        print("Decoding error: \(error)")
        if let json = try? JSONSerialization.jsonObject(with: data, options: []) {
          print("JSON: \(json)")
        }
        completion(.failure(error))
      }
    }.resume()
  }

  func savePreferences(
    token: String, preferences: Preferences, completion: @escaping (Result<Void, Error>) -> Void
  ) {
    let idealTrainingWeek = preferences.idealTrainingWeek?.map { day in
      return [
        "day": day.day.rawValue,
        "session_type": day.sessionType,
      ]
    }

    let preferencesPayload: [String: Any] = [
      "race_distance": preferences.raceDistance ?? NSNull(),
      "ideal_training_week": idealTrainingWeek ?? [],
    ]

    let body: [String: Any] = [
      "jwt_token": token,
      "method": "update_preferences",
      "payload": [
        "preferences": preferencesPayload
      ],
    ]

    performRequest(body: body, responseType: SavePreferencesResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success {
          completion(.success(()))
        } else {
          let errorMessage = response.error ?? "Failed to save preferences"
          completion(
            .failure(
              NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
        }
      case .failure(let error):
        completion(.failure(error))
      }
    }
  }

  func refreshToken(token: String, completion: @escaping (Result<String, Error>) -> Void) {
    let body: [String: Any] = ["jwt_token": token, "method": "refresh_token"]
    performRequest(body: body, responseType: RefreshTokenResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success, let newToken = response.jwt_token {
          completion(.success(newToken))
        } else {
          completion(
            .failure(
              NSError(
                domain: "", code: 0,
                userInfo: [NSLocalizedDescriptionKey: response.message ?? "Token refresh failed"])))
        }
      case .failure(let error):
        completion(.failure(error))
      }
    }
  }

  func fetchWeeklySummaries(
    token: String, completion: @escaping (Result<[WeekSummary], Error>) -> Void
  ) {
    let body: [String: Any] = ["jwt_token": token, "method": "get_weekly_summaries"]

    performRequest(body: body, responseType: WeeklySummariesResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success, let summariesStrings = response.weekly_summaries {
          let summaries = summariesStrings.compactMap { summaryString -> WeekSummary? in
            guard let data = summaryString.data(using: .utf8) else { return nil }
            do {
              let summary = try JSONDecoder().decode(WeekSummary.self, from: data)
              return summary
            } catch {
              print("Failed to decode summary. Error: \(error)")
              return nil
            }
          }
          completion(.success(summaries))
        } else {
          let errorMessage = response.message ?? "Unknown error"
          completion(
            .failure(
              NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
        }
      case .failure(let error):
        completion(.failure(error))
      }
    }
  }

  private func performRequest<T: Decodable>(
    body: [String: Any], responseType: T.Type, completion: @escaping (Result<T, Error>) -> Void
  ) {
    guard let url = URL(string: baseURL) else {
      completion(
        .failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: "Invalid URL"]))
      )
      return
    }

    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)

    // Use shared session instead of URLSession.shared
    session.dataTask(with: request) { data, response, error in
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
        let decodedResponse = try JSONDecoder().decode(T.self, from: data)
        completion(.success(decodedResponse))
      } catch {
        print("Decoding error: \(error)")
        completion(.failure(error))
      }
    }.resume()
  }

  func startOnboarding(token: String, completion: @escaping (Result<Void, Error>) -> Void) {
    let body: [String: Any] = ["jwt_token": token, "method": "start_onboarding"]
    performRequest(body: body, responseType: GenericResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success {
          completion(.success(()))
        } else {
          let errorMessage = response.message ?? "Failed to start onboarding"
          completion(
            .failure(
              NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
        }
      case .failure(let error):
        completion(.failure(error))
      }
    }
  }

  func updateDeviceToken(
    token: String, deviceToken: String, completion: @escaping (Result<Void, Error>) -> Void
  ) {
    let body: [String: Any] = [
      "jwt_token": token,
      "payload": ["device_token": deviceToken],
      "method": "update_device_token",
    ]

    performRequest(body: body, responseType: GenericResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success {
          completion(.success(()))
        } else {
          let errorMessage = response.message ?? "Failed to update device token"
          completion(
            .failure(
              NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
        }
      case .failure(let error):
        completion(.failure(error))
      }
    }
  }
}
