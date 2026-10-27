Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Camera samples for iPhone Duo

Two kinds of code live here. Sections 1 and 2 are Apple's own snippets, copied verbatim from the Tech Talk transcripts and documentation articles the report cites; they are the only camera code Apple has published for Duo (there is no Apple sample project, and none of the six Tech Talk pages links one). Section 3 is composed from Apple-documented symbols and has **not** been compiled against the iOS 27.1 SDK; its header says so, and you should say so to the user.

## 1. Apple's direction coordinator init (verbatim)

From Tech Talk 111465, "Create a direction coordinator" chapter ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)). Apple shows it inside a view controller or model that owns `view`; `directionCoordinator` must be a strong stored property.

```swift
directionCoordinator = AVCaptureDeviceDirectionCoordinator(
    view: view,
    deviceTypes: [
        .builtInOuterUltraWideCamera,
        .builtInInnerUltraWideCamera,
        .builtInDualWideCamera,
    ],
    changeHandler: { [weak self] map in
        self?.updateCameraSession(map)
    }
)
```

What this snippet establishes and what it does not:

- Established: argument labels `view:`, `deviceTypes:`, `changeHandler:`; the handler receives one value Apple names `map` (the `AVCaptureDeviceDirectionMap`); the device-type list mixes physical front types with a rear type, matching the AVKit article's rule to list rear cameras because "a rear camera can face forward".
- Not established: the declared parameter types, whether the handler is `@MainActor`-annotated in the declaration (the article says it "is called on the main actor"), and the availability annotation. These are gaps; confirm in the 27A9275 SDK headers. One third-party repo reported the symbol absent from the 27A9269 beta headers (third-party, unverified).

## 2. Apple's camera capture accessory code (verbatim)

### SwiftUI teleprompter

From Tech Talk 111464, "Teleprompter accessory" chapter, also shown on the SwiftUI reference page ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/); [CameraCaptureAccessory](https://developer.apple.com/documentation/swiftui/cameracaptureaccessory)). The research notes record the surrounding view as Apple showed it:

```swift
struct CameraRootView: View {
    @State private var model = TeleprompterModel()

    var body: some View {
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
    }
}
```

Points Apple makes with it: the accessory is attached to the camera view (the rule "registered on the same view as the camera UI"); `isEnabled` is the user toggle; `onAvailabilityChange` is how the app learns that the system can present the accessory, and the toggle is disabled otherwise; the toggle itself stays in the capture UI ("all essential controls must remain in the capture interface"). `CameraView`, `TeleprompterView`, `TeleprompterModel`, and `TeleprompterToggle` are Apple's placeholders, not framework types.

### UIKit registration

From "Registering a camera capture accessory on iPhone Duo" ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)):

```swift
let accessory = UISceneAccessory.cameraCapture(sceneConfiguration: configuration,
                                               userInfo: script)
registration = registerSceneAccessory(accessory)
registration?.isEnabled = isScriptEnabled
```

Surrounding facts from the same article: `registerSceneAccessory(_:)` is a `UIViewController` method returning `UISceneAccessoryRegistration`; read `registration.isAvailable` in `updateProperties()`; the accessory scene connects with role `UISceneSession.Role.windowCameraCaptureAccessory` and the `script` object arrives as `connectionOptions.sceneAccessoryUserInfo` in `scene(_:willConnectTo:options:)`; the system assigns the role and an Info.plist scene-manifest entry "has no effect".

## 3. Composed: handle a direction change and reapply mirroring

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
// Duo-specific symbols (AVCaptureDeviceDirectionMap, AVCaptureDeviceDescriptor,
// forwardFacingDeviceDescriptors, uniqueID) are from Apple's AVKit article
// "Choosing a camera by the direction it faces". The AVCaptureSession plumbing
// (beginConfiguration/commitConfiguration, AVCaptureDeviceInput, connections)
// is standard pre-Duo AVFoundation and was not re-verified for this skill.
import AVFoundation
import AVKit

// Called from the coordinator's change handler. The handler runs on the main
// actor and Apple says not to call AVFoundation from it, so only Sendable
// descriptors cross to the session's actor.
@MainActor
func updateCameraSession(_ map: AVCaptureDeviceDirectionMap) {
    let forward = map.forwardFacingDeviceDescriptors
    Task { await sessionController.apply(forwardFacing: forward) }
}

actor SessionController {
    let session: AVCaptureSession
    private var currentInput: AVCaptureDeviceInput?

    init(session: AVCaptureSession) { self.session = session }

    func apply(forwardFacing descriptors: [AVCaptureDeviceDescriptor]) {
        // Apple: if the active camera is still forward-facing, keep it.
        if let current = currentInput,
           descriptors.contains(where: { $0.uniqueID == current.device.uniqueID }) {
            reapplyMirroring(isForwardFacing: true)
            return
        }

        // Otherwise pick a replacement from the forward-facing array and swap
        // the single video input (Apple: do not build a multicam session).
        guard let descriptor = descriptors.first,
              let device = AVCaptureDevice(uniqueID: descriptor.uniqueID),
              let newInput = try? AVCaptureDeviceInput(device: device) else { return }

        session.beginConfiguration()
        if let old = currentInput { session.removeInput(old) }
        if session.canAddInput(newInput) {
            session.addInput(newInput)
            currentInput = newInput
        }
        session.commitConfiguration()

        // A new input means a new connection, so mirroring must be set again.
        reapplyMirroring(isForwardFacing: true)
    }

    private func reapplyMirroring(isForwardFacing: Bool) {
        for connection in session.connections where connection.isVideoMirroringSupported {
            // Apple: set automaticallyAdjustsVideoMirroring to false first,
            // or assigning isVideoMirrored raises an exception.
            connection.automaticallyAdjustsVideoMirroring = false
            // Derived from two Apple statements: mirror when the camera faces the
            // viewer ("When the rear camera is forward-facing, mirror the preview")
            // and un-mirror a front camera that faces away.
            connection.isVideoMirrored = isForwardFacing
        }
    }
}
```

Notes for the model using this sample:

- Choosing `descriptors.first` is a placeholder policy. A real app should prefer by `deviceType` (for example the outer ultra wide for 4K/120) and fall back; Apple does not prescribe the order.
- Rotation is not shown. Apple's guidance is to adopt `AVCaptureDevice.RotationCoordinator` per device, recreate it when the camera changes, and then set `AVCapturePhotoOutput.isCameraSensorOrientationCompensationEnabled = false` for performance ([Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/)). The talk references an unlinked article "Supporting Device Rotation in Your Camera App" for the mechanics; that article was not captured by the research, so do not improvise its API surface.
- For two previews (one per display), Apple says to create one `UIView` and one coordinator per display and to expect the outer display's coordinator to report rear cameras as forward-facing. Each coordinator's handler should drive its own mirroring decision for its own preview connection.
- Nothing here can be exercised in the simulator; "Simulator has no camera".
