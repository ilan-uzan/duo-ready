import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            VStack {
                Image("hero")
                    .resizable()
                    .aspectRatio(contentMode: .fill)
                VideoPlaceholder()
                    .aspectRatio(16 / 9, contentMode: .fit)
                HomeTabBar()
            }
            .navigationBarHidden(true)
        }
    }
}

/// SwiftUI custom bar: HStack of buttons pinned to the bottom.
struct HomeTabBar: View {
    var body: some View {
        HStack {
            Button("Home") {}
            Button("Search") {}
        }
    }
}

struct VideoPlaceholder: View {
    var body: some View { Color.black }
}

/// Uses an iOS 27.1-only API in a project with SUPPORTS_MACCATALYST = YES and no
/// `#if !targetEnvironment(macCatalyst)` guard (DUO-020). Gated with #available, so DUO-019
/// should also note the project still says LastUpgradeCheck = 2600.
struct PlayerScreen: View {
    var body: some View {
        if #available(iOS 27.1, *) {
            ArrangementView { Color.red } secondary: { Color.blue }
        } else {
            Color.red
        }
    }
}
