---
name: duo-scenes
description: >-
  Explains how iPhone Duo's fold, display switch, Split View, multiple windows,
  scene accessories and hinge API behave at the scene and lifecycle level, and
  fixes code that treats a fold like a relaunch. Use it whenever a user says
  their app "resets", "loses the typed text", "restarts the video", "jumps back
  to the top", "loses the form" or "shows a blank screen" when the phone opens
  or closes; asks whether a fold fires scenePhase/background/resign-active;
  asks about UIRequiresFullScreen on iOS 27, "UIScene life cycle is required"
  launch failures, SceneDelegate migration, stateRestorationActivity, or
  AppStorage in two windows; wants two windows of their app side by side, Split
  View, PiP, Stage Manager, openWindow, requestSceneSessionActivation errors or
  "which window stays active when I close the phone"; wants to put a
  teleprompter, script, countdown or framing guide on the outer screen while the
  camera records on the inner one (CameraCaptureAccessory / UISceneAccessory);
  or wants to react to the hinge angle, "tent mode", "laptop mode" or
  onHingeChange / UIHingeInteraction. Also trigger when the user never says
  "Duo" but describes "the new foldable iPhone", "when the phone opens
  mid-checkout", or "the second screen".
---

# duo-scenes: the fold is a trait change, not a lifecycle event

## What Apple actually says

