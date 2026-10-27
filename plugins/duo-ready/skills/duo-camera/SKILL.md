---
name: duo-camera
description: >-
  Make AVFoundation camera code work on iPhone Duo, where a "front" camera is
  not always looking at the user: the two front cameras
  (.builtInOuterUltraWideCamera, .builtInInnerUltraWideCamera), the Virtual
  Front Camera, AVCaptureDeviceDirectionCoordinator (AVKit), preview
  mirroring, dynamicAspectRatio and rotation, and CameraCaptureAccessory /
  UISceneAccessory.cameraCapture for a script or countdown on the outer
  display during rear-camera capture. Use it whenever capture code meets the
  new iPhone, the foldable, or two displays, even if nobody says "Duo":
  "selfie camera shows the ceiling when the phone is open", "front preview is
  mirrored wrong", "camera points away from the user", "4K selfie only gives
  1080p", "no depth from the front camera", "isVideoMirrored throws",
  "teleprompter on the outside screen while recording", "preview letterboxed
  on the big screen", "rotation wrong when the phone opens". Also use it to
  review an AVCaptureSession setup for Duo readiness before shipping.
---

# duo-camera

## What Apple actually says

- iPhone Duo is "the first iPhone to support two front cameras", both "square sensors with an ultrawide field of view"; the inner one is "the first under-display camera on iPhone". Device types are `.builtInOuterUltraWideCamera` ("up to 4K and 120fps") and `.builtInInnerUltraWideCamera` ("1080p up to 60fps") ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)).
- Asking for `.builtInWideAngleCamera` or `.builtInUltraWideCamera` at position `.front` returns the **Virtual Front Camera** (`isVirtualDevice == true`), which "automatically switches between the outer and inner physical cameras" but is limited to 1080p/60 with no depth: "Depth is only supported when accessing individual cameras" ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/); [Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces)).
- "a front camera is not always looking at you", so `AVCaptureDevice.position` is insufficient. Use `AVCaptureDeviceDirectionCoordinator` (AVKit module) to learn which cameras face the same way as a given view, and decide mirroring from that map, not from `.front`/`.back` ([Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces)).
- "When iPhone Duo is fully open and capturing photos or video with the rear camera, it can show content on the outer display in addition to showing your app on the inner display"; that is the camera capture accessory (`CameraCaptureAccessory` in SwiftUI, `UISceneAccessory.cameraCapture` in UIKit) ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo); [Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)).
- "Simulator has no camera, so test on a device before shipping" ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/); [Registering a camera capture accessory](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)).
- All of these symbols are iOS 27.1 SDK content except `UISceneAccessory`, which is iOS 27.0+. Apple has not published the exact Swift initializer signature of the direction coordinator on a reference page the research team could fetch; the signature in this skill is inferred from Apple's own example (see "What is not proven" below).

## Workflow

Ask for the user's capture code before advising. You need to see three things: how they discover the device (`AVCaptureDevice.default(...)`, `AVCaptureDevice.DiscoverySession`, hard-coded `position: .front`), how they build the preview (`AVCaptureVideoPreviewLayer`, connection mirroring, rotation), and whether they have any dual-display intent (teleprompter, countdown, framing guide for the subject). If a project path is available, run `python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>` first; its adoption report lists whether `AVCaptureDeviceDirectionCoordinator`, the inner/outer device types, or `CameraCaptureAccessory` already appear, and its findings catch the `UIScreen.main` and orientation assumptions that also break camera UIs.

### Step 1: Decide which camera abstraction the app needs

Three choices, from least to most work. Pick by feature need, not by device detection; the Group Lab says the new APIs are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo" and recommends "gating iOS 27.1 APIs behind availability checks" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

| Need | Use | Why |
|---|---|---|
| A selfie camera that just works, 1080p/60 is enough, no depth | Keep `.builtInWideAngleCamera` / `.builtInUltraWideCamera` at `.front` (the Virtual Front Camera) | It "automatically switches between the outer and inner physical cameras" as the device opens and closes. `activePrimaryConstituent` tells you which physical camera is streaming (nil until the session runs) ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)). |
| 4K or 120 fps selfie, depth, or per-camera formats | Address `.builtInOuterUltraWideCamera` / `.builtInInnerUltraWideCamera` individually | The virtual device is capped at the common subset; "Depth is only supported when accessing individual cameras" ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)). Once you address physical cameras you own the switching, so you need Step 2. |
| Any UI where the preview must show the person looking at the screen, including rear cameras facing the subject | Individual cameras plus `AVCaptureDeviceDirectionCoordinator` | Only the coordinator knows which cameras face the same way as your view; `position` cannot ([Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces)). |

Explain the trade-off to the user. Many apps should stay on the virtual camera; the coordinator path is for apps that need the outer camera's 4K/120, depth, or correct behaviour on both displays.

### Step 2: Adopt the direction coordinator (when Step 1 says so)

Apple's rules, from the AVKit article, in the order you apply them ([Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces); [Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)):

