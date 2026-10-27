Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# iPhone Duo camera API reference

Every row carries its source. "[Apple]" means Apple documentation, a Tech Talk, release notes, the spec page, or a DTS/Apple engineer forum post. "(third-party, unverified)" and "(inferred)" are exactly that. Tech Talk quotations come from transcript summaries; API names and numbers were preserved, prose wording should be re-checked against the video page before quoting it as verbatim.

Contents
1. Hardware
2. Device types and the Virtual Front Camera
3. AVCaptureDeviceDirectionCoordinator, map, descriptor
4. Mirroring rules
5. Preview, aspect ratio, rotation
6. Camera capture accessory (SwiftUI and UIKit)
7. Reserved regions relevant to camera UI
8. Simulator and testing facts
9. Gaps and unverified items
10. Apple URLs used

## 1. Hardware

| Item | Value | Source |
|---|---|---|
| Outer front camera | "12MP Center Stage camera ƒ/2.2" | [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/) |
| Inner front camera | "Under-display FaceTime camera ƒ/1.8" | [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/) |
| Rear | 48MP Fusion Main (26 mm ƒ/1.6) and 48MP Fusion Ultra Wide (13 mm ƒ/2.2, 120°) | [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/) |
| Sensors | Both front cameras are "square sensors with an ultrawide field of view"; the inner is "the first under-display camera on iPhone" | [Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/) |
| Biometrics | Touch ID in the side button, no Face ID (matters for apps that assume a TrueDepth front camera) | [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/) |

## 2. Device types and the Virtual Front Camera

| Symbol | What Apple says | Min OS | Label |
|---|---|---|---|
| `AVCaptureDevice.DeviceType.builtInOuterUltraWideCamera` | Outer physical front camera, "up to 4K and 120fps" | iOS 27.1 SDK content; availability annotation not captured | [Apple] Tech Talk 111465 |
| `AVCaptureDevice.DeviceType.builtInInnerUltraWideCamera` | Inner physical front camera, "1080p up to 60fps" | iOS 27.1 SDK content; availability annotation not captured | [Apple] Tech Talk 111465 |
| `.builtInWideAngleCamera` / `.builtInUltraWideCamera` with `position == .front` | Returns the **Virtual Front Camera**, which "automatically switches between the outer and inner physical cameras" | existing symbols, new behaviour on Duo | [Apple] Tech Talk 111465; AVKit article |
| `AVCaptureDevice.isVirtualDevice` | `true` for the Virtual Front Camera | existing | [Apple] AVKit article |
| `AVCaptureDevice.activePrimaryConstituent` | Reports the physical camera currently streaming; nil until the session runs | existing | [Apple] AVKit article |
| Virtual Front Camera limits | Common subset only: 1080p/60, no depth. "Depth is only supported when accessing individual cameras" | | [Apple] Tech Talk 111465 |
| `.builtInDualWideCamera` | Appears in Apple's `deviceTypes` example as the rear camera entry | existing | [Apple] Tech Talk 111465. Whether it reports direction beyond being accepted is unconfirmed (gap). |

Sources: [Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/); [Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces). The reference pages for the two new constants were not located (a guessed AVFoundation URL returned 404), so their exact availability string is a gap.

## 3. AVCaptureDeviceDirectionCoordinator, map, descriptor

Module: the article "Choosing a camera by the direction it faces" lives under **AVKit**; the device types and `AVCaptureDevice` properties are AVFoundation. A guessed AVFoundation URL for the article returned 404 ([Apple] AVKit article; [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) links it under AVKit).

