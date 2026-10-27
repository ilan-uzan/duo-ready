Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# duo-layout samples

Part A reproduces Apple's own examples exactly as quoted in the report and on the reference
pages re-checked on 2026-10-26. Part B contains minimal samples composed from those confirmed
symbols; none of Part B has been compiled against the iOS 27.1 SDK, and each one says so in
its header comment. Placeholder types (`ShelfList`, `BookDetail`, `Album`, ...) are the
user's own views.

Contents

- A. Apple's verbatim examples
  - A1 Size classes, screen access, safe areas (Tech Talk 111461)
  - A2 Reserved regions, SwiftUI
  - A3 Reserved regions, UIKit
  - A4 ArrangementView
  - A5 Arrangement environment values
  - A6 UIArrangementViewController
  - A7 Trait registration (Adapting your app when traits change)
- B. Composed samples
  - B1 Size-class-driven layout that keeps view identity
  - B2 Before/after: cached screen size vs `onGeometryChange`
  - B3 Before/after: UIKit screen and safe-area assumptions
  - B4 UIKit: reserved regions in `updateConstraints()`
  - B5 SwiftUI: even-column grid using the inactive division
  - B6 ArrangementView in the right container order
  - B7 UIArrangementViewController with z-index
  - B8 Scene geometry hook for games (TN3192)
  - B9 Availability gating

## A. Apple's verbatim examples

### A1 Size classes, screen access, safe areas (Tech Talk 111461)

Code fragments as shown in Apple's "Prepare your app for iPhone Duo" Tech Talk, transcribed
in the report. Re-check wording against the video page before quoting as verbatim prose.

```swift
@Environment(\.horizontalSizeClass) private var horizontalSizeClass
@Environment(\.verticalSizeClass) private var verticalSizeClass

traitCollection.horizontalSizeClass

let screen = window?.windowScene?.screen

// Safe areas: interactive content inside, artwork may extend.
foreground.frame = view.bounds.inset(by: view.safeAreaInsets)
backgroundView.frame = view.bounds

// Anti-pattern (assumes symmetric insets):
view.bounds.width - view.safeAreaInsets.left * 2
// Replacement:
view.bounds.inset(by: view.safeAreaInsets).width

// Scale:
traitCollection.displayScale   // instead of UIScreen.main.scale

// Corner concentricity (iOS 26):
ConcentricRectangle().fill(Color.green).padding(8.0).ignoresSafeArea()

// Sidebar on the inner display:
TabView { /* … */ }.defaultTabBarPlacement(.sidebar)
tabBarController.sidebar.preferredPlacement = .sidebar
```

### A2 Reserved regions, SwiftUI

From [GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)):

```swift
GeometryReader { proxy in
    RegionAvoidingLayout(
        regions: proxy.reservedRegions(kind: .occlusion)
    ) {
        ForEach(items) { item in
            ItemView(item)
        }
    }
}
```

Apple's caveat on the same page: region frames are measured from the top-leading corner of
the view you read them from; a custom `Layout`'s `bounds` in `placeSubviews` do not always
start at (0,0), so compute from (0,0) and add `bounds.origin` when placing.

Forms used in Tech Talk 111463:

```swift
proxy.reservedRegions(kind: .division)
proxy.reservedRegions(kind: .division, options: .includeInactive)
proxy.reservedRegions(kind: .occlusion)
regions.map(\.frame)
```

### A3 Reserved regions, UIKit

Tech Talk 111463:

```swift
let regions = view.reservedRegions(kind: .division)
let frames = regions.map(\.frame)
```

[UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion) page:

```swift
let regions = reservedRegions(kind: .occlusion)
let regions = reservedRegions(kind: .occlusion, options: .includeInactive)
```

### A4 ArrangementView