1. Create one coordinator per preview view, "Initialized with a view, a list of device types, and a change handler." Apple's own init call (verbatim, Tech Talk 111465) is in `references/samples.md`. The device-type list is the full set of built-in cameras you will ever capture from, including rear cameras, because "a rear camera can face forward" when the device is open and the outer display is what the person sees.
2. Keep a strong reference "while the view is onscreen". A local or weak reference drops the coordinator and the handler stops firing.
3. The change handler "is called on the main actor, first shortly after creation and again on each change". `deviceDirections: AVCaptureDeviceDirectionMap` is empty until that first call, so do not read it synchronously after init.
4. In the handler, read `forwardFacingDeviceDescriptors` ("cameras facing the same way as the view. This is not the same as cameras whose position is `.front`") and `backwardFacingDeviceDescriptors`. Each `AVCaptureDeviceDescriptor` is Sendable and carries `deviceType`, `mediaTypes`, `position`, `uniqueID`, `localizedName`.
5. Do not call AVFoundation from the handler. Hand the descriptors to your session actor/queue and resolve them there with `AVCaptureDevice(uniqueID:)`.
6. If the currently active camera is still in the forward-facing array, keep it. Otherwise pick a replacement from that array and swap the single video input. Apple says to swap one input rather than build a multicam session.
7. The coordinator ignores external, Continuity, and Desk View cameras and omits the virtual front camera. If the app lists only the virtual front camera in `deviceTypes`, the map will not contain it; list the physical front types and the rear types instead.

### Step 3: Fix mirroring

Connections auto-mirror any `.front` camera, which is wrong when that camera faces away from the person and wrong when a rear camera faces the person. Apple's rule: "Set `automaticallyAdjustsVideoMirroring` to `false` before assigning `isVideoMirrored`, or the assignment raises an exception", decide mirroring from the direction map, and reapply it after every new map and after every new input (a new input creates a new connection) ([Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces)). Tech Talk 111465 states the dual-display consequence directly: "When the rear camera is forward-facing, mirror the preview". A composed example of the swap-and-mirror step, with the required "not compile-checked" header, is in `references/samples.md`.

### Step 4: Polish the preview on the inner display

- Set `AVCaptureVideoPreviewLayer.videoGravity` deliberately; the square sensors and the inner display's shape mean the default framing may letterbox.
- Read `AVCaptureDevice.dynamicAspectRatio: AVCaptureDevice.AspectRatio?` to "select a landscape aspect ratio on the inner display and fill the display" from the square sensor ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)). The property is read-only in the fetched notes; how to request a particular ratio was not captured, so do not invent a setter.
- Adopt `AVCaptureDevice.RotationCoordinator` (the Tech Talk transcript spells it `AVCaptureDeviceRotationCoordinator`); recreate it when switching cameras because it is per device, and note that it "updates when the app moves between displays". After adopting it, set `AVCapturePhotoOutput.isCameraSensorOrientationCompensationEnabled = false` "to improve performance"; compensation is on by default for all Duo front cameras ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)).
- Do not rotate the preview or controls by hand: "Don't fake rotation by spinning UI elements. Use real size-class-driven layout" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Capture UI is still UI; the inner display ignores supported orientations, so lay out controls from size classes (see duo-layout).
- Keep controls out of the camera occlusion. The HIG describes the inner front camera region as "only present when the camera is active" and the outer one as always present; the Group Lab warns that custom UI overlapping the camera region without the reserved-region API has touch "suppressed or may not register as expected" ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo); [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Query `reservedRegions(kind: .occlusion)`; duo-layout covers the API.

### Step 5: Dual-display capture (outer-display content while capturing)

Two different things live here; keep them apart for the user.

**Preview on both displays.** "Use one UIView and one direction coordinator per display ... the outer display's coordinator reports rear cameras as forward-facing" ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)). Each display's view gets its own coordinator and its own mirroring decision.

**Content for the subject on the outer display.** `CameraCaptureAccessory` (SwiftUI, iOS 27.1+) or `UISceneAccessory.cameraCapture(sceneConfiguration:userInfo:)` registered with `UIViewController.registerSceneAccessory(_:)` (UIKit, iOS 27.0+). Apple's teleprompter code, verbatim, is in `references/samples.md`. The rules ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo); [Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/); [UISceneAccessory](https://developer.apple.com/documentation/uikit/uisceneaccessory)):

- Available only when "The app is full screen on the inner display. The app has an active camera session. The accessory is registered on the same view as the camera UI."
- "The app declares what content to provide. The system decides when and where to present it." Availability is read-only: `UISceneAccessoryRegistration.isAvailable` (read it in `updateProperties()`), or `SceneAccessoryContent.onAvailabilityChange(perform:)` in SwiftUI.
- Content disappears when capture stops, the app leaves the foreground, or the device closes. Let users toggle with `isEnabled`; do not unregister to toggle.
- "all essential controls must remain in the capture interface". The accessory is for the person being recorded (script, countdown, framing guides); the shutter stays on the inner display.
- The accessory scene's role is `UISceneSession.Role.windowCameraCaptureAccessory`; the system assigns it, and "a scene manifest (Info.plist) entry for one has no effect". Read your model from `connectionOptions.sceneAccessoryUserInfo` in `scene(_:willConnectTo:options:)`.
- "Non-camera apps can't draw directly on the outer display" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). If the user wants an outer-display UI without a running camera session, this API will not give it to them.
- Accessory content faces a third party, so keep anything sensitive out of it (inferred; Apple states the conditions, not this consequence).

