Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Triage playbook

For each class of scanner finding: what to look at in the user's code before
you speak, the fix Apple states, and which duo-ready skill to open for the
detailed work. Apple statements carry an inline source. Repo priorities (P0,
P1, P2) are ours. Anything marked (heuristic) is a detection approximation;
confirm it by reading the code. Anything marked (third-party, unverified) is
not Apple's.

Contents

1. SDK tier and toolchain: DUO-019, DUO-020
2. Lifecycle and submission blockers: DUO-009, DUO-010, DUO-003, DUO-008
3. Screen and cached geometry: DUO-001, DUO-002, DUO-023
4. Idiom, orientation and device sniffing: DUO-004, DUO-005, DUO-006, DUO-007, DUO-015
5. Hard-coded sizes and breakpoints: DUO-011, DUO-012
6. Safe areas: DUO-022, DUO-016
7. Bars: DUO-017, DUO-018
8. Media: DUO-013, DUO-014
9. Web and cross-platform: DUO-021, DUO-030 to DUO-033
10. What the scanner cannot see
11. Reading the "Already adopted" section

## 1. SDK tier and toolchain: DUO-019, DUO-020

DUO-019 Project not upgraded to Xcode 27.1 (heuristic, P1)

- Look at: the `LastUpgradeCheck` value in `project.pbxproj`, and ask which
  Xcode produces the shipping build. The value is a proxy for the Xcode that
  last upgraded the project; a CI machine may build with a different Xcode.
