Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Lifecycle and state across the fold

Contents

1. The scene lifecycle is required
2. `UIRequiresFullScreen` on iOS 27 (TN3192)
3. What Apple says survives a fold
4. State-preservation audit table
5. Orientation on the inner display
6. What Apple has not said
7. Sources

Labels: statements without a label are Apple's, with the source inline. "(third-party, unverified)" marks blogs, GitHub issues and simulator measurements. "(inferred)" marks conclusions drawn by the report or this skill.

## 1. The scene lifecycle is required

Evidence, in order of authority:

- Runtime message seen by React Native 0.88.0-rc.0 on the iPhone Duo simulator: "Application failed to launch: UIScene life cycle is required for apps built with this SDK" ([react-native issue #58606](https://github.com/react/react-native/issues/58606), third-party). The fix was adding `SceneDelegate.swift`, adding the `UIApplicationSceneManifest` Info.plist key, and moving `UIWindow` creation out of the AppDelegate; Expo users set `expo-build-properties` → `"ios": {"enableSceneSupport": true}`. The issue closed October 16, 2026 as fixed in RN 0.88.
- A third-party summary of Apple's UIKit Q&A records "Xcode 27 requires the scene lifecycle, so migrate first" ([Gubarenko Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums), third-party summary of Apple answers).
- Apple's own Three steps page lists `UIWindow(frame: UIScreen.main.bounds)` → `UIWindow(windowScene:)` among the patterns to fix ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).

No Apple documentation page stating the requirement in those words was captured in the report. Say that to the user; the launch failure is still real.

Migration list (every item traces to the sources above or to TN3192):

| Do | Why |
|---|---|
| Add `UIApplicationSceneManifest` to Info.plist | The key the RN fix added; the scanner's DUO-009 looks for it |
| Add a class conforming to `UIWindowSceneDelegate` | The scene delegate the RN fix added |
| Create the window with `UIWindow(windowScene:)` in `scene(_:willConnectTo:options:)` | Apple's replacement for `UIWindow(frame: UIScreen.main.bounds)` (Three steps) |
| Move root-view-controller and framework bootstrapping out of `application(_:didFinishLaunchingWithOptions:)` | The RN fix moved `startReactNative` to the scene delegate |
| Provide a launch screen | "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key), citing TN3208) |
| If the app supports multiple instances, set `UIApplicationSupportsMultipleScenes = YES` | Standard iPad mechanism; no Duo-specific key exists in any Apple source (inferred) |

Minimal shape (this is the audit fixture the scanner accepts, trimmed):

```swift
// Composed from Apple-documented APIs; type-checked with swiftc against the iOS 27.1 simulator SDK (Xcode 27.1, 27A9275) on 2026-10-27. Not run on a device.
import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = RootViewController()
        window.makeKeyAndVisible()
        self.window = window
    }
}
```

## 2. `UIRequiresFullScreen` on iOS 27 (TN3192)

TN3192, "Migrating your app from the deprecated UIRequiresFullScreen key", revised 2026-10-09. Verbatim rules:

- "Prior to iOS 27, this key-value pair configures iPadOS apps only, and is ignored for iOS apps."
- "Starting in iPadOS 26, `UIRequiresFullScreen` and its associated compatibility mode are deprecated and will be ignored in a future release."
- "Starting in iOS 27 and iPadOS 27, `UIRequiresFullScreen` no longer opts your app out of resizing on either platform. Instead, the system resizes your app's scene discretely. This behavior applies when you build your app with the iOS 27 SDK or later and set `UIRequiresFullScreen` to `YES`, unless `UIRequiresFullScreenIgnoredStartingWithVersion` specifies version 27 or earlier."
- The corresponding build setting is `INFOPLIST_KEY_UIRequiresFullScreen`.
- "With a discrete resize, the scene doesn't change size while people drag the window. When they finish, the `coordinateSpace.bounds` of the scene's `effectiveGeometry` changes, and the scene moves to a `UIScreen` of exactly the same size."

On Duo specifically: "The app continues to honor `UIRequiresFullScreen`, but still resizes when the device opens or closes" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)); "`UIRequiresFullScreen` is honored, and apps adapt in place rather than backgrounding" ([thread 847644](https://developer.apple.com/forums/thread/847644)). TN3192's drag-to-resize wording describes iPad and iPhone Mirroring; how a discrete resize is timed against a fold on Duo is not described beyond "still resizes when the device opens or closes" (gap).

Tech Talk 111461 verbatim (re-checked against the transcript on 2026-10-27): "iPhone Duo will continue to honor the `UIRequiresFullScreen` key, but your app will still resize when someone opens or closes their iPhone Duo. iPhone Duo respects your supported interface orientations, but your app will scale on the inner display, including in Split View multitasking." The same talk also says: "Interface orientation on the inner display behaves differently. The inner display doesn't honor your supported interface orientations. As with Idiom, avoid checking interface orientation for layout decisions. Use size classes instead." Apple has not published how "respects ... but will scale" and "doesn't honor" fit together; present both and design with size classes.

Apple's migration checklist, verbatim order: provide a launch screen; support all interface orientations; remove `UIRequiresFullScreen`.

APIs TN3192 names for apps that observe scene geometry:

| Purpose | API |
|---|---|
| Observe the new size | `windowScene(_:didUpdateEffectiveGeometry:)`, comparing `coordinateSpace.bounds` of the scene's `effectiveGeometry` |
| Skip work during a live drag | `UIWindowScene.Geometry.isInteractivelyResizing` |
| React to trait changes | `registerForTraitChanges(_:target:action:)`, `registerForTraitChanges(_:handler:)` |
| SwiftUI equivalent for live resize | `onInteractiveResizeChange(_:)` |
| Size preferences | `UISceneSizeRestrictions` via `windowScene.sizeRestrictions?.minimumSize`; SwiftUI `windowResizability(_:)` |
| Orientation lock request (not guaranteed) | `prefersInterfaceOrientationLocked` plus `setNeedsUpdateOfPrefersInterfaceOrientationLocked()` |

TN3192's own sample compares `coordinateSpace.bounds.size` in `windowScene(_:didUpdateEffectiveGeometry:)` and calls something like `gameAssetManager.updateAssets(sceneSize:)` only when `!geometry.isInteractivelyResizing`. The report describes that sample rather than quoting it, so the version below is composed:

```swift
// Composed from Apple-documented APIs; type-checked with swiftc against the iOS 27.1 simulator SDK (Xcode 27.1, 27A9275) on 2026-10-27. Not run on a device.
import UIKit

extension SceneDelegate {
    func windowScene(_ windowScene: UIWindowScene,
                     didUpdateEffectiveGeometry previousGeometry: UIWindowScene.Geometry) {
        let geometry = windowScene.effectiveGeometry
        let newSize = geometry.coordinateSpace.bounds.size
        let oldSize = previousGeometry.coordinateSpace.bounds.size
        guard newSize != oldSize, !geometry.isInteractivelyResizing else { return }
        // TN3192's example swaps asset sets here, e.g. gameAssetManager.updateAssets(sceneSize: newSize).
        // Do not read interfaceOrientation here for layout; Apple lists
        // windowScene.effectiveGeometry.interfaceOrientation among the patterns to remove (Three steps).
    }
}
```

Note the last comment: the Three steps page tells developers to remove layout logic based on `windowScene.effectiveGeometry.interfaceOrientation`; the geometry callback is for size, not orientation. On Duo, "Scene size can't be set directly. It's driven by pose and Split View" (thread 847644), so `UISceneSizeRestrictions` is a preference the system may not honor there.

## 3. What Apple says survives a fold

All from the DTS "Summary of the iPhone Duo Group Lab", [thread 847644](https://developer.apple.com/forums/thread/847644), unless marked:

- "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running."
- "Text input, scroll position, and video playback are generally preserved automatically. Apps usually don't need `scrollPosition(id:)` for LazyVGrid column changes."
- "An active editing session survives the hinge transition without getting a new scene."
- Keyboard: keep the edited field visible with `keyboardWillShowNotification`, `keyboardWillHideNotification`, `keyboardWillChangeFrameNotification`; standard controls handle the keyboard automatically.
- "For state that must survive a true scene disconnect/reconnect, implement `stateRestorationActivity(for:)` and save an `NSUserActivity`."
- Animations "should be able to start, pause, and stop at any time. Use `TimelineView` or `CADisplayLink` for custom timing."
- "Video playback continues through hinge changes. AVKit scales and resizes automatically. PiP moves to the outer display only when the device is closed, under system control." Audio-only content cannot be pinned like PiP.
- "`UserDefaults` and `@AppStorage` are app-wide, not per-window."
- "Hinge changes are just geometry/trait changes." "Multiple scenes matter mainly for Split View and scene accessories."
- Mid-session resize: re-read size in `layoutSubviews`, `viewDidLayoutSubviews`, or `viewWillTransition(to:with:)` "because a fold can resize your app in the middle of a session" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Design rule: "Create a consistent experience across displays. Keep functionality and the state of elements the same between displays ... Mail, for example, shows either a list of emails (primary) or an email (secondary) when the device is closed. When it's open, it shows both side by side"; "Avoid extreme layout changes as people fold the device. Move only what's necessary ... favor small adjustments over rearrangement" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Third-party summary of Apple's UIKit Q&A ([Gubarenko Q35, Q36, Q39](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)): bottom sheets are not dismissed on fold; deep links need no special handling; carousel position is generally preserved. Treat as a summary, not Apple's verbatim text.

Inference that follows (state it as such): because nothing is torn down by the system, state loss on fold is self-inflicted; apps that rebuild view hierarchies on size-class change lose scroll, selection and text. Field corroboration: Appwrite warns that "view controllers that reload on size change can lose state when the device folds" ([Appwrite blog](https://appwrite.io/blog/post/phone-duo-whats-new-and-what-developers-can-build), third-party); skarol.dev saw "Stale layout after folding" from sizes saved at launch, fixed via `viewWillTransition`, `viewSafeAreaInsetsDidChange()`, trait registration, and in SwiftUI by not copying sizes into `@State` in `onAppear` but using `onGeometryChange(for:of:action:)` ([skarol.dev](https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/), third-party).

## 4. State-preservation audit table

Grep the project for the left column; the right column is what to do and why.

| Pattern found | Risk | Change | Source |
|---|---|---|---|
| Root view controller or SwiftUI root swapped in `traitCollectionDidChange`, `registerForTraitChanges` handler, `onChange(of: horizontalSizeClass)` | Loses typed text, scroll, selection | Keep the same instances; let containers relayout; move only what must move | HIG consistency rule; inferred from no-teardown |
| Size read once in `viewDidLoad` / `onAppear` into a stored property or `@State` | Stale layout after fold | Re-read in `viewDidLayoutSubviews` / `layoutSubviews`; `viewWillTransition(to:with:)`; SwiftUI `onGeometryChange` | Three steps; skarol.dev (third-party) |
| `AVPlayer.pause()`, `Timer.invalidate()` in `sceneWillResignActive` / `scenePhase == .inactive` | Freezes a visible app in Split View | Pause on background; playback continues through hinge changes on its own | Apple: playback continues; inactive-in-Split-View is a simulator observation (third-party, unverified) |
| Custom animation with no pause path | Cannot stop mid-fold | `TimelineView` or `CADisplayLink`; make start/pause/stop callable any time | thread 847644 |
| `stateRestorationActivity(for:)` returning fold-specific state | Wrong tool | Reserve for true disconnect/reconnect; save an `NSUserActivity` | thread 847644 |
| Per-window flags in `UserDefaults` / `@AppStorage` | Two windows clobber each other | Scene-scoped model or `SceneStorage` | thread 847644 (app-wide); `SceneStorage` listed in the report's API table |
| Text field under the keyboard after resize | Hidden input | Observe the three `keyboardWill...` notifications | thread 847644 |
| Layout from `windowScene.effectiveGeometry.interfaceOrientation` | Wrong on inner display | Compare width vs height; use size classes | Three steps |
| Network/upload/socket owned by a view controller recreated per scene | Duplicate requests with two instances | Process-scoped, idempotent singletons | inferred; Apple's mid-checkout answer "doesn't address how to avoid duplicate network requests" |

## 5. Orientation on the inner display

Apple's operative guidance is DTS's answer to "Is there a sanctioned way to lock the inner display to portrait only?": "No. The inner display doesn't honor your supported interface orientations — avoid checking orientation for layout decisions and use size classes instead" ([thread 847644](https://developer.apple.com/forums/thread/847644)). Tech Talk 111461 says the same: "The inner display doesn't honor supported interface orientations, so use size classes rather than orientation for layout decisions. Landscape support is still valuable on the outer display, since people may use the device like a tent." Portrait-only apps "still receive compact and regular size class changes. The outer display honors supported orientations, but the inner display ignores them" (thread 847644).

The same thread, answering a question about compatibility mode on the inner display, also contains the wording "Yes, iPhone Duo still honors UISupportedInterfaceOrientations, but the expected behavior for this device differs from previous iPhone devices in certain hinge states and orientations. Instead, use size classes..." Present both quotes to the user and do not resolve the difference; both end in the same instruction.

TN3192 adds the mechanics: the system intersects what the app declares (`supportedInterfaceOrientations`, Info.plist, or `application(_:supportedInterfaceOrientationsFor:)`) with what the device supports, excludes `portraitUpsideDown` on Home-button-less iPhones, and does not guarantee `prefersInterfaceOrientationLocked` requests. A forum request for a `UIRequiresFixedInterfaceOrientation` key exists; no such key does ([Apple Forums activity 1659080](https://developer.apple.com/forums/activities/1659080), request only). Games may lock orientation but must fill the screen in every pose (HIG).

## 6. What Apple has not said

Report Appendix C and the research notes list these gaps; repeat them to the user instead of filling them:

- Whether a fold ever triggers `sceneWillResignActive` or backgrounding for a single full-screen scene. Only the multi-window DTS answer ([thread 847838](https://developer.apple.com/forums/thread/847838), quoted in `multiwindow-and-accessories.md`) describes a phase change.
- Whether the `UIScreen` instance identity changes between the inner and outer display. TN3192 says a discrete resize moves the scene to "a `UIScreen` of exactly the same size"; Apple also says "Don't store a `UIScreen`" and reach it via `view.window?.windowScene?.screen` (Three steps), so code should not care.
- Whether the display switch can re-create a scene under memory pressure.
- How to avoid duplicate network requests across two instances; Apple's mid-checkout answer covers input persistence only.
- Whether per-scene security setup (jailbreak/tamper detection, SSL pinning) in a scene delegate needs duplicating; this was a listed Q&A topic ([Apple Forums activity 1664080](https://developer.apple.com/forums/activities/1664080)) and no answer was captured.
- Timing of a discrete resize relative to the fold animation on Duo.

## 7. Sources

| Source | URL |
|---|---|
| DTS: A Summary of the iPhone Duo Group Lab (thread 847644) | https://developer.apple.com/forums/thread/847644 |
| DTS: ScenePhase during fold, multi-window (thread 847838) | https://developer.apple.com/forums/thread/847838 |
| TN3192: Migrating your app from the deprecated UIRequiresFullScreen key | https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key |
| Three steps to make your app shine on iPhone Duo | https://developer.apple.com/iphone-duo/prepare/ |
| Tech Talk 111461, Prepare your app for iPhone Duo | https://developer.apple.com/videos/play/tech-talks/111461/ |
| HIG: Designing for iPhone Duo | https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo |
| Apple Forums activity 1659080 (Photos & Camera Q&A listing) | https://developer.apple.com/forums/activities/1659080 |
| Apple Forums activity 1664080 (SwiftUI Q&A listing) | https://developer.apple.com/forums/activities/1664080 |
| react-native issue #58606 (third-party) | https://github.com/react/react-native/issues/58606 |
| Gubarenko, summary of Apple UIKit Q&A (third-party) | https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums |
| skarol.dev field report (third-party) | https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/ |
| Appwrite blog (third-party) | https://appwrite.io/blog/post/phone-duo-whats-new-and-what-developers-can-build |