### Step 6: Verify

- The simulator cannot exercise any of this: "Simulator has no camera". Camera switching, direction changes, mirroring, and accessory availability need a device.
- Known simulator behaviour to warn about: in Xcode 27.1 "an app using `CameraCaptureAccessory` can use both displays at the same time without an active camera capture session. (190155353)"; the Xcode 27.2 RC notes record it as fixed ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). An accessory that appears in the simulator without a session proves nothing about the device.
- On device, walk the poses in Device Hub order (closed, partially open, open) with the app running, and confirm: the preview shows the person looking at the active display; mirroring is correct for a rear camera facing forward and a front camera facing away; the preview fills the inner display; rotation follows the display without spinning views; the accessory appears only while capturing full screen on the inner display and disappears when the device closes. Steps for the manual pass are in duo-test.

## Common mistakes

- Equating `position == .front` with "faces the user" (Apple: insufficient on Duo) and discovering only the virtual camera when the app needs 4K, 120 fps, or depth.
- Listing only front device types in the coordinator, so a rear camera that faces the person is never offered; and expecting the virtual front camera in the map, which the coordinator omits.
- Assigning `isVideoMirrored` without first setting `automaticallyAdjustsVideoMirroring = false` (Apple: raises an exception), or setting mirroring once and not reapplying after a new map or new input. (Field reports echo the same two items; third-party, consistent with Apple.)
- Dropping the coordinator (no strong reference) or reading `deviceDirections` before the first handler call.
- Calling AVFoundation from the change handler instead of forwarding the Sendable descriptors to the session actor.
- Building a multicam session to "cover both cameras" when Apple says to swap a single input.
- Keeping `isCameraSensorOrientationCompensationEnabled` at its default after adopting the rotation coordinator (Apple: disable it to improve performance).
- Spinning the preview or controls with a transform on fold or rotation (Apple: don't fake rotation).
- Putting the record button or other essential controls in the accessory, unregistering the accessory to hide it, adding an Info.plist scene entry for it, or trying to use it without a running camera session.
- Treating the Xcode 27.1 simulator's accessory behaviour (190155353) as device behaviour, or shipping camera changes tested only in the simulator.

## What is not proven (say so to the user)

- The Swift signature `AVCaptureDeviceDirectionCoordinator(view:deviceTypes:changeHandler:)` and the handler's parameter type are inferred from Apple's Tech Talk example; the class reference page was not captured, and availability annotations for the coordinator, `AVCaptureDeviceDescriptor`, and the two new device-type constants were not stated on the fetched article. One third-party repo reported the coordinator "absent from the headers" of the 27A9269 beta SDK (third-party, unverified). Tell the user to confirm the symbol in the Xcode 27.1 (27A9275) SDK before relying on autocomplete to fill it in, and to keep `#if canImport`/`#available` guards (see duo-audit for the compile-guard notes).
- Whether `.builtInDualWideCamera` and other rear device types report direction beyond being accepted in the `deviceTypes` list is unconfirmed; Apple's example lists it, nothing more.
- No Apple answer was captured for "AVCaptureDeviceDiscoverySession & stream continuity across hinge transitions with Virtual Front Camera" or "CameraCaptureAccessory: orientation in the partially folded pose"; both were topics of the ended Photos & Camera Q&A ([Apple Forums activity 1659080](https://developer.apple.com/forums/activities/1659080)). Do not guess the behaviour; recommend testing on device.
- Apple uses no "tent mode" or "flex mode" terminology and provides no system rear-camera preview on the outer display; that effect is built with accessory content you render yourself (inferred from the accessory rules).

## When to read the references

- `references/camera-api.md`: symbol table (device types, virtual camera properties, coordinator, map, descriptor, mirroring, rotation, accessory APIs) with availability and label per row; hardware specs; the full list of Apple rules quoted verbatim.
- `references/samples.md`: Apple's verbatim coordinator init and teleprompter code (SwiftUI and UIKit), plus a composed, clearly labelled swap-and-mirror handler.

## Related skills

- duo-scenes: scene accessories in general (`ExternalNonInteractiveAccessory`, session roles, multi-window), fold as trait change, hinge API.
- duo-layout: reserved regions (`.occlusion` for the camera, `.division` for the fold), size classes for the capture UI.
- duo-test: device vs simulator matrix, manual pass, what cannot be automated.
- duo-audit: run the scanner first; its adoption report shows which camera APIs the project already uses.
- duo-ship: App Store screenshots and previews if the camera UI is in them.
