import SwiftUI
import AVKit

@main
struct GoodApp: App {
    var body: some Scene {
        WindowGroup { RootView() }
    }
}

struct RootView: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.verticalSizeClass) private var verticalSizeClass
    @Environment(\.displayScale) private var displayScale
    @State private var size: CGSize = .zero

    var body: some View {
        NavigationStack {
            content
                .toolbar {
                    ToolbarItem(placement: .primaryAction) {
                        Button("Share", systemImage: "square.and.arrow.up") {}
                    }
                }
                .toolbarVerticalBehavior(.automatic)
        }
        .onGeometryChange(for: CGSize.self) { proxy in proxy.size } action: { size = $0 }
    }

    @ViewBuilder private var content: some View {
        if #available(iOS 27.1, *) {
            ArrangementView { PlayerView() } secondary: { UpNextView() }
                .arrangementViewStyle(.split)
                .onHingeChange { _, context in
                    _ = context.hinge?.status
                }
        } else if horizontalSizeClass == .regular {
            HStack { PlayerView(); UpNextView() }
        } else {
            VStack { PlayerView(); UpNextView() }
        }
    }
}

struct PlayerView: View {
    var body: some View {
        GeometryReader { proxy in
            let regions: [CGRect]
            if #available(iOS 27.1, *) {
                regions = proxy.reservedRegions(kind: .division).map(\.frame)
            } else {
                regions = []
            }
            Color.black.overlay(Text("\(regions.count) regions"))
        }
        .aspectRatio(contentMode: .fit)
        .backgroundExtensionEffect()
    }
}

struct UpNextView: View {
    var body: some View { List { Text("Up next") } }
}

struct CameraScreen: View {
    @State private var accessoryEnabled = true
    var body: some View {
        Color.gray
            .sceneAccessory {
                CameraCaptureAccessory(isEnabled: $accessoryEnabled) { Text("Smile") }
            }
    }
}