| Symbol | What Apple says | Label |
|---|---|---|
| `AVCaptureDeviceDirectionCoordinator` | "Initialized with a view, a list of device types, and a change handler. Its change handler is called on the main actor, first shortly after creation and again on each change. Keep a strong reference while the view is onscreen. Use one coordinator per preview view." | [Apple] AVKit article |
| `init(view:deviceTypes:changeHandler:)` | Labels taken from Apple's example call (see `samples.md`). Parameter types and the handler's parameter type are **inferred from the example**; the class reference page was not captured. | (inferred from Apple example) |
| `deviceDirections: AVCaptureDeviceDirectionMap` | Empty until the first handler call | [Apple] AVKit article |
| `AVCaptureDeviceDirectionMap.forwardFacingDeviceDescriptors: [AVCaptureDeviceDescriptor]` | "cameras facing the same way as the view. This is not the same as cameras whose position is `.front`" | [Apple] AVKit article |
| `AVCaptureDeviceDirectionMap.backwardFacingDeviceDescriptors` | Cameras facing away from the view | [Apple] AVKit article |
| `AVCaptureDeviceDescriptor` | Sendable; fields `deviceType`, `mediaTypes`, `position`, `uniqueID`, `localizedName` | [Apple] AVKit article |
| `AVCaptureDevice(uniqueID:)` | Resolve a descriptor to a device "on the session's actor" | [Apple] AVKit article |
| Main-actor isolation | The coordinator is main-actor isolated; descriptors are Sendable so they can cross to the session actor | [Apple] Tech Talk 111465 |

Rules, in Apple's words or close paraphrase (AVKit article unless noted):

1. List every built-in camera you capture from, including rear cameras: "a rear camera can face forward".
2. The coordinator ignores external, Continuity, and Desk View cameras and omits the virtual front camera.
3. Don't call AVFoundation from the handler.
4. If the active camera is still in the forward-facing array, keep it; otherwise pick a replacement.
5. Swap a single video input rather than building a multicam session.
6. Dual display: "Use one UIView and one direction coordinator per display ... the outer display's coordinator reports rear cameras as forward-facing" (Tech Talk 111465).

## 4. Mirroring rules

| Rule | Source |
|---|---|
| Decide mirroring from the direction map, not from `position` | [Apple] AVKit article |
| Connections auto-mirror any `.front` camera, so a forward-facing rear camera needs manual mirroring and a backward-facing front camera should be unmirrored | [Apple] AVKit article |
| "Set `automaticallyAdjustsVideoMirroring` to `false` before assigning `isVideoMirrored`, or the assignment raises an exception" | [Apple] AVKit article |
| Reapply mirroring after each new map and after adding a new input (a new input means a new connection) | [Apple] AVKit article |
| "When the rear camera is forward-facing, mirror the preview" | [Apple] Tech Talk 111465 |

Field reports repeat the first-set-`automaticallyAdjustsVideoMirroring` rule and the strong-reference rule (third-party, consistent with Apple: ecorpit, SwiftLee).

## 5. Preview, aspect ratio, rotation

| Symbol | What Apple says | Label |
|---|---|---|
| `AVCaptureVideoPreviewLayer.videoGravity: AVLayerVideoGravity` | Named as the first preview-polish step | [Apple] Tech Talk 111465 |
| `AVCaptureDevice.dynamicAspectRatio: AVCaptureDevice.AspectRatio?` | Read-only in the captured notes (`{ get }`); use it to "select a landscape aspect ratio on the inner display and fill the display" from the square sensor. No setter or request API was captured; do not invent one. | [Apple] Tech Talk 111465 |
| `AVCaptureDevice.RotationCoordinator` | Per device; recreate when switching cameras; "updates when the app moves between displays". The transcript summary spells it `AVCaptureDeviceRotationCoordinator`. The talk also references an unlinked article "Supporting Device Rotation in Your Camera App". | [Apple] Tech Talk 111465 |
| `AVCapturePhotoOutput.isCameraSensorOrientationCompensationEnabled: Bool` | Set to `false` after adopting the rotation coordinator "to improve performance"; compensation is on by default for all Duo front cameras | [Apple] Tech Talk 111465 |
| Layout | "Don't fake rotation by spinning UI elements. Use real size-class-driven layout" | [Apple] [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644) |
| Orientation | "The inner display doesn't honor supported interface orientations, so use size classes rather than orientation for layout decisions" | [Apple] [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/) |

