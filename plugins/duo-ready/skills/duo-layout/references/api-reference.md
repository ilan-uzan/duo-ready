Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# duo-layout API reference

Every layout-relevant symbol for iPhone Duo, with the signature as Apple publishes it, the
minimum OS, and a status label. Labels: **[Apple]** = Apple documentation, Tech Talk, release
note, technote or an Apple engineer's forum post; **[3P]** = third-party or simulator
observation, unverified; **[Inference]** = this repo's conclusion. Rows marked "verified
2026-10-26" were re-checked on the live developer.apple.com reference page that day.

Contents

1. Size classes and traits
2. Screen, scale, window
3. Scene geometry
4. Safe areas and margins
5. Reserved regions (SwiftUI)
6. Reserved regions (UIKit)
7. Arrangement views (SwiftUI)
8. Arrangement views (UIKit)
9. Hinge (not for layout)
10. Sidebar and corners
11. Info.plist keys in play
12. Availability and compile guards
13. Numbers Apple has not published
14. Gaps a layout answer must not paper over

## 1. Size classes and traits

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `@Environment(\.horizontalSizeClass)`, `@Environment(\.verticalSizeClass)` | SwiftUI size classes; the only sanctioned layout switch | existing | [Apple] Tech Talk 111461 |
| `UITraitCollection.horizontalSizeClass`, `UITraitCollection.verticalSizeClass` | "Use automatic trait tracking to observe ... changes" | existing | [Apple] [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) |
| `registerForTraitChanges(_:handler:)`, `registerForTraitChanges(_:target:action:)` | Named in TN3192 as the observation hooks | existing | [Apple] [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key) |
| `UITraitHorizontalSizeClass`, `UITraitVerticalSizeClass`, `UITraitChangeRegistration`, `unregisterForTraitChanges(_:)` | Used in Apple's examples: `registerForTraitChanges([UITraitHorizontalSizeClass.self, UITraitVerticalSizeClass.self]) { (self: Self, previousTraitCollection: UITraitCollection) in ... }` | existing | [Apple] [Adapting your app when traits change](https://developer.apple.com/documentation/uikit/adapting-your-app-when-traits-change), verified 2026-10-26 |
| `UIDevice.userInterfaceIdiom` | Stays `.phone` on Duo; "Don't use `UIDevice.userInterfaceIdiom` ... for layout decisions" | n/a | [Apple] [Forums 847945](https://developer.apple.com/forums/thread/847945); Preparing your app |
| `UIInterfaceOrientation`, `UIDevice.current.orientation`, `statusBarOrientation`, `interfaceOrientation`, `windowScene.effectiveGeometry.interfaceOrientation` | Remove from layout code; compare width vs height or use size classes | n/a | [Apple] [Three steps](https://developer.apple.com/iphone-duo/prepare/) |
| Overriding `horizontalSizeClass` | "would likely interfere with system updates" | n/a | [Apple] [Forums 847644](https://developer.apple.com/forums/thread/847644) |

Size-class matrix (Tech Talk 111461): outer portrait compact/regular; outer landscape
compact/compact; inner display regular/regular in either rotation.

## 2. Screen, scale, window

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `UIScreen.main` | "ambiguous on two-display devices and will be deprecated in a future release" | n/a | [Apple] Tech Talk 111461 |
| `view.window?.windowScene?.screen` | "Don't store a `UIScreen`"; access it at the moment of use | existing | [Apple] Three steps; Tech Talk 111461 (`let screen = window?.windowScene?.screen`) |
| `traitCollection.displayScale`, `@Environment(\.displayScale)` | Replace `UIScreen.main.scale` | existing | [Apple] Three steps |
| `UIWindow(windowScene:)` | Replace `UIWindow(frame: UIScreen.main.bounds)` | existing | [Apple] Three steps |
| `view.bounds`, `window.bounds` | Replace `UIScreen.main.bounds` | existing | [Apple] Three steps |
| `GeometryReader`, `GeometryProxy` | SwiftUI container geometry | existing | [Apple] Three steps |
| `onGeometryChange(for:of:action:)` | `nonisolated func onGeometryChange<T>(for type: T.Type, of transform: @escaping @Sendable (GeometryProxy) -> T, action: @escaping (T) -> Void) -> some View where T : Equatable, T : Sendable` (a second overload's action takes `(T, T)`) | iOS 16.0+ | [Apple] named in Three steps; declaration from the [reference page](https://developer.apple.com/documentation/swiftui/view/ongeometrychange(for:of:action:)), verified 2026-10-26 |
| `layoutSubviews()`, `viewDidLayoutSubviews()`, `viewWillTransition(to:with:)` | Re-read sizes here "because a fold can resize your app in the middle of a session" | existing | [Apple] Three steps |
| `UIScreen.main.bounds` measured as 466×678 while the app ran on the inner display | Simulator observation | n/a | [3P] blakecrosley.com |

## 3. Scene geometry

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `windowScene(_:didUpdateEffectiveGeometry:)` | Compare `coordinateSpace.bounds` (or `.size`) with the previous value | iOS 27 (TN3192 context) | [Apple] TN3192 |
| `UIWindowScene.effectiveGeometry.coordinateSpace.bounds` | Scene size in points | existing | [Apple] TN3192 |
| `UIWindowScene.Geometry.isInteractivelyResizing` | Skip asset swaps while true | iOS 27 | [Apple] TN3192 |
| `onInteractiveResizeChange(_:)` | SwiftUI counterpart | iOS 27 | [Apple] TN3192 |
| `UISceneSizeRestrictions`, `windowScene.sizeRestrictions?.minimumSize`, `windowResizability(_:)` | Size preferences; "Scene size can't be set directly. It's driven by pose and Split View" | existing / iOS 27 | [Apple] TN3192; Tech Talk 111466 |
| `prefersInterfaceOrientationLocked`, `setNeedsUpdateOfPrefersInterfaceOrientationLocked()` | "not guaranteed to be honored" | existing | [Apple] TN3192 |
| Discrete resize under `UIRequiresFullScreen = YES` | "the scene moves to a `UIScreen` of exactly the same size" | iOS 27 SDK | [Apple] TN3192 |

## 4. Safe areas and margins

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `view.safeAreaInsets`, `view.bounds.inset(by: view.safeAreaInsets)` | Apple's form: `foreground.frame = view.bounds.inset(by: view.safeAreaInsets)`; `backgroundView.frame = view.bounds` | existing | [Apple] Tech Talk 111461 |
| `view.bounds.width - view.safeAreaInsets.left * 2` | Anti-pattern; assumes symmetry | n/a | [Apple] Tech Talk 111461 |
| `ignoresSafeArea()` | Only for background artwork | existing | [Apple] Tech Talk 111461 |
| Layout margins | "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently" | existing | [Apple] Tech Talk 111461 |
| `safeAreaLayoutGuide`, `viewSafeAreaInsetsDidChange()` | Named only in a third-party fix write-up of the asymmetric-inset rule | existing | [3P] skarol.dev |
| `contentMargins(for: .container)` | Appears in one community repo only; not found on any Apple Duo page | unknown | [3P] unverified |
| Fold in `safeAreaInsets` | It is not there: "Safe-area insets alone are not enough" | n/a | [Apple] Forums 847644 |

## 5. Reserved regions (SwiftUI)

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)` | `func reservedRegions(kind: ReservedRegion.Kind, options: ReservedRegion.QueryOptions = [], layoutDirectionBehavior: LayoutDirectionBehavior = .mirrors) -> [ReservedRegion]`; returns regions "that overlap the view, with frames in the view's coordinate space" | iOS 27.1+ | [Apple] [reference](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)) |
| `struct ReservedRegion` | `id: ReservedRegion.ID`, `kind: ReservedRegion.Kind`, `frame: CGRect` (coordinates relative to the view, `(0, 0)` top-leading, "already includes `margins`"), `margins: EdgeInsets` ("Extra space around the reserved area that keeps interactive content clear of it"), `isActive: Bool` ("whether the region currently affects the view"); Equatable, Hashable, Identifiable, Sendable | iOS 27.1+ | [Apple] [ReservedRegion](https://developer.apple.com/documentation/swiftui/reservedregion), verified 2026-10-26 (the report had listed these member names as [3P]) |
| `ReservedRegion.Kind.occlusion` | "An area that covers your content, such as the Dynamic Island, a camera, or window controls" | iOS 27.1+ | [Apple] |
| `ReservedRegion.Kind.division` | "An area where content splits into separate regions, such as the fold of a hinge" | iOS 27.1+ | [Apple] |
| `ReservedRegion.QueryOptions.includeInactive` | Return inactive regions too (the flat fold has zero width) | iOS 27.1+ | [Apple] |
| `LayoutDirectionBehavior.mirrors` (default) / `.fixed` | `.fixed` disables RTL mirroring of frames | iOS 27.1+ | [Apple] |
| Custom `Layout` caveat | `bounds` in `placeSubviews` does not always start at (0,0); compute from (0,0) and add `bounds.origin` | n/a | [Apple] same page |
| `onGeometryChange` as proxy source | Named as an alternative to `GeometryReader` for reading regions | iOS 27.1+ | [Apple] Tech Talk 111463 |
| Regions arrive after the first layout pass; most are inactive by default; the status-bar area of the vertical bar is an active occlusion; the folded outer display reports no regions | Simulator observations | n/a | [3P] iPhone-Duo-by-Examples, SwiftLee |

## 6. Reserved regions (UIKit)

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `UIView.reservedRegions(kind:options:)` | `@MainActor @preconcurrency func reservedRegions(kind: UIView.ReservedRegion.Kind, options: UIView.ReservedRegion.QueryOptions = []) -> [UIView.ReservedRegion]`; "UIKit tracks the regions you read in `updateConstraints()` and runs it again when the regions change" | iOS 27.1+ | [Apple] [reference](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)) |
| `struct UIView.ReservedRegion` | `let frame: CGRect` (view coordinates, points, "already includes `margins`"), `let isActive: Bool`, `let kind: UIView.ReservedRegion.Kind`, `let margins: UIEdgeInsets`; Equatable, Hashable, Identifiable; Objective-C name `UIViewReservedRegion` | iOS 27.1+, iPadOS 27.1+, Mac Catalyst 27.1+, tvOS 27.1+, visionOS 27.1+ | [Apple] [UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion), verified 2026-10-26 |
| `UIView.ReservedRegion.Kind.occlusion` / `.division` | `static let`; division is "A region that splits the view, such as the fold of iPhone Duo" | iOS 27.1+ | [Apple] |
| `UIView.ReservedRegion.QueryOptions.includeInactive` | `static let` | iOS 27.1+ | [Apple] |
| Apple's call forms | `let regions = view.reservedRegions(kind: .division); let frames = regions.map(\.frame)`; `reservedRegions(kind: .occlusion, options: .includeInactive)` | iOS 27.1+ | [Apple] Tech Talk 111463; UIView.ReservedRegion page |
| Spelling | Tech Talk 111461's summary says `UIViewReservedRegion`; that is the Objective-C name. In Swift write `UIView.ReservedRegion` | n/a | [Apple], resolved by the verified page |
| Objective-C selector `reservedRegionsOfKind:options:` | Reported from headers | iOS 27.1+ | [3P] blakecrosley.com |
| Consume in `updateConstraints()`, not `viewDidLayoutSubviews()` | Follows from Apple's tracking statement | n/a | [Inference] |
| Compositional collection layouts do not avoid the fold automatically | Third-party summary of Apple's UIKit Q&A | n/a | [3P] Gubarenko Q6 |

## 7. Arrangement views (SwiftUI)

All iOS 27.1+ / iPadOS 27.1+ (also macOS, tvOS, visionOS, watchOS 27.1). Source:
[ArrangementView](https://developer.apple.com/documentation/swiftui/arrangementview) unless noted.

| Symbol | Signature / notes | Status |
|---|---|---|
| `ArrangementView` | `nonisolated struct ArrangementView<Primary, Secondary> where Primary : View, Secondary : View`; `init(primary: () -> Primary, secondary: () -> Secondary)`; `init(_ configuration: ArrangementViewStyleConfiguration)`; declared in `SwiftUICore` per headers ([3P]) | [Apple] |
| `ArrangementViewStyle` | protocol; `.split` (`SplitArrangementViewStyle`), `.overlay` (`OverlayArrangementViewStyle`); default style is `.split` | [Apple] |
| `SplitArrangementViewStyle.axes(_:)`, `OverlayArrangementViewStyle.axes(_:)` | e.g. `.split.axes(.horizontal)`, `.split.axes(.vertical)` | [Apple] |
| `ArrangementViewStyleConfiguration` | `.primary` / `.secondary` | [Apple] |
| `View.arrangementViewStyle(_:)` | `.arrangementViewStyle(.split.axes(.horizontal))` | [Apple] Preparing your app |
| `View.overlayArrangementEdge(_:)` | "the horizontal edge a view in an overlay arrangement aligns to when the arrangement transitions to landscape" | [Apple] |
| `View.splitArrangementFixedLayoutSize(horizontal: Bool, vertical: Bool)` | | [Apple] |
| `View.splitArrangementLayoutRatio(_: CGFloat?)` | | [Apple] |
| `View.splitArrangementLayoutRatio(minHorizontal:idealHorizontal:maxHorizontal:minVertical:idealVertical:maxVertical:)` | | [Apple] |
| `View.splitArrangementLayoutSize(minWidth:idealWidth:maxWidth:minHeight:idealHeight:maxHeight:)` | | [Apple] |
| `EnvironmentValues.overlayArrangementZIndex` | `var overlayArrangementZIndex: Int { get set }`; "Views with a higher z-index are rendered on top of views with a lower z-index"; Apple: `zIndex > 0 ? .collapsed : .expanded` | [Apple] [reference](https://developer.apple.com/documentation/swiftui/environmentvalues/overlayarrangementzindex), verified 2026-10-26; Tech Talk 111463 |
| `EnvironmentValues.splitArrangementAxis` | `var splitArrangementAxis: Axis? { get set }`; "The value is `nil` when the view is not contained within a split arrangement view" | [Apple] [reference](https://developer.apple.com/documentation/swiftui/environmentvalues/splitarrangementaxis), verified 2026-10-26 |
| Behaviour | Inputs: "horizontal and vertical size classes, the view's width-to-height aspect ratio, and any active division regions"; outputs: "whether each view is shown and its frame"; "If the arrangement cannot split along its primary axis, it shows only one view"; "When a closed iPhone Duo is held in landscape, only the primary view is shown" | [Apple] Tech Talk 111463 |
| Container rules | Keep navigation outside; do not nest in `List`, `ScrollView`, `NavigationSplitView`, grid; do not put `NavigationSplitView` or `TabView` inside | [Apple] HIG; Preparing your app; ArrangementView page |
| In book pose `.split` puts its divider on the fold even with a ratio set; avoid `maxHorizontal`; `splitArrangementFixedLayoutSize` overrides the fold; root view always reads `overlayArrangementZIndex == 0`; `splitArrangementAxis` read nil in that repo's tests | Simulator observations | [3P] iPhone-Duo-by-Examples |

## 8. Arrangement views (UIKit)

All iOS 27.1+, iPadOS 27.1+, Mac Catalyst 27.1+, tvOS 27.1+, visionOS 27.1+. Source:
[UIArrangementViewController](https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller).

| Symbol | Signature / notes | Status |
|---|---|---|
| `UIArrangementViewController` | `@MainActor class UIArrangementViewController : UIViewController`; `init()` | [Apple] |
| `setViewController(_:for:animated:)` | `setViewController(_: UIViewController?, for: ViewPlacement, animated: Bool)`; ObjC `setViewController:forPlacement:animated:`; Apple's example calls `setViewController(primaryVC, for: .primary)` | [Apple] |
| `viewController(for:)` | `-> UIViewController?` | [Apple] |
| `placement(for:)` | `placement(for: UIViewController) -> ViewPlacement?` | [Apple] |
| `updateArrangement(_:animated:)` | `updateArrangement<A>(_: A, animated: Bool)`; Apple's example: `updateArrangement(.split.axes(.vertical))` | [Apple] |
| `state(for:)` | `state(for: ViewPlacement) -> ViewState?`; `ViewState` exposes `zIndex`: `(primaryState?.zIndex ?? 0) > 0 ? .collapsed : .expanded` | [Apple] Tech Talk 111463 |
| `UIArrangementViewController.Arrangement` | protocol; `static var overlay: UIOverlayArrangement`, `static var split: UISplitArrangement` | [Apple] |
| `UIArrangementViewController.ViewPlacement` | `.primary`, `.secondary`; ObjC `UIArrangementViewControllerViewPlacementPrimary/Secondary/None` | [Apple] |
| `UIArrangementViewController.ViewState` | ObjC `UIArrangementViewState` | [Apple] |
| `UISplitArrangement`, `UIOverlayArrangement` | `struct UISplitArrangement { func axes(_: UIAxis) -> UISplitArrangement }`; `struct UIOverlayArrangement { func axes(_: UIAxis) -> UIOverlayArrangement }`; ObjC `+splitArrangement` / `+overlayArrangement`, `arrangement.axes = UIAxisVertical` | [Apple] |
| Delegate | None documented | [Apple] |
| Wrap in `UINavigationController(rootViewController: arrangementVC)` | Navigation outside the arrangement | [Apple] Tech Talk 111463 |

## 9. Hinge (not for layout)

Listed so you can recognise it in code; "For layout decisions, use the arrangement and region
APIs" (Tech Talk 111464). Full detail is in `duo-scenes`.

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `onHingeChange(isEnabled:_:)` | `nonisolated func onHingeChange(isEnabled: Bool = true, _ action: @escaping (DeviceHingeContext, DeviceHingeContext) -> Void) -> some View`; `DeviceHingeContext.hinge: DeviceHinge?`; `DeviceHinge.angle: Angle`, `.status: DeviceHinge.Status` | iOS 27.1+ | [Apple] |
| `UIHingeInteraction`, `UIHinge` | `init(updateHandler:)`; `UIHinge.angle: CGFloat` in radians; `status: UIHinge.Status` | iOS 27.1+ | [Apple] |
| Status cases | SwiftUI `DeviceHinge.Status`: `.closed`, `.partiallyOpen`, `.fullyOpen`; UIKit `UIHinge.Status`: `.unknown`, `.closed`, `.partiallyOpen`, `.fullyOpen` (iOS 27.1 SDK headers, 27A9275, read 2026-10-27) | iOS 27.1+ | [Apple SDK] |
| Angle thresholds for tent / laptop / book | None published; "Update rate and precision are system policy, so don't depend on specific values" | n/a | [Apple] Forums 847644 |

## 10. Sidebar and corners

| Symbol | Signature / notes | Min OS | Status |
|---|---|---|---|
| `TabView { … }.defaultTabBarPlacement(.sidebar)` | Opt into a sidebar on the inner display; not automatic on iPhone | iOS 27 | [Apple] Tech Talk 111461 |
| `tabBarController.sidebar.preferredPlacement = .sidebar` | UIKit counterpart | iOS 27 | [Apple] Forums 847912 |
| `ConcentricRectangle`, `UICornerConfiguration` | Match display corners: `ConcentricRectangle().fill(Color.green).padding(8.0).ignoresSafeArea()` | iOS 26 | [Apple] Tech Talk 111461 |
| `NavigationSplitView`, `UISplitViewController` | Split views "expand on the inner display and collapse to a single pane on the outer display"; no Duo-specific API | existing | [Apple] HIG |

## 11. Info.plist keys in play

| Key | Effect on Duo | Status |
|---|---|---|
| `UISupportedInterfaceOrientations` | Honoured on the outer display; the inner display ignores supported orientations (Tech Talk 111461; Forums 847644, which also contains a compatibility-mode answer saying the key is "still honored" with different expected behaviour; rely on neither for layout) | [Apple] |
| `UIRequiresFullScreen` | iOS 27 SDK: no longer opts out of resizing; scene resizes discretely; still resizes on open/close | [Apple] TN3192; Tech Talk 111461 |
| `UIRequiresFullScreenIgnoredStartingWithVersion`, `INFOPLIST_KEY_UIRequiresFullScreen` | Related build/plist settings | [Apple] TN3192 |
| Any Duo-specific key | None exists; "iPhone Duo is not a separate device class" | [Apple] Forums 847644 |

## 12. Availability and compile guards

| Guard | Notes | Status |
|---|---|---|
| `if #available(iOS 27.1, *)` | Apple recommends "gating iOS 27.1 APIs behind availability checks"; the APIs are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo" | [Apple] Forums 847644 |
| `#if !targetEnvironment(macCatalyst)` | iOS 27.1-only APIs produce compile errors in Mac Catalyst builds (185924957) | [Apple] Xcode 27.1 Release Notes |
| `#if canImport(SwiftUI, _version: 8.0.85)` | Reported workaround for building under Xcode 27.0 where the symbols do not exist | [3P] blakecrosley.com |
| Header annotations `@available(anyAppleOS 27.1, *)`, `API_AVAILABLE(ios(27.1), tvos(27.1), visionos(27.1))` | Observed in headers | [3P] |

## 13. Numbers Apple has not published

Everything in points is third-party. Never let layout depend on them.

| Quantity | Value | Status |
|---|---|---|
| Inner panel | 1878×2670 px, 430 ppi | [Apple] Tech Specs |
| Outer panel | 1398×2034 px, 460 ppi | [Apple] Tech Specs |
| ASC screenshot sizes | outer 1398×2034, inner 2007×2853 | [Apple] ASC |
| Outer points | 466×678 pt @3x | [3P] simulator profile |
| Inner points | 669×951 pt @3x (951×669 landscape-native) | [3P] simulator; arithmetic matches ASC [Inference] |
| Vertical bar inset | about 84 pt, one side | [3P] simulator |
| Fold division region | 40 pt wide (20 pt margins), active only when partially folded | [3P] simulator |
| Window content sizes under the 27.1 SDK | closed 466×678 (content 382×562); open 951×669 (content 867×553, inactive division at x=455); open rotated 669×951 (content 669×734) | [3P] blakecrosley.com |

## 14. Gaps a layout answer must not paper over

- Point dimensions and scale factor: not published by Apple.
- Exact Split View point sizes; whether three-column split views appear on the inner display.
- `viewWillTransition(to:with:)` behaviour on fold: Apple only says the app "resizes".
- Whether the `UIScreen` instance changes identity between displays.
- Hinge angle thresholds between poses: none.
- `contentMargins(for: .container)` as a Duo API: unverified.
- `DeviceHinge.Status` / `UIHinge.Status` case list: resolved from the iOS 27.1 SDK headers (see the table above).
- No Apple sample project exists; Apple's only runnable artifact is the App Resizability skill.
