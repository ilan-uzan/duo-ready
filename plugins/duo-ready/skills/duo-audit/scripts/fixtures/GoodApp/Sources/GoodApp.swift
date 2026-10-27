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
                .modifier(AutomaticVerticalToolbar())
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
            Color.black.overlay(Text("\(divisionRegions(proxy).count) regions"))
        }
        .aspectRatio(contentMode: .fit)
        .modifier(BackgroundExtension())
    }

    private func divisionRegions(_ proxy: GeometryProxy) -> [CGRect] {
        if #available(iOS 27.1, *) {
            return proxy.reservedRegions(kind: .division).map(\.frame)
        }
        return []
    }
}

/// Applies the existing backgroundExtensionEffect() call only where the SDK makes it available (iOS 26.0+).
struct BackgroundExtension: ViewModifier {
    @ViewBuilder func body(content: Content) -> some View {
        if #available(iOS 26.0, *) {
            content.backgroundExtensionEffect()
        } else {
            content
        }
    }
}

/// Applies toolbarVerticalBehavior on iOS 27.1 and later; no-op on older systems.
struct AutomaticVerticalToolbar: ViewModifier {
    @ViewBuilder func body(content: Content) -> some View {
        if #available(iOS 27.1, *) {
            content.toolbarVerticalBehavior(.automatic)
        } else {
            content
        }
    }
}

struct UpNextView: View {
    var body: some View { List { Text("Up next") } }
}

@available(iOS 27.1, *)
struct CameraScreen: View {
    @State private var accessoryEnabled = true
    var body: some View {
        Color.gray
            .sceneAccessory {
                CameraCaptureAccessory(isEnabled: $accessoryEnabled) { Text("Smile") }
            }
    }
}