From [ArrangementView](https://developer.apple.com/documentation/swiftui/arrangementview) and
[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

```swift
ArrangementView {
    PlayerControls()
} secondary: {
    VideoPlayer()
}
.arrangementViewStyle(.overlay)

ArrangementView {
    NowPlayingView()
} secondary: {
    LyricsView()
}
.arrangementViewStyle(.split)

ArrangementView {
    PrimaryContent()
} secondary: {
    SecondaryContent()
}
.arrangementViewStyle(.split.axes(.vertical))

ArrangementView {
    PrimaryView()
} secondary: {
    SecondaryView()
}
.arrangementViewStyle(.split.axes(.horizontal))
```

### A5 Arrangement environment values

Tech Talk 111463:

```swift
struct UpNextView: View {
  @Environment(\.overlayArrangementZIndex)
  private var zIndex: Int

  var body: some View {
    UpNextList(minimization: minimization)
  }

  var minimization: UpNextMinimization {
    zIndex > 0 ? .collapsed : .expanded
  }
}
```

[overlayArrangementZIndex](https://developer.apple.com/documentation/swiftui/environmentvalues/overlayarrangementzindex) reference page (verified 2026-10-26):

```swift
struct PlayerView: View {
    @Environment(\.overlayArrangementZIndex) var zIndex

    var body: some View {
        VideoPlayerControls()
            .opacity(zIndex == 0 ? 1.0 : 0.5)
    }
}
```

[splitArrangementAxis](https://developer.apple.com/documentation/swiftui/environmentvalues/splitarrangementaxis) reference page (verified 2026-10-26):

```swift
struct DetailsView: View {
    @Environment(\.splitArrangementAxis) var axis

    var body: some View {
        let layout: AnyLayout = axis == .horizontal
            ? AnyLayout(VStackLayout())
            : AnyLayout(HStackLayout())
        layout {
            Artwork()
            Metadata()
        }
    }
}
```

### A6 UIArrangementViewController

From [UIArrangementViewController](https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller) and Tech Talk 111463:

```swift
let arrangementVC = UIArrangementViewController()

let primaryVC = PrimaryViewController()
arrangementVC.setViewController(primaryVC, for: .primary)

let secondaryVC = SecondaryViewController()
arrangementVC.setViewController(secondaryVC, for: .secondary)

arrangementVC.updateArrangement(.split.axes(.vertical))   // or .split, .overlay, .split.axes(.horizontal)

let primaryState = arrangementVC.state(for: .primary)
myModel.minimization = (primaryState?.zIndex ?? 0) > 0 ? .collapsed : .expanded
```

### A7 Trait registration

From [Adapting your app when traits change](https://developer.apple.com/documentation/uikit/adapting-your-app-when-traits-change), the article the Preparing page links for automatic trait tracking (verified 2026-10-26):

```swift
override func viewDidLoad() {
    super.viewDidLoad()

    registerForTraitChanges([
        UITraitHorizontalSizeClass.self,
        UITraitVerticalSizeClass.self
    ]) { (self: Self, previousTraitCollection: UITraitCollection) in
        self.updateLayout()
    }
}
```

## B. Composed samples

### B1 Size-class-driven layout that keeps view identity

Why: the HIG wants one compact-width and one regular-width layout, and a fold "is treated as a
size-class and trait change" (Forums 847644), so switching the layout rather than the view tree
keeps `ShelfList` and `BookDetail` alive with their scroll positions.

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

struct LibraryScreen: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        // Regular width (inner display, either rotation) shows both panes side by side.
        // Compact width (outer display) stacks them. Never consult idiom or orientation.
        let layout: AnyLayout = horizontalSizeClass == .regular
            ? AnyLayout(HStackLayout())
            : AnyLayout(VStackLayout())
        layout {
            ShelfList()
            BookDetail()
        }
    }
}
```

When the relationship is list-and-detail, prefer `NavigationSplitView`, which Apple says
expands on the inner display and collapses to a single pane on the outer display without any
Duo-specific code (HIG).

### B2 Before/after: cached screen size vs `onGeometryChange`

```swift
// Before: breaks on Duo. UIScreen.main is "ambiguous on two-display devices" (Tech Talk 111461)
// and a value copied in onAppear goes stale when the device folds.
import SwiftUI

struct PosterGrid_Before: View {
    @State private var width: CGFloat = 0

    var body: some View {
        PosterRows(columns: width > 700 ? 4 : 2)       // magic breakpoint; Apple: remove device-size checks
            .onAppear { width = UIScreen.main.bounds.width }
    }
}
```

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

struct PosterGrid: View {
    @State private var containerWidth: CGFloat = 0
    private let minimumItemWidth: CGFloat = 160   // your design's minimum, not a device size

    var body: some View {
        PosterRows(columns: columnCount)
            .onGeometryChange(for: CGFloat.self) { proxy in
                proxy.size.width                   // container width, re-evaluated after every resize
            } action: { newWidth in
                containerWidth = newWidth
            }
    }

    private var columnCount: Int {
        let fit = Int(containerWidth / minimumItemWidth)
        return max(2, fit - fit % 2)               // HIG: prefer an even number of columns
    }
}
```

### B3 Before/after: UIKit screen and safe-area assumptions

```swift
// Before: three Duo breakages in one controller.
import UIKit

final class HeroViewController_Before: UIViewController {
    private let cachedWidth = UIScreen.main.bounds.width                 // wrong display, read once
    private let isWide = UIDevice.current.userInterfaceIdiom == .pad     // idiom stays .phone on Duo

    override func viewDidLoad() {
        super.viewDidLoad()
        let contentWidth = view.bounds.width - view.safeAreaInsets.left * 2   // assumes symmetric insets
        _ = (cachedWidth, isWide, contentWidth)
    }
}
```

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

final class HeroViewController: UIViewController {
    private let backgroundView = UIImageView()
    private let foreground = UIStackView()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(backgroundView)
        view.addSubview(foreground)

        // Automatic trait tracking (Apple's example form in "Adapting your app when traits change").
        registerForTraitChanges([
            UITraitHorizontalSizeClass.self,
            UITraitVerticalSizeClass.self
        ]) { (self: Self, previousTraitCollection: UITraitCollection) in
            self.updateLayout()
        }
        updateLayout()
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        // Re-read every layout pass: "a fold can resize your app in the middle of a session".
        backgroundView.frame = view.bounds                               // artwork may extend past the safe area
        foreground.frame = view.bounds.inset(by: view.safeAreaInsets)   // each edge handled independently
    }

    private func updateLayout() {
        // Decide by size class, never by idiom or orientation.
        foreground.axis = traitCollection.horizontalSizeClass == .regular ? .horizontal : .vertical
    }
}
```

### B4 UIKit: reserved regions in `updateConstraints()`

Why here: "UIKit tracks the regions you read in `updateConstraints()` and runs it again when
the regions change" ([UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))).
`frame` already includes `margins`, so no extra padding is added.

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

@available(iOS 27.1, *)
final class PlaybackControlsView: UIView {
    private let playButton = UIButton(type: .system)
    private var centerXConstraint: NSLayoutConstraint!

    override init(frame: CGRect) {
        super.init(frame: frame)
        playButton.translatesAutoresizingMaskIntoConstraints = false
        addSubview(playButton)
        centerXConstraint = playButton.centerXAnchor.constraint(equalTo: centerXAnchor)
        NSLayoutConstraint.activate([
            centerXConstraint,
            playButton.bottomAnchor.constraint(equalTo: safeAreaLayoutGuide.bottomAnchor, constant: -16)
        ])
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) is not supported") }

    override func updateConstraints() {
        // Only active regions are returned by default; the flat fold is inactive with zero width.
        let activeDivision = reservedRegions(kind: .division).first { $0.isActive }

        if let fold = activeDivision, fold.frame.width < fold.frame.height {
            // A vertical fold line: center the control in the trailing part, clear of the fold
            // (Tech Talk 111463 puts interactive controls in the trailing/bottom region).
            centerXConstraint.constant = (fold.frame.maxX + bounds.width) / 2 - bounds.midX
        } else {
            // Flat, closed, or a horizontal fold line: centered on the whole view.
            centerXConstraint.constant = 0
        }
        super.updateConstraints()
    }
}
```

### B5 SwiftUI: even-column grid using the inactive division

Why: "prefer an even number of grid columns whenever a division region is present, whether or
not it is currently active" (Tech Talk 111463). Apple also says apps "usually don't need
`scrollPosition(id:)` for LazyVGrid column changes" (Forums 847644), so the grid keeps its
place when the count changes.

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

@available(iOS 27.1, *)
struct AlbumGrid: View {
    let albums: [Album]
    private let minimumItemWidth: CGFloat = 150

    var body: some View {
        GeometryReader { proxy in
            let divisions = proxy.reservedRegions(kind: .division, options: .includeInactive)
            let fit = max(1, Int(proxy.size.width / minimumItemWidth))
            let columns = divisions.isEmpty ? fit : max(2, fit - fit % 2)

            ScrollView {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: columns)) {
                    ForEach(albums) { album in
                        AlbumCell(album: album)
                    }
                }
                .padding()
            }
        }
    }
}
```

### B6 ArrangementView in the right container order

Why: Apple states the container rules three times (HIG, Preparing your app, ArrangementView
page). The order below, navigation outside, arrangement in the middle, scrolling content inside
each pane, is this repo's inference from those rules.

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

@available(iOS 27.1, *)
struct NowPlayingScreen: View {
    var body: some View {
        NavigationStack {                       // navigation container outside (HIG)
            ArrangementView {
                NowPlayingView()                // main
            } secondary: {
                LyricsList()                    // detail; its List lives inside the pane
            }
            .arrangementViewStyle(.split)       // main/detail relationship (Tech Talk 111463)
            .navigationTitle("Now Playing")
        }
    }
}

@available(iOS 27.1, *)
struct LyricsList: View {
    @Environment(\.splitArrangementAxis) private var axis   // nil outside a split arrangement

    var body: some View {
        List(lyricLines) { line in
            Text(line.text)
        }
        .listStyle(axis == .horizontal ? .plain : .insetGrouped)
    }
}
```

