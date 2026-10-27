Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# duo-audit rule table

The table and the per-rule details below are generated from the `RULES` tuple
in `scripts/duo_audit.py` (version 1.0.0). To refresh them, run
`python3 -I scripts/duo_audit.py --list-rules` from the skill directory and
compare; if a row differs, the script is the source of truth. Do not add rules
here. New rules go into the `RULES` table with a fixture line and a test, as
CONTRIBUTING.md describes.

Contents

1. How to read the columns
2. Rule table (27 rows)
3. Rule details (why and fix, verbatim from the script)
4. Severity and kind counts

## 1. How to read the columns

- ID: stable identifier used in reports and in inline suppressions
  (`// duo-audit: ignore DUO-003`). Ids DUO-024 to DUO-029 are unused;
  DUO-030 to DUO-033 are the cross-platform project rules.
- Severity: P0 = the app is wrong or will not ship; P1 = visibly broken on one
  display; P2 = degraded or needs a manual check. These priorities are the
  repo's, derived from Apple's statements and field reports; Apple does not
  rank its grep list.
- Kind: `cited` means the detected pattern is one Apple names; `heuristic`
  means the detection is a pattern-matching approximation of an Apple rule and
  false positives are expected. Confirm heuristic hits by reading the code.
  DUO-023's source field says explicitly that no Apple statement covers the
  exact pattern.
