import Foundation

class APIManager {
  static let shared = APIManager()
  private init() {}

  private let baseURL = "https://lwg77yq7dd.execute-api.us-east-1.amazonaws.com/prod/signup"

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
    token: String, completion: @escaping (Result<TrainingWeekData, Error>) -> Void
  ) {
    let body: [String: Any] = ["jwt_token": token, "method": "get_training_week"]
    performRequest(body: body, responseType: TrainingWeekResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success, let trainingWeekString = response.trainingWeek,
          let trainingWeekData = trainingWeekString.data(using: .utf8)
        {
          do {
            let parsedData = try JSONDecoder().decode(TrainingWeekData.self, from: trainingWeekData)
            completion(.success(parsedData))
          } catch {
            completion(.failure(error))
          }
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

  func savePreferences(token: String, preferences: Preferences, completion: @escaping (Result<Void, Error>) -> Void) {
    let idealTrainingWeek = preferences.idealTrainingWeek?.map { day in
      return [
        "day": day.day.rawValue,
        "session_type": day.sessionType
      ]
    }

    let preferencesPayload: [String: Any] = [
      "race_distance": preferences.raceDistance ?? NSNull(),
      "ideal_training_week": idealTrainingWeek ?? []
    ]

    let body: [String: Any] = [
      "jwt_token": token,
      "method": "update_preferences",
      "payload": [
        "preferences": preferencesPayload
      ]
    ]
    
    performRequest(body: body, responseType: SavePreferencesResponse.self) { result in
      switch result {
      case .success(let response):
        if response.success {
          completion(.success(()))
        } else {
          let errorMessage = response.error ?? "Failed to save preferences"
          completion(.failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: errorMessage])))
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
          completion(.failure(NSError(domain: "", code: 0, userInfo: [NSLocalizedDescriptionKey: response.message ?? "Token refresh failed"])))
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

    URLSession.shared.dataTask(with: request) { data, response, error in
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
        completion(.failure(error))
      }
    }.resume()
  }
}