Overlay variant for a foreground/background relationship (controls over video); the floating
pane collapses itself when it is on top:

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

@available(iOS 27.1, *)
struct PlayerScreen: View {
    var body: some View {
        ArrangementView {
            PlayerControls()                    // primary: trailing/bottom part when partially open
        } secondary: {
            VideoSurface()                      // secondary: leading/top part when partially open
        }
        .arrangementViewStyle(.overlay)
    }
}

@available(iOS 27.1, *)
struct PlayerControls: View {
    @Environment(\.overlayArrangementZIndex) private var zIndex   // read in the pane, not the root

    var body: some View {
        ControlsBar(isCompact: zIndex > 0)      // floating over the video: show the compact bar
    }
}
```

### B7 UIArrangementViewController with z-index

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

@available(iOS 27.1, *)
final class PlayerSceneBuilder {
    func makeRoot(primaryVC: UIViewController, secondaryVC: UIViewController) -> UIViewController {
        let arrangementVC = UIArrangementViewController()
        arrangementVC.setViewController(primaryVC, for: .primary)
        arrangementVC.setViewController(secondaryVC, for: .secondary)
        arrangementVC.updateArrangement(.overlay)

        // Navigation stays outside the arrangement (Tech Talk 111463).
        return UINavigationController(rootViewController: arrangementVC)
    }

    func isPrimaryFloating(in arrangementVC: UIArrangementViewController) -> Bool {
        (arrangementVC.state(for: .primary)?.zIndex ?? 0) > 0
    }
}
```