- Source: the Apple page, Tech Talk or Developer Forums thread the rule rests
  on. Where a non-Apple URL appears (react-native issue #58606, flutter issue
  #193056, skarol.dev, the Gubarenko substack summary of Apple's UIKit Q&A), it
  is a third-party record of a field report or of Apple's spoken answers and is
  labelled as such in the rule text.

## 2. Rule table

Rule count: 27 (7 P0, 12 P1, 8 P2); 18 cited, 9 heuristic.

| ID | Severity | Kind | Title | Source |
|---|---|---|---|---|
| DUO-001 | P0 | cited | UIScreen.main used for layout | https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ |
| DUO-002 | P1 | cited | UIScreen.main.scale used instead of displayScale | Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; https://developer.apple.com/iphone-duo/prepare/ |
| DUO-003 | P1 | cited | UIWindow created from a frame instead of a window scene | https://developer.apple.com/iphone-duo/prepare/ |
| DUO-004 | P0 | cited | userInterfaceIdiom used to choose a layout | https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo ; https://developer.apple.com/iphone-duo/prepare/ ; https://developer.apple.com/forums/thread/847644 |
| DUO-005 | P0 | cited | Device or interface orientation used for layout | https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ |
| DUO-006 | P1 | cited | supportedInterfaceOrientations override is portrait-only | https://developer.apple.com/forums/thread/847644 ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key |
| DUO-007 | P1 | cited | Info.plist UISupportedInterfaceOrientations is portrait-only | https://developer.apple.com/forums/thread/847644 ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ |
| DUO-008 | P1 | cited | UIRequiresFullScreen = YES (deprecated) | https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ |
| DUO-009 | P0 | cited | No scene lifecycle (UIApplicationSceneManifest / scene delegate missing) | Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://github.com/react/react-native/issues/58606 |
| DUO-010 | P0 | cited | No launch screen (UILaunchScreen / UILaunchStoryboardName) | https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key |
| DUO-011 | P0 | heuristic | Hard-coded iPhone screen dimension compared against width/height | https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/ |
| DUO-012 | P1 | heuristic | Magic width/height breakpoint | Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/ |
| DUO-013 | P2 | heuristic | Fill content mode on media without a focal point | https://developer.apple.com/iphone-duo/prepare/ |
| DUO-014 | P2 | heuristic | Fixed 16:9 aspect ratio | https://developer.apple.com/forums/thread/847644 ; Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/ ; https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo |
| DUO-015 | P1 | cited | Device model string sniffed for layout | Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://developer.apple.com/forums/thread/847644 |
| DUO-016 | P2 | heuristic | Status bar hidden - side inset still applies | Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; report: https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/ |
| DUO-017 | P1 | heuristic | Custom tab/tool bar built from plain views | https://developer.apple.com/forums/thread/847644 ; https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo |
| DUO-018 | P2 | heuristic | Navigation bar hidden (custom top bar will not go vertical) | https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo |
| DUO-019 | P1 | heuristic | Project not upgraded to Xcode 27.1 (LastUpgradeCheck < 2710) | https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ |
| DUO-020 | P1 | cited | iOS 27.1-only API in a Mac Catalyst target without #if !targetEnvironment(macCatalyst) | https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes ; https://developer.apple.com/forums/thread/847644 |
| DUO-021 | P2 | cited | WKWebView content cannot see the fold | Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://developer.apple.com/forums/thread/847644 |
| DUO-022 | P0 | cited | Symmetric safe-area math | Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ |
| DUO-023 | P1 | heuristic | Window frame read from UIApplication.shared.windows / keyWindow | Heuristic - no Apple statement covers this exact pattern. |
| DUO-030 | P1 | cited | React Native project: scene lifecycle and stale Dimensions | https://github.com/react/react-native/issues/58606 ; Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) |
| DUO-031 | P2 | cited | Flutter project: orientation lock and multi-scene limits | Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; https://github.com/flutter/flutter/issues/193056 |
| DUO-032 | P2 | cited | Capacitor/Ionic project: web content cannot see the fold | Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://developer.apple.com/forums/thread/847644 |
| DUO-033 | P2 | cited | Unity project: fixed aspect ratio and cached screen size | https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo ; https://developer.apple.com/forums/thread/847644 |

## 3. Rule details (why and fix, verbatim from the script)

### DUO-001 UIScreen.main used for layout

- Severity: P0. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple: UIScreen.main is "ambiguous on two-display devices and will be deprecated"; its bounds go stale when the device folds and the scene is resized mid-session.
- Fix: Replace with view.bounds / window.bounds (SwiftUI: GeometryReader or onGeometryChange); re-read sizes in layoutSubviews, viewDidLayoutSubviews or viewWillTransition(to:with:); never store a UIScreen - reach it via view.window?.windowScene?.screen.
- Source: https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/

### DUO-002 UIScreen.main.scale used instead of displayScale

- Severity: P1. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple's Tech Talk shows `let screenScale = UIScreen.main.scale` as the 'before' and `traitCollection.displayScale` as the 'after'; the main screen is ambiguous on iPhone Duo.
- Fix: Use traitCollection.displayScale (UIKit) or @Environment(\.displayScale) (SwiftUI).
- Source: Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; https://developer.apple.com/iphone-duo/prepare/

### DUO-003 UIWindow created from a frame instead of a window scene

- Severity: P1. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple lists `UIWindow(frame: UIScreen.main.bounds)` among the patterns to fix: the window must belong to a scene so the system can resize it between displays.
- Fix: Create windows with UIWindow(windowScene:) from your UIWindowSceneDelegate.
- Source: https://developer.apple.com/iphone-duo/prepare/

### DUO-004 userInterfaceIdiom used to choose a layout

- Severity: P0. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple: "Don't use UIDevice.userInterfaceIdiom ... for layout decisions"; iPhone Duo has no idiom of its own and "iPhone apps can have any combination of size classes".
- Fix: Branch on traitCollection.horizontalSizeClass / verticalSizeClass (or the SwiftUI environment values) and on the container's bounds; don't treat regular width as iPad.
- Source: https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo ; https://developer.apple.com/iphone-duo/prepare/ ; https://developer.apple.com/forums/thread/847644

### DUO-005 Device or interface orientation used for layout

- Severity: P0. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple: remove layout logic based on UIDevice.current.orientation, statusBarOrientation, interfaceOrientation or windowScene.effectiveGeometry.interfaceOrientation; the inner display does not honor supported orientations.
- Fix: Compare available width vs height, or use size classes; observe geometry via viewWillTransition(to:with:) / windowScene(_:didUpdateEffectiveGeometry:).
- Source: https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/

### DUO-006 supportedInterfaceOrientations override is portrait-only

- Severity: P1. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple: "The inner display doesn't honor your declared interface orientations"; portrait-only apps still receive compact and regular size-class changes and are shown wide on the inner display.
- Fix: Support all orientations (TN3192 migration checklist) and lay out from size classes; games may lock orientation but must still fill the screen in every pose.
- Source: https://developer.apple.com/forums/thread/847644 ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key

### DUO-007 Info.plist UISupportedInterfaceOrientations is portrait-only

- Severity: P1. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple: UISupportedInterfaceOrientations is honored on the outer display only; the inner display ignores it, so the app must still handle regular-width, wide layouts.
- Fix: Declare all orientations and drive layout from size classes; remove any assumption that a portrait lock means a tall, narrow canvas.
- Source: https://developer.apple.com/forums/thread/847644 ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/

### DUO-008 UIRequiresFullScreen = YES (deprecated)

- Severity: P1. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: TN3192: UIRequiresFullScreen is deprecated and "no longer opts your app out of resizing"; with the iOS 27 SDK it only yields discrete resizing, and the app still resizes on fold/unfold.
- Fix: Remove UIRequiresFullScreen (and INFOPLIST_KEY_UIRequiresFullScreen), support all orientations, and observe windowScene(_:didUpdateEffectiveGeometry:).
- Source: https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/

### DUO-009 No scene lifecycle (UIApplicationSceneManifest / scene delegate missing)

- Severity: P0. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple's UIKit Q&A: "Xcode 27 requires the scene lifecycle, so migrate first"; React Native 0.88 rc failed to launch on the Duo simulator with "UIScene life cycle is required".
- Fix: Add UIApplicationSceneManifest to Info.plist, add a UIWindowSceneDelegate, and move window creation from the AppDelegate to scene(_:willConnectTo:options:).
- Source: Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://github.com/react/react-native/issues/58606

### DUO-010 No launch screen (UILaunchScreen / UILaunchStoryboardName)

- Severity: P0. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: TN3192: "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" (TN3208).
- Fix: Add a UILaunchScreen dictionary (or UILaunchStoryboardName) to Info.plist, or set INFOPLIST_KEY_UILaunchScreen_Generation = YES in build settings.
- Source: https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key

### DUO-011 Hard-coded iPhone screen dimension compared against width/height

- Severity: P0. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: remove checks like `bounds.height == 844` and "avoid fixed widths, breakpoints, and metrics tied to a specific screen". The literal set this rule matches is a heuristic list.
- Fix: Size views relative to their container; choose layouts from size classes and the container's bounds, not device point sizes.
- Source: https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/

### DUO-012 Magic width/height breakpoint

- Severity: P1. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: "avoid fixed widths, breakpoints, and metrics tied to a specific screen"; a fixed threshold can never be hit (or always hit) on a display the threshold wasn't written for.
- Fix: Replace numeric breakpoints with horizontalSizeClass/verticalSizeClass checks, or derive thresholds from content (e.g. minimum column width).
- Source: Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/

### DUO-013 Fill content mode on media without a focal point

- Severity: P2. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: "Hero images and video set to .scaleAspectFill or .aspectRatio(contentMode: .fill) can lose important content on wider displays."
- Fix: "Use the current size classes or aspect ratio to choose between fill and fit, or set a focal point." Lines mentioning a focal point are not flagged.
- Source: https://developer.apple.com/iphone-duo/prepare/

### DUO-014 Fixed 16:9 aspect ratio

- Severity: P2. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: "Don't assume fixed ratios. Resize to fit each pose, favor changing aspect ratio over letterboxing"; Split View and PiP mean apps "may run at varying aspect ratios".
- Fix: Let players and media fill the available bounds (AVKit resizes automatically); if padding is unavoidable, add artwork to it (HIG).
- Source: https://developer.apple.com/forums/thread/847644 ; Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/ ; https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo

### DUO-015 Device model string sniffed for layout

- Severity: P1. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple: no API identifies iPhone Duo - "Design from size, traits, and reserved regions, not hardware names or screen dimensions"; Duo has no UIUserInterfaceIdiom of its own.
- Fix: Delete model-name tables; use size classes, scene geometry and reservedRegions(kind:).
- Source: Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://developer.apple.com/forums/thread/847644

### DUO-016 Status bar hidden - side inset still applies

- Severity: P2. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: safe areas "are often asymmetric on iPhone Duo. Handle each side independently." A developer report (skarol.dev) found that hiding the status bar hides the icons but not the side-column safe-area inset.
- Fix: Constrain to safeAreaLayoutGuide / keep .ignoresSafeArea() for backgrounds only, and verify the hidden-status-bar screens in the iPhone Duo simulator.
- Source: Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; report: https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/

### DUO-017 Custom tab/tool bar built from plain views

- Severity: P1. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: "Only system containers adapt automatically (TabView, UITabBarController, toolbars with standard items). Custom bars and UIToolbar subviews do not."
- Fix: Set toolbar items on a view controller inside a navigation controller / use .toolbar(content:) on NavigationStack; use UITabBarController or TabView for tabs.
- Source: https://developer.apple.com/forums/thread/847644 ; https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo

### DUO-018 Navigation bar hidden (custom top bar will not go vertical)

- Severity: P2. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Apple: if the system doesn't present your bars vertically, "check that you're using the bar support that navigation containers ... provide"; a hidden system bar replaced by a custom header stays horizontal.
- Fix: Keep the system navigation bar and add items with .toolbar(content:) / navigationItem; extend hero art under the bar with backgroundExtensionEffect() or UIBackgroundExtensionView.
- Source: https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo

### DUO-019 Project not upgraded to Xcode 27.1 (LastUpgradeCheck < 2710)

- Severity: P1. Kind: heuristic. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple: apps built with the iOS 26 SDK run centered with empty space; iOS 27 SDK fills most of the inner display; only the iOS 27.1 SDK uses the full display with vertical bars. LastUpgradeCheck is a heuristic proxy for the Xcode version that last touched the project.
- Fix: Build with Xcode 27.1 (iOS 27.1 SDK) and re-test every pose. Developer tip (blakecrosley.com): verify the SDK stamp with `otool -l <binary> | grep -A4 LC_BUILD_VERSION`.
- Source: https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/

### DUO-020 iOS 27.1-only API in a Mac Catalyst target without #if !targetEnvironment(macCatalyst)

- Severity: P1. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Xcode 27.1 release notes: iOS 27.1-only APIs produce compile errors for Mac Catalyst (185924957); the documented workaround is #if !targetEnvironment(macCatalyst).
- Fix: Wrap ArrangementView / reservedRegions / hinge / vertical-bar calls in #if !targetEnvironment(macCatalyst) and gate with if #available(iOS 27.1, *).
- Source: https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes ; https://developer.apple.com/forums/thread/847644

### DUO-021 WKWebView content cannot see the fold

- Severity: P2. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple's UIKit Q&A: "Query geometry in the host and pass it to the page. Viewport-segment and posture APIs are experimental Safari features, not available in WKWebView. CSS insets don't account for the fold."
- Fix: Read reservedRegions / safe areas in the host view and inject them into the page; use responsive layout in the web content instead of device detection.
- Source: Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://developer.apple.com/forums/thread/847644

### DUO-022 Symmetric safe-area math

- Severity: P0. Kind: cited. Detection: line-level (swift/objc source).
- Why: Apple's Tech Talk shows `view.bounds.width - view.safeAreaInsets.left * 2` as the anti-pattern: "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently."
- Fix: Use view.bounds.inset(by: view.safeAreaInsets) / safeAreaLayoutGuide and read left and right (leading and trailing) insets separately.
- Source: Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/

### DUO-023 Window frame read from UIApplication.shared.windows / keyWindow

- Severity: P1. Kind: heuristic. Detection: line-level (swift/objc source).
- Why: Heuristic: a frame captured from the key window at launch is a cached screen size, which goes stale when the scene resizes on fold/unfold. No Apple statement names this exact API.
- Fix: Read geometry from the view's own window / windowScene at layout time (layoutSubviews, viewDidLayoutSubviews, onGeometryChange).
- Source: Heuristic - no Apple statement covers this exact pattern.

### DUO-030 React Native project: scene lifecycle and stale Dimensions

- Severity: P1. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: RN 0.88.0-rc.0 failed to launch on the Duo simulator ("UIScene life cycle is required"), fixed in 0.88; Apple's UIKit Q&A says the scene lifecycle is required with Xcode 27.
- Fix: Upgrade to RN 0.88+ or add SceneDelegate + UIApplicationSceneManifest (Expo: expo-build-properties ios.enableSceneSupport). Third-party guidance (iphoneduosupport.com): use useWindowDimensions() instead of module-scope Dimensions.get, per-edge safe-area insets.
- Source: https://github.com/react/react-native/issues/58606 ; Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)

### DUO-031 Flutter project: orientation lock and multi-scene limits

- Severity: P2. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple: the inner display ignores declared orientations. Flutter's engine "does not fully support multi-scene" (flutter #193056, duplicate of #48838).
- Fix: Drive layout from MediaQuery size, not setPreferredOrientations; third-party guidance (iphoneduosupport.com): use per-side MediaQuery padding, pause on `paused` not `inactive`.
- Source: Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/ ; https://github.com/flutter/flutter/issues/193056

### DUO-032 Capacitor/Ionic project: web content cannot see the fold

- Severity: P2. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple: posture/viewport-segment APIs are not available in WKWebView and CSS insets don't account for the fold; web developers should use responsive design, not device detection.
- Fix: Pass fold geometry from the native host into the page; third-party guidance (iphoneduosupport.com): viewport-fit=cover, per-side env() insets, 100dvh, ResizeObserver.
- Source: Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 (summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) ; https://developer.apple.com/forums/thread/847644

### DUO-033 Unity project: fixed aspect ratio and cached screen size

- Severity: P2. Kind: cited. Detection: project-level (plist, pbxproj, framework config or cross-file facts).
- Why: Apple HIG for games: "fill the screen as the device pose changes ... Prefer changing the aspect ratio over letterboxing or pillarboxing". No Unity-specific Apple guidance exists.
- Fix: Re-read Screen.width/height and Screen.safeArea each frame (insets are asymmetric) and avoid letterboxing; add artwork to unavoidable padding (HIG).
- Source: https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo ; https://developer.apple.com/forums/thread/847644

## 4. Severity and kind counts

Counted from the table above:

- P0: 7 rules (DUO-001, 004, 005, 009, 010, 011, 022); 6 cited, 1 heuristic (DUO-011).
- P1: 12 rules (DUO-002, 003, 006, 007, 008, 012, 015, 017, 019, 020, 023, 030); 8 cited, 4 heuristic (DUO-012, 017, 019, 023).
- P2: 8 rules (DUO-013, 014, 016, 018, 021, 031, 032, 033); 4 cited, 4 heuristic (DUO-013, 014, 016, 018).
- Total: 27 rules; 18 cited, 9 heuristic.

Exit code is 1 when any P0 finding is shown, 0 otherwise, 2 on usage error.