- "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running." Text input, scroll position and video playback "are generally preserved automatically"; an active editing session "survives the hinge transition without getting a new scene" ([DTS: A Summary of the iPhone Duo Group Lab, thread 847644](https://developer.apple.com/forums/thread/847644)).
- `UIRequiresFullScreen` no longer opts an app out of resizing on iOS 27; the system "resizes your app's scene discretely" instead, and on Duo the app "still resizes when the device opens or closes" ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key); [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Multitasking on the inner display is Split View (50/50) plus a stacked video-and-app layout; "Every app participates"; new windows "cannot be created" on the outer display; no Stage Manager, no free-form resize ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/); [Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/); thread 847644).
- Scene accessories are the only way to show content on the outer display while the app runs on the inner one, and only during active camera capture: "Non-camera apps can't draw directly on the outer display" ([UISceneAccessory](https://developer.apple.com/documentation/uikit/uisceneaccessory); [Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo); Tech Talk 111464).
- Hinge data "is ideal for driving interactions and effects. For layout decisions, use the arrangement and region APIs" (Tech Talk 111464). There is "no single pose API" and hinge "Update rate and precision are system policy, so don't depend on specific values" (thread 847644).

Everything below is built on those statements. Where Apple has not said something, this skill says so instead of guessing.

## Workflow

### Step 0: look at the real code first

Ask for, or open, the user's project before advising. The same symptom ("the form resets when the phone opens") has opposite fixes depending on whether the app tears down its own view hierarchy or whether it is still an AppDelegate-only app that never adopted scenes. When a project path is available, run:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

The rules that matter for this skill are DUO-009 (no scene lifecycle), DUO-003 (`UIWindow(frame:)` instead of `UIWindow(windowScene:)`), DUO-008 (`UIRequiresFullScreen = YES`), DUO-010 (no launch screen), DUO-005 (orientation used for layout) and DUO-023 (window frame read from `UIApplication.shared.windows`). Then grep by hand for the things the scanner cannot judge: `traitCollectionDidChange`, `viewWillTransition(to:with:)`, `scenePhase`, `sceneWillResignActive`, `sceneDidEnterBackground`, `applicationWillResignActive`, `stateRestorationActivity`, `@AppStorage`, `UserDefaults`, `requestSceneSessionActivation`, `openWindow`, `UIApplicationSupportsMultipleScenes`, `AVPlayer`/`pause()`, `CADisplayLink`, `Timer`, and any `removeFromSuperview`/`rootViewController =` reassignment inside a trait or size callback.

### Step 1: confirm the app launches at all (scene lifecycle)

An app built with the iOS 27 SDK must use the scene lifecycle. The evidence in the report is a launch failure, not an Apple page: React Native 0.88.0-rc.0 failed to start on the Duo simulator with "Application failed to launch: UIScene life cycle is required for apps built with this SDK" ([react-native issue #58606](https://github.com/react/react-native/issues/58606), third-party), and a third-party summary of Apple's UIKit Q&A records "Xcode 27 requires the scene lifecycle, so migrate first" ([Gubarenko Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums), third-party summary of Apple answers). Treat it as blocking.

What to change, in order:

1. Add `UIApplicationSceneManifest` to Info.plist and a `UIWindowSceneDelegate`.
2. Create the window with `UIWindow(windowScene:)` inside `scene(_:willConnectTo:options:)`; Apple lists `UIWindow(frame: UIScreen.main.bounds)` among the patterns to remove ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
3. Move anything that used to run in `application(_:didFinishLaunchingWithOptions:)` and touched the window (root view controller, React Native/Flutter view creation) into the scene delegate. For Expo the switch is `expo-build-properties` with `"ios": {"enableSceneSupport": true}` (third-party, from the same issue).
4. Provide a launch screen: "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" (TN3192, citing TN3208).

The GoodApp fixture in `duo-audit/scripts/fixtures/GoodApp/Sources/SceneDelegate.swift` shows the minimal shape the scanner accepts. Read `references/lifecycle-and-state.md` section 1 for the migration list.

### Step 2: decide what `UIRequiresFullScreen` means for this app

Read the Info.plist and build settings for `UIRequiresFullScreen` and `INFOPLIST_KEY_UIRequiresFullScreen`. Then explain the iOS 27 semantics from TN3192 (revised 2026-10-09):

- Before iOS 27 the key configured iPadOS apps only and was ignored for iOS apps.
- From iOS 27 / iPadOS 27 it "no longer opts your app out of resizing on either platform. Instead, the system resizes your app's scene discretely", when the app is built with the iOS 27 SDK or later and sets the key to `YES`, "unless `UIRequiresFullScreenIgnoredStartingWithVersion` specifies version 27 or earlier".
- A discrete resize means the scene does not change size while people drag a window; when they finish, `coordinateSpace.bounds` of the scene's `effectiveGeometry` changes "and the scene moves to a `UIScreen` of exactly the same size".
- On Duo the key is honored "but still resizes when the device opens or closes" (Tech Talk 111461); DTS adds "apps adapt in place rather than backgrounding" (thread 847644).

Apple's migration checklist is three items: provide a launch screen, support all interface orientations, remove `UIRequiresFullScreen`. Recommend it unless the user has a measured reason (a game that swaps asset sets per size is TN3192's own example) to keep discrete resizing. If they keep the key, they must observe `windowScene(_:didUpdateEffectiveGeometry:)`, skip work while `UIWindowScene.Geometry.isInteractivelyResizing` is true, and use `registerForTraitChanges(_:target:action:)` / `registerForTraitChanges(_:handler:)` (UIKit) or `onInteractiveResizeChange(_:)` (SwiftUI). Size preferences go through `UISceneSizeRestrictions` (`windowScene.sizeRestrictions?.minimumSize`) or `windowResizability(_:)`, with the caveat that on Duo "Scene size can't be set directly. It's driven by pose and Split View" (thread 847644).

Do not promise an orientation lock on the inner display. Apple's operative guidance is DTS's answer to "Is there a sanctioned way to lock the inner display to portrait only?": "No. The inner display doesn't honor your supported interface orientations — avoid checking orientation for layout decisions and use size classes instead" (thread 847644), which matches Tech Talk 111461, and `prefersInterfaceOrientationLocked` requests "are not guaranteed to be honored" (TN3192). The same thread, answering a question about compatibility mode on the inner display, also says "Yes, iPhone Duo still honors UISupportedInterfaceOrientations, but the expected behavior for this device differs from previous iPhone devices in certain hinge states and orientations. Instead, use size classes..."; quote both to the user rather than resolving the difference yourself. Full detail and the composed geometry sample are in `references/lifecycle-and-state.md` section 2. Tech Talk 111461 adds, in the same breath, that iPhone Duo "respects your supported interface orientations, but your app will scale on the inner display, including in Split View multitasking"; Apple has not reconciled the two sentences, so quote both and rely on size classes (see `references/lifecycle-and-state.md`).

### Step 3: find the self-inflicted teardown

Because the fold is a trait change, state loss on fold is almost always the app's own doing. Look for:

- View hierarchies rebuilt in `traitCollectionDidChange`, `viewWillTransition(to:with:)`, `registerForTraitChanges` handlers, or SwiftUI `onChange(of: horizontalSizeClass)` that swaps the whole tree with `if compact { A } else { B }` using different identities. Apple's HIG rule is "Keep functionality and the state of elements the same between displays" and "Avoid extreme layout changes as people fold the device" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). The inference the report draws, and that you should state as inference, is that keeping view instances alive and letting them relayout is what preserves scroll, selection and text ([3P corroboration: Appwrite, "view controllers that reload on size change can lose state when the device folds"](https://appwrite.io/blog/post/phone-duo-whats-new-and-what-developers-can-build)).
- Sizes copied once into `@State` in `onAppear`, or read once in `viewDidLoad`; Apple says to re-read in `layoutSubviews` / `viewDidLayoutSubviews` and use `viewWillTransition(to:with:)` "because a fold can resize your app in the middle of a session" (Three steps). SwiftUI: `onGeometryChange` rather than caching (third-party field fix: [skarol.dev](https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/)).
- Media paused or timers invalidated in `sceneWillResignActive` / `scenePhase == .inactive`. In Split View a visible app can be `inactive` (third-party, unverified: [iPhone-Duo-by-Examples](https://github.com/artemnovichkov/iPhone-Duo-by-Examples)); Apple's own statement is only that playback "continues through hinge changes" and "AVKit scales and resizes automatically" (thread 847644). Pause on background, not on inactive, and say that the inactive-in-Split-View observation is from the simulator.
- Animations that cannot be interrupted. Apple: animations "should be able to start, pause, and stop at any time. Use `TimelineView` or `CADisplayLink` for custom timing" (thread 847644).
- `stateRestorationActivity(for:)` used as a fold workaround. Apple scopes it to "state that must survive a true scene disconnect/reconnect"; implement it and save an `NSUserActivity` for that purpose, not for folds.
- Text fields hidden by the keyboard after the resize. Apple names `keyboardWillShowNotification`, `keyboardWillHideNotification`, `keyboardWillChangeFrameNotification` to keep the edited field visible across the transition; standard controls handle the keyboard automatically (thread 847644).

State plainly what Apple has not said: whether a fold can ever fire `sceneWillResignActive` or background a full-screen single-scene app is not stated anywhere except the multi-window DTS answer in Step 4 (Appendix C of the report lists this as a gap). Do not tell the user "the fold never changes scenePhase"; tell them Apple says the process keeps running and the scene is not disconnected, and that the only documented phase change is the secondary window in multi-window.

### Step 4: multiple windows and Split View

Confirm what the user wants: two apps side by side (Split View, nothing to adopt beyond resizing), or two instances of their own app (multiple scenes).

- Split View is "a 50/50 layout started from the home gesture"; PiP "pins to top and the app resizes vertically in real time"; "Free-form drag-to-resize isn't supported"; Stage Manager is not supported; the PiP window "moves to the outer display only when the device closes, under system control" (Tech Talk 111466; thread 847644). Test it by dragging "the app by the home indicator to either side of the screen, and check vertically laid-out content on both sides" (Tech Talk 111461). Each app in Split View puts its bars on its outer edge (HIG), which duo-bars covers.
- Multiple instances: "iPhone Duo is the first iPhone to support multiple instances of your app's UI ... On the outer display of iPhone Duo, new windows cannot be created. That behavior is reserved for the inner display"; "creation availability is dynamic, so apps must handle errors when requesting scenes"; offer the action through `UIWindowSceneActivationAction`, "which hides automatically when new windows aren't available" (Tech Talk 111464). Apple's Duo material does not name the request method; the pre-existing API in the report is `requestSceneSessionActivation`, so wire its error handler (this mapping is the report's inference). The notes spell the action type `UIWindowScene.ActivationAction` and the report `UIWindowSceneActivationAction`; confirm the spelling in the SDK headers before shipping.
- The scene manifest still needs `UIApplicationSupportsMultipleScenes = YES` as on iPad; no Duo-specific key appears in any Apple source (inferred).
- Which window survives a close: DTS wrote that if the app "is in full-screen using the entire open flat inner display, the scene is unaffected by the hinge state change ... Otherwise, if someone is using multi-window on the inner display, the most recently active scene window would be remain active when the device closes—the secondary window scene would transition to an inactive state, then backgrounded" ([thread 847838](https://developer.apple.com/forums/thread/847838)). Design the secondary scene to tolerate being backgrounded mid-task.
- "`UserDefaults` and `@AppStorage` are app-wide, not per-window" (thread 847644). Per-window state belongs in `@SceneStorage` or the scene's own model; singletons (auth, sockets, Core Data contexts, upload queues) must be process-scoped and safe to hit from two scenes (inferred from the no-teardown statement; Apple's mid-checkout answer "doesn't address how to avoid duplicate network requests").
- `openWindow` on iPhone opened the new window full screen rather than in Split View in the simulator (third-party, unverified).
- Apple does not publish Split View point sizes or say whether three-column split views appear on the inner display; the audio/video rule is that playback "is associated with the most recent app that began the playback session" (thread 847644).

Details and the DTS quotes in full: `references/multiwindow-and-accessories.md` sections 1 to 3.

### Step 5: putting content on the other display (scene accessories)

If the user wants the outer display to show something while the app runs on the inner one, there is exactly one supported path and it requires an active camera session.

- UIKit: `UISceneAccessory` (iOS 27.0+) with `cameraCapture(sceneConfiguration:)`, `cameraCapture(sceneConfiguration:userInfo:)`, `externalNonInteractive(sceneConfiguration:)`, `externalNonInteractive(sceneConfiguration:userInfo:)`; register from the capture view controller with `registerSceneAccessory(_:)`, keep the returned `UISceneAccessoryRegistration` (`isAvailable` read-only, `isEnabled` read/write), read `isAvailable` in `updateProperties()`. The accessory scene connects with role `UISceneSession.Role.windowCameraCaptureAccessory` and receives the model in `connectionOptions.sceneAccessoryUserInfo` inside `scene(_:willConnectTo:options:)`. "The system assigns the session role, so the app never sets it. Accessory scenes have no project-level configuration, so a scene manifest (Info.plist) entry for one has no effect" (Registering a camera capture accessory).
- SwiftUI: `CameraCaptureAccessory` (iOS 27.1+) inside `View.sceneAccessory(content:)`, with `init(isEnabled:content:)` and `SceneAccessoryContent.onAvailabilityChange(perform:)` ([CameraCaptureAccessory](https://developer.apple.com/documentation/swiftui/cameracaptureaccessory)).
- Conditions: "The app is full screen on the inner display. The app has an active camera session. The accessory is registered on the same view as the camera UI." Content disappears when capture stops, the app leaves the foreground, or the device closes. Toggle with `isEnabled`; do not unregister. Keep every essential control in the capture interface. "Simulator has no camera, so test on a device before shipping" (Tech Talk 111464; Registering article; thread 847644).
- Simulator caveat: in Xcode 27.1 "an app using `CameraCaptureAccessory` can use both displays at the same time without an active camera capture session. (190155353)"; the 27.2 RC notes record it fixed ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). A teleprompter that "works" in the simulator without a session is not proof.
- Accessory content faces the person being filmed, so keep private data out of it (inferred).

Use Apple's teleprompter code verbatim from `references/multiwindow-and-accessories.md` section 4. For camera selection and mirroring, hand off to duo-camera.

### Step 6: the hinge, for effects only

When the user wants "tent mode" or an angle-driven effect:

- SwiftUI `onHingeChange(isEnabled:_:)` delivers `(DeviceHingeContext, DeviceHingeContext)`; `context.hinge` is `DeviceHinge?` (nil on devices without a hinge) with `angle: Angle` and `status: DeviceHinge.Status` ([onHingeChange](https://developer.apple.com/documentation/swiftui/view/onhingechange(isenabled:_:)); [DeviceHinge](https://developer.apple.com/documentation/swiftui/devicehinge)).
- UIKit `UIHingeInteraction(updateHandler:)` added with `view.addInteraction(_:)`; `update.hinge` is `UIHinge?` (nil means the interaction "has left a hierarchy that provides hinge updates") with `angle: CGFloat` "in radians" and `status: UIHinge.Status` ([UIHingeInteraction](https://developer.apple.com/documentation/uikit/uihingeinteraction); [UIHinge](https://developer.apple.com/documentation/uikit/uihinge)). The units differ between frameworks; convert deliberately.
- The iOS 27.1 SDK (Xcode 27.1, 27A9275, headers read 2026-10-27) declares SwiftUI `DeviceHinge.Status` as `.closed`, `.partiallyOpen`, `.fullyOpen` (no `.unknown`) and UIKit `UIHinge.Status` as `.unknown`, `.closed`, `.partiallyOpen`, `.fullyOpen`. Apple's prose and samples only show `.partiallyOpen`, and Apple says not to depend on specific hinge values, so use the status for effects, not layout.
- Apple gives no angle thresholds for tent, laptop or book, and says not to depend on specific values. If the user needs a layout decision (what goes above or below the fold), route them to `reservedRegions(kind: .division)` and `ArrangementView` / `UIArrangementViewController` in duo-layout; use the hinge for the effect itself (pitch bend, parallax, a 3D object that follows the angle).
- The APIs are iOS 27.1+ on any iPhone or iPad, not Duo-exclusive; gate with `if #available(iOS 27.1, *)` and wrap Catalyst with `#if !targetEnvironment(macCatalyst)` (Xcode 27.1 Release Notes).
- Motion: `CMMotionManager.startDeviceMotionUpdates(using:)`, conform the view to `CMBodyIdentifiable` and set `deviceMotionBody`; attitude is corrected for the displaying body only when the app is full screen on that display; "Apps don't need to know which face is up. Use size classes" (thread 847644). The report captured these names from the Group Lab summary, not from a reference page; say so.

Apple's verbatim samples and the full signature table are in `references/hinge-api.md`.

### Step 7: verify

- In Device Hub use Closed / Partially Open / Open and the Option-drag slider, fold while a field is being edited, while a video plays, and while a sheet is up; confirm the text, scroll offset and playback position survive and the sheet is still there (Apple: bottom sheets are not dismissed on fold, per a third-party summary of Apple's Q&A, Gubarenko Q35).
- Launch on the outer display, open the phone, close it again, rotate in each state.
- Split View via the home-indicator drag; with two instances of the app, close the phone and check which one stayed active (thread 847838).
- Camera accessory on a real device only.
- The simulator cannot be folded from `simctl` or XCUITest (forum thread 847883 has no Apple reply), so these are manual passes; duo-test has the matrix.

## Common mistakes

- Treating the fold as a relaunch and reloading data or rebuilding the root view controller on size-class change; loses scroll, selection and typed text ([Inference] from Apple's no-teardown statement; [3P] Appwrite and skarol.dev field reports).
- Shipping an AppDelegate-only app and hitting "UIScene life cycle is required for apps built with this SDK" at launch ([3P] react-native #58606; [Apple] Q&A via third-party summary).
- Expecting `UIRequiresFullScreen = YES` to stop resizing on Duo ([Apple] TN3192; Tech Talk 111461).
- Pausing media or timers on `inactive`, which in Split View freezes a visible app ([3P] simulator observation; Apple says pause logic should not be tied to hinge changes).
- Using `stateRestorationActivity(for:)` to "survive the fold" ([Apple] scopes it to true disconnects).
- Storing per-window state in `UserDefaults` / `@AppStorage` ([Apple] app-wide, not per-window).
- Requesting a new scene without an error handler, or showing a custom "open in new window" button on the outer display ([Apple] Tech Talk 111464).
- Adding a scene-manifest entry for the accessory scene, or trying to draw on the outer display without a camera session ([Apple] Registering article; Tech Talk 111464).
- Using hinge angle thresholds for layout, or hard-coding Device Hub's 127°/180° values ([Apple] no thresholds published; [3P] angles are from one blog).
- Treating SwiftUI `Angle` and UIKit radians as the same number ([Apple] both reference pages).

## When to read the references

- `references/lifecycle-and-state.md`: the full DTS continuity quotes, TN3192 semantics and migration checklist, the composed `didUpdateEffectiveGeometry` sample, and the state-preservation audit table.
- `references/multiwindow-and-accessories.md`: Split View and PiP rules, multiple-scene API and error handling, the DTS multi-window answer, and the `UISceneAccessory` / `CameraCaptureAccessory` surface with Apple's teleprompter code.
- `references/hinge-api.md`: `onHingeChange` / `DeviceHinge` / `UIHingeInteraction` / `UIHinge` signatures, Apple's verbatim samples, the status-case verification table, motion APIs, and Device Hub angle controls.

## Related skills

- duo-audit: run the scanner first; DUO-003, DUO-008, DUO-009, DUO-010 are the lifecycle rules.
- duo-layout: size classes, reserved regions and arrangement views, which is where layout decisions belong instead of the hinge.
- duo-bars: how bars sit on each app's outer edge in Split View, sheets, opt-out.
- duo-camera: direction coordinator, virtual front camera and mirroring for the capture session that a scene accessory depends on.
- duo-test: Device Hub poses, Split View passes, what cannot be automated.
- duo-ship: launch-screen requirement and TN3192 in the release checklist.
- duo-crossplatform: the React Native scene-lifecycle crash and Flutter's multi-scene limits in detail.
- duo-backend: process-scoped singletons, idempotent writes and analytics across two scenes.
