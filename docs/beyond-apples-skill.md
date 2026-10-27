# Apple's App Resizability skill and what duo-ready adds

Last checked: 2026-10-26

Xcode 27.1 ships its own coding-assistant skill for iPhone Duo. This page describes what that skill covers, as far as Apple and the sources we have say, and which topics the duo-ready skills address in addition. It is a statement of scope, not a comparison of quality.

## What Apple's skill is

- Apple's "Three steps to make your app shine on iPhone Duo" page makes running the skill Step 1: ask Xcode's coding assistant to "get my app ready for iPhone Duo". For other agents, run `xcrun agent skills export` in Terminal. Apple's own caveat: "The skill finds most issues, but not all of them" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)). Status: Apple.
- The skill introduced at WWDC26 as the "Modernize your UIKit app" skill is renamed **App Resizability** in Xcode 27.1 and covers SwiftUI and iPhone Duo ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/); origin session: [WWDC26 "Modernize your UIKit app"](https://developer.apple.com/videos/play/wwdc2026/278/), referenced, not fetched). Status: Apple.
- A community repackaging describes it as: "Adapts layouts to resizable windows and multiple windows (split screen, Stage Manager, foldables): replaces mainScreen, orientation, idiom, lifecycle, and safe-area assumptions" ([artemnovichkov/xcode-skills](https://github.com/artemnovichkov/xcode-skills)). Status: third-party, unverified.
- Apple publishes no sample project for iPhone Duo; the skill is Apple's only runnable artifact ([Apple hub](https://developer.apple.com/iphone-duo/); [Hello Developer, October 2026](https://developer.apple.com/hello/october26/)). Status: Apple.

## What it covers: the Step 2 anti-patterns

Step 2 of Apple's page is a list of patterns to search for and replace. The third-party description of the skill above matches this list, and the field reports collected in our research all trace to a pattern on it. Treat the list as the skill's scope (inferred); the list itself is Apple's ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)):

| Anti-pattern (search for) | Apple's replacement |
|---|---|
| `UIScreen.main.bounds` | `view.bounds`, `window.bounds`; SwiftUI `GeometryReader` or `onGeometryChange` |
| Reading size once at launch or in `viewIsAppearing` | Re-read in `layoutSubviews` / `viewDidLayoutSubviews`; use `viewWillTransition(to:with:)` for work that must run on resize, "because a fold can resize your app in the middle of a session" |
| `UIScreen.main.scale` | `traitCollection.displayScale` / `@Environment(\.displayScale)` |
| `UIWindow(frame: UIScreen.main.bounds)` | `UIWindow(windowScene:)` |
| Storing a `UIScreen` | "Don't store a `UIScreen`"; access via `view.window?.windowScene?.screen` |
| Layout from `UIDevice.current.orientation`, `statusBarOrientation`, `interfaceOrientation`, `windowScene.effectiveGeometry.interfaceOrientation` | Compare available width vs height; use size classes |
| `userInterfaceIdiom == .phone` / `== .pad` | "Don't choose a layout by idiom" |
| `horizontalSizeClass == .regular` treated as iPad | "Don't treat 'regular width' as 'iPad.'" ("an iPhone app can have any combination of size classes") |
| `bounds.height == 844`-style checks | "Remove checks for specific device sizes" |
| `.scaleAspectFill` / `.aspectRatio(contentMode: .fill)` hero media | "Check full-bleed media ... choose fill or fit based on size class or aspect ratio, or set a focal point" |

Tech Talk 111461 shows the code form of each fix, including `@Environment(\.horizontalSizeClass)` / `@Environment(\.verticalSizeClass)`, `let screen = window?.windowScene?.screen`, `view.bounds.inset(by: view.safeAreaInsets)`, and `UIScreen.main.scale` → `traitCollection.displayScale` ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

## What duo-ready adds

Apple's page has two more steps after the skill (Step 3: test environments; "Go further": App Store submission) and most of the Duo-specific API surface lives in the Technology Overview, the HIG, five further Tech Talks, and the Developer Forums Group Lab summary rather than in the Step 2 list. The duo-ready skills (listed in `.claude-plugin/marketplace.json` as `/duo-audit /duo-layout /duo-bars /duo-scenes /duo-camera /duo-test /duo-ship /duo-design /duo-backend /duo-crossplatform`) cover these topics:

| Topic | What it covers | Primary Apple sources |
|---|---|---|
| Vertical bars | System-owned bars moving to the side; opt-in by SDK plus container; icon/title rules; `axisBehavior`, `visibilityPriority`, `ToolbarOverflowMenu`, `toolbarVerticalBehavior`, `UITraitCollection.verticalBarEdge`; sheet placement; when Apple says to opt out | [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo); [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/); [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) |
| Hinge and scenes | A fold as a trait change, not a lifecycle event; `onHingeChange` / `UIHingeInteraction` for effects only; `UIRequiresFullScreen` discrete resizing (TN3192); Split View, PiP, multiple windows on the inner display; scene accessories (`CameraCaptureAccessory` / `UISceneAccessory`) | [Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/); [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key); [Forums 847644](https://developer.apple.com/forums/thread/847644); [Forums 847838](https://developer.apple.com/forums/thread/847838) |
| Camera | Two front cameras; the Virtual Front Camera; `AVCaptureDeviceDirectionCoordinator` and why `AVCaptureDevice.position` is insufficient; mirroring and rotation rules; dual-display preview | [Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/); [Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces) |
| Testing | Apple's three test environments; Device Hub pose controls; Xcode 27.1 and 27.2 simulator known issues; the absence of a `simctl` fold command; what the simulator cannot test | [Three steps](https://developer.apple.com/iphone-duo/prepare/); [Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub); [Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes) |
| App Store screenshots and the April 2027 rule | Duo screenshot and app preview sizes; the "Made for iPhone Duo" badge; "Starting April 2027, any apps or games submitted will need to include screenshots for iPhone Duo"; the unresolved scope conflict between the news post and the specs page | [Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo); [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications) |
| Backend and web | Apple's statement that there is no API for web pages to detect iPhone Duo; Safari's experimental Viewport Segments and Device Posture APIs; WKWebView limits; what Apple has not said about server-driven UI (labelled inferred) | [Forums 847644](https://developer.apple.com/forums/thread/847644) |
| Cross-platform | The scene-lifecycle requirement that affects React Native, Flutter, Unity and Capacitor apps; the fact that no framework had official Duo guidance as of late October 2026; where a native bridge is needed | [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key); framework details are third-party, unverified |
| Design review | The HIG's five bolded best practices and fold-transition rules; Tech Talk 111463's displacement rules and book/table pose destinations; Tech Talk 111466 on pose-specific layouts | [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo); [Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/); [Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/) |

Layout itself (size classes, reserved regions, arrangement views) is covered by both: Apple's skill addresses the Step 2 hygiene, and duo-ready's layout skill adds the iOS 27.1 API families (`ReservedRegion` / `UIView.ReservedRegion`, `ArrangementView` / `UIArrangementViewController`) from the Technology Overview and Tech Talk 111463.

## How to use both

Apple's ordering is: run the skill, then search for the Step 2 patterns, then test in the three environments, then submit. Running Apple's App Resizability skill first is consistent with that ordering; the duo-ready skills are written for the steps after it. Every rule in duo-ready cites the Apple page it came from, and anything Apple has not published is labelled third-party, unverified or inferred (see known-gaps.md).
