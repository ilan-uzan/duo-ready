Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Multitasking, multiple scenes and scene accessories

Contents

1. Split View and the stacked video layout
2. Multiple instances of your app
3. Which scene stays active when the device closes
4. Scene accessories: `UISceneAccessory` and `CameraCaptureAccessory`
5. Gaps
6. Sources

Labels: statements without a label are Apple's, with the source inline. "(third-party, unverified)" marks blogs, GitHub READMEs and simulator measurements. "(inferred)" marks conclusions drawn by the report or this skill.

## 1. Split View and the stacked video layout

- "Every app participates in side-by-side multitasking. Apps that already support resizing on iPad or iPhone Mirroring should work with little extra effort. The new stacked video-and-app layout is handled the same way, using size classes and scene geometry." ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/))
- Split View is "a 50/50 layout started from the home gesture"; PiP "pins to top and the app resizes vertically in real time"; Split View and PiP "mean apps may run at varying aspect ratios, so they should be freely resizable" ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)).
- "Scene size can't be set directly. It's driven by pose and Split View"; "Free-form drag-to-resize isn't supported"; "iPhone Duo does not support Stage Manager and does not have its own `UIUserInterfaceIdiom`"; "iPad apps don't run in compatibility mode on iPhone Duo, unlike on Apple Vision Pro" ([thread 847644](https://developer.apple.com/forums/thread/847644)).
- "The PiP window moves to the outer display only when the device closes, under system control"; "Audio/video playback is associated with the most recent app that began the playback session"; PiP can be pinned to the top in landscape; audio-only content cannot be pinned like PiP (thread 847644).
- "Split View multitasking is supported on the inner display"; "In Split View multitasking, each app places controls on its outer edge" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). duo-bars covers the bar side.
- "Safe areas and layout margins are often asymmetric, so handle each side independently and test in Split View" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- How to test: drag "the app by the home indicator to either side of the screen, and check vertically laid-out content on both sides" (Tech Talk 111461).

There is nothing to opt into and nothing to opt out of: an app that resizes correctly for size classes is Split View ready. What Apple does not publish: Split View point sizes, whether the split is adjustable, whether three-column split views appear on the inner display (gaps; the 50/50 figure is from Tech Talk 111466 and the Group Lab).

Simulator observation (third-party, unverified, [iPhone-Duo-by-Examples](https://github.com/artemnovichkov/iPhone-Duo-by-Examples); also [iphoneduosupport.com](https://iphoneduosupport.com/frameworks/react-native/)): in Split View a visible app can be `inactive`, so pausing media on any non-active phase freezes visible content; pause on background only. Apple's own statements are that playback "continues through hinge changes" and that pause logic should not be tied to the fold; the `inactive` observation itself is not Apple's.

## 2. Multiple instances of your app

From Tech Talk 111464 unless marked:

- "iPhone Duo is the first iPhone to support multiple instances of your app's UI"; "On the outer display of iPhone Duo, new windows cannot be created. That behavior is reserved for the inner display."
- "creation availability is dynamic, so apps must handle errors when requesting scenes."
- Offer the action through `UIWindowSceneActivationAction`, "which hides automatically when new windows aren't available". The research notes render the same type as `UIWindowScene.ActivationAction`; both spellings came from transcript summaries, so confirm the exact name in the SDK headers (the report's discrepancy rule: prefer the doc spelling once seen).
- "Each app instance is its own `UIScene`/window, similar to iPad multi-window. New windows can only be created on the inner display. `UserDefaults` and `@AppStorage` are app-wide, not per-window" (thread 847644).

Checklist for an app that wants two instances:

| Item | Status |
|---|---|
| `UIApplicationSupportsMultipleScenes = YES` in the scene manifest | Standard iPad mechanism; no Duo-specific key in any Apple source (inferred) |
| Request new scenes through an error-handling path | Apple: "apps must handle errors when requesting scenes". The pre-existing API named in the report is `requestSceneSessionActivation`; Apple's Duo material does not name the method, so mapping Apple's sentence onto its error handler is the report's inference |
| Expose the "open in new window" affordance via `UIWindowSceneActivationAction` | Apple; it hides itself on the outer display |
| Per-window state in a scene-scoped model or `SceneStorage`, not `UserDefaults` / `@AppStorage` | Apple (app-wide) |
| Singletons (auth refresh, sockets, Core Data contexts, upload queues) process-scoped and idempotent | Inferred from the no-teardown statement; Apple's mid-checkout answer "doesn't address how to avoid duplicate network requests" |
| Privacy blur on resign-active applied per scene | Inferred: Split View shows two instances at once |
| SwiftUI `openWindow` | In the simulator it opened the new window full screen, not in Split View (third-party, unverified, iPhone-Duo-by-Examples) |

Cross-platform: Flutter's engine "does not fully support multi-scene" and its Info.plist template defaults `UIApplicationSupportsMultipleScenes` to false ([flutter #193056](https://github.com/flutter/flutter/issues/193056), third-party, closed as duplicate of #48838). duo-crossplatform has the detail.

## 3. Which scene stays active when the device closes

The DTS answer on `ScenePhase` during a fold, verbatim ([thread 847838](https://developer.apple.com/forums/thread/847838)):

"if your app is in full-screen using the entire open flat inner display, the scene is unaffected by the hinge state change ... Otherwise, if someone is using multi-window on the inner display, the most recently active scene window would be remain active when the device closes—the secondary window scene would transition to an inactive state, then backgrounded"

Consequences to tell the user:

- Single full-screen scene: no phase change on fold; the scene resizes.
- Two of your own windows open on the inner display, device closes: the most recently active one stays active; the other goes inactive, then background. The secondary window must therefore tolerate `sceneDidEnterBackground` mid-task, which is ordinary iPad multi-window hygiene.
- This is the only Apple statement about phase changes on fold. Whether other situations background a scene is a gap (report Appendix C).

## 4. Scene accessories: `UISceneAccessory` and `CameraCaptureAccessory`

Scene accessories are the only sanctioned way to show content on the outer display while the app runs on the inner one. "Non-camera apps can't draw directly on the outer display" (thread 847644). The Technology Overview frames the use case: "When iPhone Duo is fully open and capturing photos or video with the rear camera, it can show content on the outer display in addition to showing your app on the inner display" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). The AVFoundation article's examples are "a script, a countdown, or framing guides" for the person being recorded ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)).

### 4.1 UIKit surface

| Symbol | Notes | Source |
|---|---|---|
| `@MainActor class UISceneAccessory` | iOS 27.0+, iPadOS 27.0+, Mac Catalyst 27.0+ (note: 27.0, not 27.1) | [UISceneAccessory](https://developer.apple.com/documentation/uikit/uisceneaccessory) |
| `class func cameraCapture(sceneConfiguration: UISceneConfiguration) -> Self` | Camera-capture accessory | same |
| `cameraCapture(sceneConfiguration:userInfo: Any)` | Passes a model to the accessory scene | same |
| `externalNonInteractive(sceneConfiguration:)`, `externalNonInteractive(sceneConfiguration:userInfo:)` | Non-interactive content on an external display; its behavior on Duo is not described in the report (gap) | same |
| `UIViewController.registerSceneAccessory(_:)` → `UISceneAccessoryRegistration` | Register on the view controller that hosts the camera UI | Registering article |
| `UISceneAccessoryRegistration.isAvailable` (read-only; ObjC `available`) | System-controlled; read in `updateProperties()` | Registering article |
| `UISceneAccessoryRegistration.isEnabled` (read/write; ObjC `enabled`) | User toggle; "enabled by default and can be toggled at any time" | Registering article; Tech Talk 111464 |
| `UIViewController.unregisterSceneAccessory(_:)` | Exists; Apple says use `isEnabled` to toggle rather than unregistering | Registering article |
| `UISceneSession.Role.windowCameraCaptureAccessory` (ObjC `UIWindowSceneSessionRoleCameraCaptureAccessory`) | Role of the accessory scene; "The system assigns the session role, so the app never sets it" | Registering article |
| `connectionOptions.sceneAccessoryUserInfo` in `scene(_:willConnectTo:options:)` | Where the `userInfo` model arrives | Registering article |
| Scene manifest | "Accessory scenes have no project-level configuration, so a scene manifest (Info.plist) entry for one has no effect" | Registering article |

Apple's UIKit snippet (verbatim from the report):

```swift
let accessory = UISceneAccessory.cameraCapture(sceneConfiguration: configuration, userInfo: script)
registration = registerSceneAccessory(accessory)
registration?.isEnabled = isScriptEnabled
```

### 4.2 SwiftUI surface

| Symbol | Notes | Source |
|---|---|---|
| `nonisolated struct CameraCaptureAccessory<Content> where Content : View` | iOS 27.1+, iPadOS 27.1+ | [CameraCaptureAccessory](https://developer.apple.com/documentation/swiftui/cameracaptureaccessory) |
| `init(content:)`, `init(isEnabled: Binding<Bool>, content:)` | | same |
| Conforms to `SceneAccessoryContent` | "Unlike `ExternalNonInteractiveAccessory`, the content can be interactive" | same |
| `View.sceneAccessory(content:)` | Attach to the camera view | same |
| `SceneAccessoryContent.onAvailabilityChange(perform:)` | Receives a `Bool` | Registering article |
| `ExternalNonInteractiveAccessory` | "A scene accessory that presents non-interactive content on an external display"; Duo behavior not described (gap) | CameraCaptureAccessory page |

Apple's teleprompter code (verbatim, Tech Talk 111464):

```swift
CameraView(model: model)
    .sceneAccessory {
        CameraCaptureAccessory(isEnabled: $model.isEnabled) {
            TeleprompterView(model: model)
        }
        .onAvailabilityChange { newValue in
            model.isAvailable = newValue
        }
    }
    .toolbar {
        TeleprompterToggle(isEnabled: $model.isEnabled)
            .disabled(!model.isAvailable)
    }
```

### 4.3 Conditions and rules

- Availability conditions: "The app is full screen on the inner display. The app has an active camera session. The accessory is registered on the same view as the camera UI" (Tech Talk 111464; Registering article).
- Content disappears when capture stops, the app leaves the foreground, or the device closes. Let users toggle with `isEnabled`; do not unregister. All essential controls must remain in the capture interface; the accessory is for the subject, not the operator (Registering article).
- "The app declares what content to provide. The system decides when and where to present it" (UISceneAccessory page).
- "Simulator has no camera, so test on a device before shipping" (thread 847644). Xcode 27.1 known issue: "In the iPhone Duo simulator, an app using `CameraCaptureAccessory` can use both displays at the same time without an active camera capture session. (190155353)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)); the 27.2 RC notes record it fixed ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). An accessory that appears in the 27.1 simulator without a session proves nothing about devices.
- Simulator observations (third-party, unverified, iPhone-Duo-by-Examples): the accessory scene runs as "a separate scene, same process"; "Folded, the accessory isn't available."
- Inferred: the content is seen by a third party, so keep sensitive data out of it.
- A camera app on both displays needs one `UIView` and one `AVCaptureDeviceDirectionCoordinator` per display (Tech Talk 111465); duo-camera covers the session side.
- A listed but unanswered Q&A topic: "CameraCaptureAccessory: orientation in the partially folded pose" ([Apple Forums activity 1659080](https://developer.apple.com/forums/activities/1659080)); no answer was captured.

## 5. Gaps

- Split View point sizes and whether the ratio is adjustable.
- Three-column split views on the inner display.
- Exact spelling `UIWindowSceneActivationAction` vs `UIWindowScene.ActivationAction`; confirm in headers.
- Whether `requestSceneSessionActivation` is the intended request path; Apple's sentence names no method.
- What `externalNonInteractive` accessories do on Duo, if anything.
- Accessory orientation in the partially folded pose.
- Any phase change on fold beyond the multi-window answer.

## 6. Sources

| Source | URL |
|---|---|
| Tech Talk 111464, Leverage multiple displays and scenes on iPhone Duo | https://developer.apple.com/videos/play/tech-talks/111464/ |
| Tech Talk 111466, Design for iPhone Duo | https://developer.apple.com/videos/play/tech-talks/111466/ |
| Tech Talk 111461, Prepare your app for iPhone Duo | https://developer.apple.com/videos/play/tech-talks/111461/ |
| Tech Talk 111465, Build a great camera experience for iPhone Duo | https://developer.apple.com/videos/play/tech-talks/111465/ |
| DTS: A Summary of the iPhone Duo Group Lab (thread 847644) | https://developer.apple.com/forums/thread/847644 |
| DTS: ScenePhase during fold (thread 847838) | https://developer.apple.com/forums/thread/847838 |
| HIG: Designing for iPhone Duo | https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo |
| Preparing your app for iPhone Duo | https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo |
| UISceneAccessory | https://developer.apple.com/documentation/uikit/uisceneaccessory |
| Registering a camera capture accessory on iPhone Duo | https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo |
| CameraCaptureAccessory | https://developer.apple.com/documentation/swiftui/cameracaptureaccessory |
| Xcode 27.1 Release Notes | https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes |
| Xcode 27.2 RC Release Notes | https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes |
| Apple Forums activity 1659080 | https://developer.apple.com/forums/activities/1659080 |
| iPhone-Duo-by-Examples (third-party) | https://github.com/artemnovichkov/iPhone-Duo-by-Examples |
| iphoneduosupport.com React Native page (third-party) | https://iphoneduosupport.com/frameworks/react-native/ |
| flutter #193056 (third-party) | https://github.com/flutter/flutter/issues/193056 |