- Fix: build with Xcode 27.1 (iOS 27.1 SDK) and re-test every pose; the inner
  display tier follows the build SDK (https://developer.apple.com/iphone-duo/prepare/).
  To check a binary, `otool -l <binary> | grep -A4 LC_BUILD_VERSION` should
  read `sdk 27.1` (third-party, unverified).
- Open: stay in `duo-audit` (see `references/sdk-tiers-and-three-steps.md`);
  `duo-ship` for the release checklist.

DUO-020 iOS 27.1-only API in a Mac Catalyst target without a guard (cited, P1)

- Look at: `SUPPORTS_MACCATALYST = YES` in the pbxproj plus any file using
  `ArrangementView`, `reservedRegions(`, `onHingeChange`, `UIHingeInteraction`,
  `CameraCaptureAccessory`, the vertical-bar modifiers or
  `AVCaptureDeviceDirectionCoordinator` without `targetEnvironment(macCatalyst)`.
- Fix: wrap the call in `#if !targetEnvironment(macCatalyst)` (Xcode 27.1
  Release Notes, 185924957,
  https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)
  and gate with `if #available(iOS 27.1, *)`, which Apple recommends for all
  27.1 APIs (https://developer.apple.com/forums/thread/847644). Targeting iOS
  27.1 shows no Catalyst run destination (187046347); the documented workaround
  is a Mac Catalyst 27.0 minimum deployment.
- Open: the skill that owns the API (`duo-layout`, `duo-bars`, `duo-scenes`
  or `duo-camera`).

## 2. Lifecycle and submission blockers: DUO-009, DUO-010, DUO-003, DUO-008

DUO-009 No scene lifecycle (cited, P0)

- Look at: Info.plist for `UIApplicationSceneManifest` (or the build setting
  `INFOPLIST_KEY_UIApplicationSceneManifest_Enabled`), a type conforming to
  `UIWindowSceneDelegate`, or a SwiftUI `App`. The rule fires only when a
  `UIApplicationDelegate` exists and none of those do.
- Fix: add `UIApplicationSceneManifest`, add a `UIWindowSceneDelegate`, and
  move window creation into `scene(_:willConnectTo:options:)`. Apple's UIKit
  Q&A reportedly said "Xcode 27 requires the scene lifecycle, so migrate first"
  (third-party summary of Apple answers); React Native 0.88.0-rc.0 failed to
  launch with "UIScene life cycle is required for apps built with this SDK"
  (https://github.com/react/react-native/issues/58606, third-party).
- Open: `duo-scenes`.

DUO-010 No launch screen (cited, P0)

- Look at: Info.plist for `UILaunchScreen` or `UILaunchStoryboardName`, or the
  build settings `INFOPLIST_KEY_UILaunchScreen_Generation` /
  `INFOPLIST_KEY_UILaunchStoryboardName`.
- Fix: add one. "Starting in iOS 27 and iPadOS 27, a launch screen is required
  for App Store submission" (TN3192,
  https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key).
- Open: `duo-ship`.

DUO-003 UIWindow created from a frame (cited, P1)

- Look at: `UIWindow(frame:)` / `initWithFrame:` in the app delegate or a
  window manager; usually paired with DUO-001 on the same line.
- Fix: `UIWindow(windowScene:)` from the scene delegate; Apple lists
  `UIWindow(frame: UIScreen.main.bounds)` among the patterns to replace
  (https://developer.apple.com/iphone-duo/prepare/).
- Open: `duo-scenes`.

DUO-008 UIRequiresFullScreen = YES (cited, P1)

- Look at: Info.plist `UIRequiresFullScreen` or the build setting
  `INFOPLIST_KEY_UIRequiresFullScreen`; also `UIRequiresFullScreenIgnoredStartingWithVersion`.
- Fix: remove the key. TN3192: "Starting in iOS 27 and iPadOS 27,
  `UIRequiresFullScreen` no longer opts your app out of resizing on either
  platform. Instead, the system resizes your app's scene discretely." On Duo
  "The app continues to honor `UIRequiresFullScreen`, but still resizes when
  the device opens or closes" (Tech Talk 111461). TN3192's migration list:
  provide a launch screen, support all interface orientations, remove the key;
  observe geometry via `windowScene(_:didUpdateEffectiveGeometry:)` and
  `UIWindowScene.Geometry.isInteractivelyResizing`.
- Open: `duo-scenes` (geometry observation) and `duo-ship` (TN3192 checklist).

## 3. Screen and cached geometry: DUO-001, DUO-002, DUO-023

DUO-001 UIScreen.main used for layout (cited, P0)

- Look at: what the bounds feed. A cached `static let screenWidth =
  UIScreen.main.bounds.width` is the worst case: it is read once and never
  updated when the fold resizes the scene. Also look for stored `UIScreen`
  references.
- Fix: `view.bounds` / `window.bounds`; SwiftUI `GeometryReader` or
  `onGeometryChange`; re-read in `layoutSubviews` / `viewDidLayoutSubviews`;
  `viewWillTransition(to:with:)` for work that must run on resize; "Don't
  store a `UIScreen`", reach it via `view.window?.windowScene?.screen`
  (https://developer.apple.com/iphone-duo/prepare/). `UIScreen.main` is
  "ambiguous on two-display devices and will be deprecated in a future release"
  (Tech Talk 111461).
- Field note (third-party, unverified): one open-source reader required
  `UIScreen.main.bounds.width > 900` for two-page mode, so it never appeared on
  the inner display; another developer measured `UIScreen.main.bounds`
  returning the outer display's size while the app ran on the inner display.
- Open: `duo-layout`.

DUO-002 UIScreen.main.scale (cited, P1)

- Look at: image rendering, `CGContext` creation, pixel snapping.
- Fix: `traitCollection.displayScale` (UIKit) or
  `@Environment(\.displayScale)` (SwiftUI) (Tech Talk 111461).
- Open: `duo-layout`.

DUO-023 Window frame read from `UIApplication.shared.windows` / `keyWindow` (heuristic, P1)

- Look at: whether the frame or safe-area insets are cached. Reading the key
  window to present an alert is not a layout problem; capturing its frame into
  a constant is.
- Fix: read geometry from the view's own window or window scene at layout
  time. The rule's source field says no Apple statement names this exact API;
  the reasoning is Apple's "re-read size on resize" rule.
- Open: `duo-layout`.

## 4. Idiom, orientation and device sniffing: DUO-004, DUO-005, DUO-006, DUO-007, DUO-015

DUO-004 userInterfaceIdiom used to choose a layout (cited, P0)

- Look at: every branch on `.pad` / `.phone`. Features gated on `.pad`
  disappear on Duo, which reports `.phone`: "its device idiom is still
  `.phone`" (https://developer.apple.com/forums/thread/847945). A third-party
  report lost an Apple Pencil hover preview this way.
- Fix: branch on `traitCollection.horizontalSizeClass` /
  `verticalSizeClass` or the SwiftUI environment values, and on the
  container's bounds. "Don't choose a layout by idiom"; "Don't treat 'regular
  width' as 'iPad.'" (https://developer.apple.com/iphone-duo/prepare/). The
  inner display is regular/regular in both rotations; the outer is
  compact/regular in portrait and compact/compact in landscape (Tech Talk
  111461). Check both size classes, not width alone.
- Open: `duo-layout`.

DUO-005 Device or interface orientation used for layout (cited, P0)

- Look at: `UIDevice.current.orientation`, `statusBarOrientation`,
  `interfaceOrientation`, `windowScene.effectiveGeometry.interfaceOrientation`,
  and `orientationDidChangeNotification` observers that trigger relayout.
- Fix: compare available width to height, or use size classes
  (https://developer.apple.com/iphone-duo/prepare/). "The inner display
  doesn't honor supported interface orientations, so use size classes rather
  than orientation for layout decisions" (Tech Talk 111461). Observe geometry
  via `viewWillTransition(to:with:)` or `windowScene(_:didUpdateEffectiveGeometry:)`.
- Open: `duo-layout`.

DUO-006 `supportedInterfaceOrientations` override is portrait-only (cited, P1)
DUO-007 Info.plist `UISupportedInterfaceOrientations` is portrait-only (cited, P1)

- Look at: whether the app assumes a tall, narrow canvas because it is locked
  to portrait. On the inner display that assumption fails: a third-party
  report describes "Tall, narrow layouts appear wide and short on the inner
  display".
- Operative Apple guidance: asked whether there is a sanctioned way to lock the
  inner display to portrait only, the Group Lab summary answers that there is
  not: "The inner display doesn't honor your supported interface orientations
  — avoid checking orientation for layout decisions and use size classes
  instead", and "Portrait-only apps ... still receive compact and regular size
  class changes. The outer display honors supported orientations, but the inner
  display ignores them" (https://developer.apple.com/forums/thread/847644).
  The same thread, answering a compatibility-mode question, also contains the
  wording "Yes, iPhone Duo still honors `UISupportedInterfaceOrientations`,
  but the expected behavior for this device differs from previous iPhone
  devices in certain hinge states and orientations"; either way a
  portrait-only app must handle regular size classes on the inner display.
- Fix: support all orientations (TN3192's migration checklist) and lay out from
  size classes. Games may lock orientation but "be sure to fill the screen as
  the device pose changes ... Prefer changing the aspect ratio over
  letterboxing or pillarboxing" (HIG,
  https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo).
  TN3192 notes that orientation lock requests via
  `prefersInterfaceOrientationLocked` plus
  `setNeedsUpdateOfPrefersInterfaceOrientationLocked()` are not guaranteed to
  be honored. No `UIRequiresFixedInterfaceOrientation` key exists (a forum
  request, third-party).
- Open: `duo-layout`.

DUO-015 Device model string sniffed for layout (cited, P1)

- Look at: `utsname`, `hw.machine`, `UIDevice.current.model` tables and
  `"iPhoneNN,N"` literals. Analytics-only use is a `duo-backend` topic, not a
  layout bug; layout use is the bug.
- Fix: delete model tables for layout. "Design from size, traits, and reserved
  regions, not hardware names or screen dimensions" (third-party summary of
  Apple's UIKit Q&A); Duo has no `UIUserInterfaceIdiom` of its own
  (https://developer.apple.com/forums/thread/847644). The identifier
  `iPhone19,4` is third-party and Apple publishes no identifier table.
- Open: `duo-layout`; `duo-backend` for analytics properties.

## 5. Hard-coded sizes and breakpoints: DUO-011, DUO-012

DUO-011 Hard-coded iPhone screen dimension compared against width/height (heuristic, P0)
DUO-012 Magic width/height breakpoint (heuristic, P1)

- Look at: whether the literal is a device size (DUO-011 matches a fixed list
  of known iPhone point sizes) or a content threshold (DUO-012 matches any
  three- or four-digit comparison against a width/height). A minimum column
  width derived from content is legitimate; a `height == 844` check is not.
  Lines mentioning `sizeClass` are vetoed automatically.
- Fix: size relative to the container and choose layouts from size classes:
  "Remove checks for specific device sizes" (https://developer.apple.com/iphone-duo/prepare/);
  "avoid fixed widths, breakpoints, and metrics tied to a specific screen"
  (Tech Talk 111466). Do not replace the literal with a Duo point size; Apple
  publishes none.
- Open: `duo-layout`.

## 6. Safe areas: DUO-022, DUO-016

DUO-022 Symmetric safe-area math (cited, P0)

- Look at: `safeAreaInsets.left * 2`, `2 * safeAreaInsets.right`,
  `max(left, right)` used to center content. On Duo the vertical bar adds a
  one-sided inset, so symmetric math shifts content off centre.
- Fix: `view.bounds.inset(by: view.safeAreaInsets)` or
  `safeAreaLayoutGuide`, reading each side separately. Tech Talk 111461 shows
  `view.bounds.width - view.safeAreaInsets.left * 2` as the anti-pattern and
  states "Safe areas and layout margins are often asymmetric on iPhone Duo.
  Handle each side independently." Bars sit outside the safe area; horizontal
  bars provide top/bottom insets, vertical bars provide leading/trailing insets.
- Field notes (third-party, unverified): the side column measured about 84 pt;
  a close button pinned top-trailing vanished under the clock; nested scroll
  views reported zero side safe area.
- Open: `duo-layout`.

DUO-016 Status bar hidden, side inset still applies (heuristic, P2)

- Look at: screens that hide the status bar to reclaim space, and whether
  their content uses `.ignoresSafeArea()` / `edgesIgnoringSafeArea` for
  anything other than a background.
- Fix: constrain foreground content to the safe area; keep
  `.ignoresSafeArea()` for backgrounds only; verify these screens in the Duo
  simulator. The Apple rule is the asymmetric safe-area statement above; the
  observation that hiding the status bar hides the icons but not the inset is
  a third-party report (skarol.dev) and must be labelled as such.
- Open: `duo-layout`; `duo-bars` if the intent was to free the side column.

## 7. Bars: DUO-017, DUO-018

DUO-017 Custom tab/tool bar built from plain views (heuristic, P1)

- Look at: the matched type. The rule matches `class`/`struct` names
  containing TabBar, ToolBar, BottomBar, NavBar or NavigationBar that inherit
  from `UIView`, `UIStackView`, `UIControl`, `UIVisualEffectView` or SwiftUI
  `View`. A `struct ToolbarTitleView: View` used inside `.toolbar {}` is a
  false positive; an `HStack` of buttons pinned to the bottom is the real
  thing.
- Fix: "In SwiftUI, add the `toolbar(content:)` modifier to a
  `NavigationStack` or `NavigationSplitView`. In UIKit, set toolbar items on a
  view controller that you add to a navigation controller, instead of creating
  a custom bar for your view based on `UIToolbar`, `UINavigationBar`, or
  `UITabBar`" (https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo).
  Tabs: `UITabBarController` or `TabView`. "Content from custom `UIToolbar`,
  `UINavigationBar`, or `UITabBar` instances isn't considered" (Tech Talk
  111462). Sidebars are opt-in: `tabBarController.sidebar.preferredPlacement =
  .sidebar` (https://developer.apple.com/forums/thread/847912) or
  `TabView { … }.defaultTabBarPlacement(.sidebar)` (Tech Talk 111461).
- After the container fix, check item rules by reading the code: "If your item
  has a title and doesn't have an icon, the system doesn't present it
  vertically. / If your item uses a custom view rather than a title or icon,
  the system doesn't present it vertically" (Technology Overview). The scanner
  does not check this.
- Open: `duo-bars`.

DUO-018 Navigation bar hidden (heuristic, P2)

- Look at: why it is hidden. A hero image under a transparent bar is a
  different fix from a custom header replacing the bar.
- Fix: keep the system bar and add items via `.toolbar(content:)` or
  `navigationItem`; extend hero art under the bar with
  `View.backgroundExtensionEffect()` or `UIBackgroundExtensionView`
  (Technology Overview). Where bars truly are not needed, the HIG allows full
  width "as long as nothing conflicts with the Dynamic Island or the status
  bar" (https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo).
- Open: `duo-bars`.

## 8. Media: DUO-013, DUO-014

DUO-013 Fill content mode on media without a focal point (heuristic, P2)

- Look at: whether the media is a hero image or a thumbnail. Lines mentioning
  a focal point, focus or size class are vetoed. Thumbnails in a grid are
  usually fine; a full-bleed header is the case Apple describes.
- Fix: "Hero images and video set to `.scaleAspectFill` or
  `.aspectRatio(contentMode: .fill)` can lose important content on wider
  displays. Use the current size classes or aspect ratio to choose between
  fill and fit, or set a focal point" (https://developer.apple.com/iphone-duo/prepare/).
- Open: `duo-layout`; `duo-design` for the art direction decision.

DUO-014 Fixed 16:9 aspect ratio (heuristic, P2)

- Look at: whether the ratio is the media's intrinsic ratio (a video's own
  frame, legitimate) or a layout constraint forcing a container to 16:9.
- Fix: let players and media fill the available bounds; AVKit resizes
  automatically and playback persists through hinge changes
  (https://developer.apple.com/forums/thread/847644). "Don't assume fixed
  ratios. Resize to fit each pose, favor changing aspect ratio over
  letterboxing, and add artwork to unavoidable padding" (Group Lab summary;
  Tech Talk 111466; HIG). Do not quote the inner display's aspect ratio as a
  number; Apple does not.
- Open: `duo-layout`; games to `duo-design`.

## 9. Web and cross-platform: DUO-021, DUO-030 to DUO-033

DUO-021 WKWebView content cannot see the fold (cited, P2)

- Look at: whether the page lays itself out from `window.innerWidth` cached at
  load, uses user-agent sniffing, or relies on CSS safe-area insets to avoid
  the fold.
- Fix: "Query geometry in the host and pass it to the page. Viewport-segment
  and posture APIs are experimental Safari features, not available in
  WKWebView. CSS insets don't account for the fold" (third-party summary of
  Apple's UIKit Q&A). "There's no API for web pages to detect iPhone Duo
  specifically. Use responsive design instead" (https://developer.apple.com/forums/thread/847644).
- Open: `duo-backend` (web and WKWebView); `duo-crossplatform` for hybrid apps.

DUO-030 React Native (cited, P1)

- Look at: the RN version in `package.json`, the presence of a scene delegate,
  and module-scope `Dimensions.get('window')`.
- Fix: upgrade to RN 0.88 or add `SceneDelegate.swift` plus
  `UIApplicationSceneManifest` and move `UIWindow` creation out of the
  AppDelegate; Expo: `expo-build-properties` with
  `"ios": {"enableSceneSupport": true}` (https://github.com/react/react-native/issues/58606,
  third-party). `useWindowDimensions()` instead of module-scope `Dimensions`
  (third-party, unverified).
- Open: `duo-crossplatform`.

DUO-031 Flutter (cited, P2)

- Look at: `setPreferredOrientations`, multi-window expectations,
  `MediaQuery.displayFeatures`.
- Fix: the inner display ignores declared orientations (Tech Talk 111461);
  Flutter multi-scene is tracked in flutter #193056, a duplicate of #48838
  (third-party). `MediaQuery.displayFeatures` is documented for Android only
  and returns empty on Duo (third-party, unverified).
- Open: `duo-crossplatform`.

DUO-032 Capacitor/Ionic (cited, P2)

- Look at: the web layer's safe-area and viewport handling.
- Fix: pass fold geometry from the native host into the page; the web content
  has no fold API (same Apple statements as DUO-021). `viewport-fit=cover`,
  per-side `env()` insets, `100dvh`, `ResizeObserver` are third-party,
  unverified guidance.
- Open: `duo-crossplatform`.

DUO-033 Unity (cited, P2)

- Look at: cached `Screen.width/height`, fixed-aspect letterboxing,
  symmetric `Screen.safeArea` math.
- Fix: HIG for games: "fill the screen as the device pose changes ... Prefer
  changing the aspect ratio over letterboxing or pillarboxing in games; if you
  can't avoid letterboxing or pillarboxing, add artwork to the padding area"
  (https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo).
  No Unity-specific Apple guidance exists; polling `Screen.width/height` each
  frame is third-party advice.
- Open: `duo-crossplatform`.

## 10. What the scanner cannot see

Raise these from reading the code and from the simulator, not from the report:

- Camera. No rule. If the app captures from a front camera, open
  `duo-camera`: "a front camera is not always looking at you" and
  `AVCaptureDevice.position` is insufficient; use
  `AVCaptureDeviceDirectionCoordinator`
  (https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces).
- Toolbar items with a title and no icon, or with custom views; they are not
  presented vertically and can leave an empty rail (Technology Overview; a
  third-party report saw exactly this with a text-only "Done"). Open `duo-bars`.
- Centered content and odd column counts on the fold: "prefer an even number
  of columns so content divides cleanly. Use the `ReservedRegion` API to keep
  important elements clear of the center if the system doesn't move them
  automatically" (HIG). Custom bottom sheets "need fold avoidance using
  reserved regions. Safe-area insets alone are not enough"
  (https://developer.apple.com/forums/thread/847644). Open `duo-layout`.
- Stale navigation after a fold (a detail pushed in compact width staying
  full-width after unfolding; third-party report). Open `duo-layout` and
  `duo-scenes`.
- View hierarchies rebuilt on size-class change, which lose scroll and
  selection; Apple treats the fold as "a size-class and trait change, not a
  scene disconnect" (https://developer.apple.com/forums/thread/847644). Open
  `duo-scenes`.
- Sheet placement on the inner display (`View.presentationPlacement(_:)` /
  `UISheetPresentationController.preferredPlacement`, Technology Overview).
  Open `duo-bars`.
- Dynamic Type at the largest sizes: "For fixed one-screen layouts, holding
  text at the largest standard size can fail App Store Connect's Larger Text
  criteria" (https://developer.apple.com/forums/thread/847644).
- Screenshots and the April 2027 rule. Open `duo-ship`.

## 11. Reading the "Already adopted" section

The scanner lists positive keyword hits: size classes, `displayScale`,
geometry observation (`onGeometryChange`, `viewWillTransition(to:`,
`didUpdateEffectiveGeometry`, `registerForTraitChanges`,
`viewSafeAreaInsetsDidChange`), scene-based windows, reserved regions,
arrangement views, hinge APIs, scene accessories, vertical bar APIs, camera
direction coordinator, background extension, sheet placement, iOS 27.1
availability gating, multiple scenes, and `UIApplicationSceneManifest`.

Treat each entry as "this symbol appears at least once", nothing more. It does
not mean the symbol is used on the right view, that availability is gated, or
that the build SDK exposes it. When a user has adopted `ArrangementView`,
check the container rule by hand: "Avoid placing an arrangement view inside a
navigation split view, list, scroll view, or other container that might cause
part of your view to become inaccessible" (Technology Overview); and "not
every app needs to use Arrangement Views or the reserved regions API"
(https://developer.apple.com/forums/thread/847887).