### B8 Scene geometry hook for games (TN3192)

TN3192 describes comparing `coordinateSpace.bounds.size` in
`windowScene(_:didUpdateEffectiveGeometry:)` and updating assets when
`!geometry.isInteractivelyResizing`. The technote's exact listing is not reproduced in the
report, so this is a composition of the described steps.

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?
    private var lastSceneSize: CGSize = .zero
    private let gameAssetManager = GameAssetManager()

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)    // never UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = GameViewController()
        window.makeKeyAndVisible()
        self.window = window
    }

    func windowScene(_ windowScene: UIWindowScene, didUpdateEffectiveGeometry previousGeometry: UIWindowScene.Geometry) {
        let geometry = windowScene.effectiveGeometry
        guard !geometry.isInteractivelyResizing else { return }
        let size = geometry.coordinateSpace.bounds.size
        guard size != lastSceneSize else { return }
        lastSceneSize = size
        // Fill the new size; prefer changing aspect ratio over letterboxing (HIG).
        gameAssetManager.updateAssets(sceneSize: size)
    }
}
```

### B9 Availability gating

Apple: the iOS 27.1 APIs are "Available on any iPhone or iPad running iOS 27.1+", gate them
"behind availability checks" (Forums 847644); Mac Catalyst builds need
`#if !targetEnvironment(macCatalyst)` (Xcode 27.1 Release Notes).

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

extension UIView {
    /// Frames of currently active fold regions, or empty on older systems and non-folding devices.
    var activeFoldFrames: [CGRect] {
        #if !targetEnvironment(macCatalyst)
        if #available(iOS 27.1, *) {
            return reservedRegions(kind: .division).filter(\.isActive).map(\.frame)
        }
        #endif
        return []
    }
}
```