## 6. Camera capture accessory (SwiftUI and UIKit)

Purpose (Apple): "Show content, such as a script, a countdown, or framing guides, on iPhone Duo's outer display for the person being recorded, while the capture interface stays on the inner display" ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)). The Technology Overview: "When iPhone Duo is fully open and capturing photos or video with the rear camera, it can show content on the outer display in addition to showing your app on the inner display" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).

| Symbol | Details | Min OS | Label |
|---|---|---|---|
| `nonisolated struct CameraCaptureAccessory<Content> where Content : View` | `init(content: () -> Content)`; `init(isEnabled: Binding<Bool>, content: () -> Content)`; conforms to `SceneAccessoryContent`; "Unlike `ExternalNonInteractiveAccessory`, the content can be interactive" | iOS 27.1+, iPadOS 27.1+ | [Apple] [CameraCaptureAccessory](https://developer.apple.com/documentation/swiftui/cameracaptureaccessory) |
| `View.sceneAccessory(content:)` | Attaches the accessory to the camera view | iOS 27.1+ | [Apple] CameraCaptureAccessory page |
| `SceneAccessoryContent.onAvailabilityChange(perform:)` | Handler receives a `Bool` | iOS 27.1+ | [Apple] Registering article |
| `ExternalNonInteractiveAccessory` | "A scene accessory that presents non-interactive content on an external display" (not the Duo outer display path) | iOS 27.1+ | [Apple] CameraCaptureAccessory page |
| `@MainActor class UISceneAccessory` | `class func cameraCapture(sceneConfiguration: UISceneConfiguration) -> Self`; `cameraCapture(sceneConfiguration:userInfo: Any)`; `externalNonInteractive(sceneConfiguration:)`; `externalNonInteractive(sceneConfiguration:userInfo:)` | iOS 27.0+, iPadOS 27.0+, Mac Catalyst 27.0+ | [Apple] [UISceneAccessory](https://developer.apple.com/documentation/uikit/uisceneaccessory) |
| `UIViewController.registerSceneAccessory(_:)` → `UISceneAccessoryRegistration` | `.isAvailable` read-only (ObjC `available`), `.isEnabled` read/write (ObjC `enabled`); read `isAvailable` in `updateProperties()`; `unregisterSceneAccessory(_:)` | iOS 27.0+ | [Apple] Registering article |
| `UISceneSession.Role.windowCameraCaptureAccessory` | ObjC `UIWindowSceneSessionRoleCameraCaptureAccessory`; "The system assigns the session role, so the app never sets it." | iOS 27.0+ | [Apple] Registering article |
| `connectionOptions.sceneAccessoryUserInfo` | Read the model passed as `userInfo` in `scene(_:willConnectTo:options:)` | iOS 27.0+ | [Apple] Registering article |
| Info.plist | "Accessory scenes have no project-level configuration, so a scene manifest (Info.plist) entry for one has no effect." | | [Apple] Registering article |

Conditions and behaviour:

- Available when "The app is full screen on the inner display. The app has an active camera session. The accessory is registered on the same view as the camera UI." ([Apple] Registering article; Tech Talk 111464: "available when your app is full screen on the inner display, and your app has an active camera session").
- "The app declares what content to provide. The system decides when and where to present it." Availability is set only by the system ([Apple] UISceneAccessory; Registering article).
- Content disappears when capture stops, the app leaves the foreground, or the device closes ([Apple] Registering article).
- Use `isEnabled`, don't unregister, to let users toggle ([Apple] Registering article).
- All essential controls must remain in the capture interface ([Apple] Registering article).
- "Non-camera apps can't draw directly on the outer display" ([Apple] Apple Developer Forums 847644).
- "Simulator has no camera, so test on a device before shipping" ([Apple] Registering article; Tech Talk 111464).
- Apple uses no "tent mode" or "flex mode" terminology; there is no system-provided rear-camera preview on the outer display. Rendering your own preview inside accessory content is the only route (inferred).
- The accessory scene runs as a separate scene in the same process (third-party, unverified: iPhone-Duo-by-Examples).

## 7. Reserved regions relevant to camera UI

- "The inner front-facing camera can block your view when it's active, and the outer front-facing camera always occludes your view" ([Apple] [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- HIG: "The outer front-facing camera. This region is always present, and expands into the Dynamic Island for Live Activities ... The inner front-facing camera. This region is only present when the camera is active" ([Apple] [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Custom UI overlapping the camera region without the reserved-region API has touch "suppressed or may not register as expected" ([Apple] Apple Developer Forums 847644).
- Query: SwiftUI `proxy.reservedRegions(kind: .occlusion)`; UIKit `view.reservedRegions(kind: .occlusion)` ([Apple] [GeometryProxy.reservedRegions](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)); [UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))). Full treatment in duo-layout.

## 8. Simulator and testing facts

| Fact | Source |
|---|---|
| "Simulator has no camera, so test on a device before shipping" | [Apple] Registering article; Tech Talk 111464 |
| Xcode 27.1 known issue: "In the iPhone Duo simulator, an app using `CameraCaptureAccessory` can use both displays at the same time without an active camera capture session. (190155353)" | [Apple] [Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes) |
| Xcode 27.2 RC notes record 190155353 as fixed | [Apple] [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes) |
| Device Hub pose controls: "Closed", "Partially Open", "Open" buttons; hold Option and drag the slider below the bezel to fold to any angle | [Apple] [Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub) |
| The simulator cannot test camera transitions, capture accessories, reachability, haptics, performance, memory, or thermals | (third-party, unverified: SwiftLee) |
| "Folded, the accessory isn't available" in the simulator | (third-party, unverified: iPhone-Duo-by-Examples) |

## 9. Gaps and unverified items

| Item | Status |
|---|---|
| Exact Swift signature of `AVCaptureDeviceDirectionCoordinator.init(view:deviceTypes:changeHandler:)` and the handler's parameter type | Inferred from Apple's example only; class reference page not captured. Verify against the 27A9275 SDK. |
| Availability annotations for the coordinator, `AVCaptureDeviceDescriptor`, `.builtInOuterUltraWideCamera`, `.builtInInnerUltraWideCamera` | Not stated on the fetched article; the Group Lab says the new APIs are iOS 27.1+ in general |
| Presence of the coordinator in SDK headers | One repo reported it "absent from the headers" of the 27A9269 beta (third-party, unverified: sven-ericmolzahn/iphone-duo-skill). Not re-checked against 27A9275 here. |
| Whether `.builtInDualWideCamera` or other rear types report direction beyond being accepted by the coordinator | Unconfirmed |
| How to request a particular `dynamicAspectRatio` | Only the read-only property was captured |
| Stream continuity across hinge transitions with the Virtual Front Camera; `CameraCaptureAccessory` orientation in the partially folded pose | Raised in the ended Photos & Camera Q&A ([Apple Forums activity 1659080](https://developer.apple.com/forums/activities/1659080)); no Apple answer captured |
| Any new permission, privacy-manifest entry, or Required Reason API for the accessory or hinge | None found (inferred from absence) |

## 10. Apple URLs used

- https://developer.apple.com/videos/play/tech-talks/111465/ (Build a great camera experience for iPhone Duo, 9:27)
- https://developer.apple.com/videos/play/tech-talks/111464/ (Leverage multiple displays and scenes on iPhone Duo, 7:17)
- https://developer.apple.com/videos/play/tech-talks/111461/ (Prepare your app for iPhone Duo)
- https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces
- https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo
- https://developer.apple.com/documentation/swiftui/cameracaptureaccessory
- https://developer.apple.com/documentation/uikit/uisceneaccessory
- https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo
- https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
- https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)
- https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)
- https://developer.apple.com/forums/thread/847644
- https://developer.apple.com/forums/activities/1659080
- https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes
- https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes
- https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub
- https://www.apple.com/iphone-duo/specs/
