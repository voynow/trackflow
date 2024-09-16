//
//  mobileApp.swift
//  mobile
//
//  Created by jamie voynow on 9/15/24.
//

import SwiftUI

@main
struct mobileApp: App {
  @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

  var body: some Scene {
    WindowGroup {
      ContentView()
        .onOpenURL { url in
          appDelegate.application(UIApplication.shared, open: url, options: [:])
        }
    }
  }
}
