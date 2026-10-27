Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Hinge API: `onHingeChange`, `DeviceHinge`, `UIHingeInteraction`, `UIHinge`

Contents

1. Apple's rule: effects, not layout
2. SwiftUI surface and Apple's samples
3. UIKit surface and Apple's sample
4. Status cases: what is and is not confirmed
5. Availability and compile guards
6. Motion (Core Motion) on a two-body device
7. Testing the hinge in Device Hub
8. Gaps
9. Sources

Labels: statements without a label are Apple's, with the source inline. "(third-party, unverified)" marks blogs, GitHub READMEs and simulator measurements. "(inferred)" marks conclusions drawn by the report or this skill.

## 1. Apple's rule: effects, not layout

"SwiftUI provides the `onHingeChange` modifier, and UIKit provides `UIHingeInteraction`. Both report the high-level hinge status (closed, partially open, fully open) and continuous hinge angle updates ... Hinge data is ideal for driving interactions and effects. For layout decisions, use the arrangement and region APIs" ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/), chapters: Respond to the hinge 0:49, Pitch bend demo 1:18, Hinge data vs layout APIs 2:35).

From the DTS Group Lab summary ([thread 847644](https://developer.apple.com/forums/thread/847644)):

- "There's no single pose API. Infer pose from hinge status, angle, orientation, and size class together."
- Hinge "Update rate and precision are system policy, so don't depend on specific values. Use for effects, not layout."
- "Hinge changes are just geometry/trait changes."
- No angle thresholds separating tent, laptop and book exist in any Apple source.

Layout questions (what sits above or below the fold, how a grid splits) belong to `reservedRegions(kind: .division)` and `ArrangementView` / `UIArrangementViewController`, covered by duo-layout. Apple's own effect example is a guitar pitch bend driven by the angle while the device is partially open.

## 2. SwiftUI surface and Apple's samples

| Symbol | Signature / notes | Source |
|---|---|---|
| `onHingeChange` | `nonisolated func onHingeChange(isEnabled: Bool = true, _ action: @escaping (DeviceHingeContext, DeviceHingeContext) -> Void) -> some View`; iOS 27.1+, iPadOS 27.1+, Mac Catalyst 27.1+, macOS 27.1+, tvOS 27.1+, visionOS 27.1+, watchOS 27.1+; "Use this modifier to be informed of changes to the hinge context of the device." | [onHingeChange(isEnabled:_:)](https://developer.apple.com/documentation/swiftui/view/onhingechange(isenabled:_:)) |
| `DeviceHingeContext` | "A type describing the context of hinges on the device"; `hinge: DeviceHinge?`, nil on devices without a hinge | same page; Tech Talk 111464 |
| `DeviceHinge` | `struct DeviceHinge` (Equatable, Hashable, Sendable); `angle: Angle`; `status: DeviceHinge.Status`; "A hinge provides its angle along with a status determined by the system based on the current angle and device orientation." | [DeviceHinge](https://developer.apple.com/documentation/swiftui/devicehinge) |

The closure receives two contexts; Apple's samples use the second as the new value. `angle` is a SwiftUI `Angle`, so read `.degrees` or `.radians` explicitly.

Apple's reference-page example (verbatim, DeviceHinge page):

```swift
@State private var hinge: DeviceHinge? = nil

var body: some View {
    VStack {
        if let hinge {
            AngleDisplayView(angle: hinge.angle)
            StatusDisplayView(status: hinge.status)
        } else {
            ContentUnavailableView("Hinge Unavailable", systemImage: "rectangle.split.2x1")
        }
    }
    .onHingeChange { _, newContext in
        hinge = newContext.hinge
    }
}
```

Apple's Tech Talk example (verbatim, Tech Talk 111464):

```swift
GuitarView(pitchBend: pitchBend)
    .onHingeChange { _, context in
        if let hinge = context.hinge, hinge.status == .partiallyOpen {
            pitchBend = calculatePitchBend(angle: hinge.angle)
        } else {
            pitchBend = 0
        }
    }
```

Third-party observations (unverified, [iPhone-Duo-by-Examples](https://github.com/artemnovichkov/iPhone-Duo-by-Examples)): `angle` reads 180° when the device is flat; `isEnabled: false` pauses delivery; the action runs with the initial state and on every change.

## 3. UIKit surface and Apple's sample

| Symbol | Signature / notes | Source |
|---|---|---|
| `UIHingeInteraction` | `@MainActor class UIHingeInteraction : NSObject, UIInteraction`; iOS 27.1+, iPadOS 27.1+, Mac Catalyst 27.1+, tvOS 27.1+, visionOS 27.1+ | [UIHingeInteraction](https://developer.apple.com/documentation/uikit/uihingeinteraction) |
| `init(updateHandler:)` | `init(updateHandler: (UIHingeInteraction, UIHingeInteraction.Update) -> Void)`; ObjC `initWithUpdateHandler:` | same |
| `isEnabled` | `var isEnabled: Bool` | same |
| `UIHingeInteraction.Update` | ObjC `UIHingeInteractionUpdate`; `hinge: UIHinge?`; nil means "the interaction has left a hierarchy that provides hinge updates" | same |
| `UIHinge` | `@MainActor class UIHinge : NSObject` (NSCopying, Sendable); `var angle: CGFloat` ("The current angle of the hinge, in radians."); `var status: UIHinge.Status` (ObjC `UIHingeStatus`) | [UIHinge](https://developer.apple.com/documentation/uikit/uihinge) |

Attach with `view.addInteraction(interaction)` like any `UIInteraction`. Units: UIKit gives radians as `CGFloat`; SwiftUI gives `Angle`. Do not compare one to the other without converting.

Apple's example (verbatim, UIHingeInteraction page):

```swift
override func viewDidLoad() {
    super.viewDidLoad()

    let interaction = UIHingeInteraction { [weak self] _, update in
        guard let self else { return }
        // A nil `hinge` indicates the interaction has left a
        // hierarchy that provides hinge updates.
        guard let hinge = update.hinge else {
            handleHingeUnavailable()
            return
        }

        updateAngleDisplay(with: hinge.angle)
        updateStatusDisplay(with: hinge.status)
    }

    view.addInteraction(interaction)
}
```

## 4. Status cases: what is and is not confirmed

Tech Talk 111464 describes the statuses in prose as "closed, partially open, fully open". Only one case name appears in Apple code.

| Case | SwiftUI `DeviceHinge.Status` | UIKit `UIHinge.Status` | Status |
|---|---|---|---|
| `.partiallyOpen` | In Apple's Tech Talk code | Implied by the same prose | Confirmed by Apple code (SwiftUI) |
| `.closed` | Reported by third parties | Reported by third parties | third-party, unverified ([iPhone-Duo-by-Examples](https://github.com/artemnovichkov/iPhone-Duo-by-Examples); [ecorpit](https://ecorpit.com/iphone-duo-sdk-new-apis-xcode-27-1-developer-guide-2026/)) |
| `.fullyOpen` | Reported by third parties | Reported by third parties | third-party, unverified (same) |
| `.unknown` | Not reported | Reported by one source only | third-party, unverified (ecorpit only) |

The Apple `DeviceHinge.Status` and `UIHinge.Status` pages were not fetched by the research (report Appendix C; notes list `swiftui/devicehinge/status` and `uikit/uihinge/status` as unfetched). When writing code, use `.partiallyOpen` as Apple does and let Xcode's autocomplete confirm the other cases; tell the user which names are unverified. If a WebFetch of the Status page is possible, do it before asserting more.

## 5. Availability and compile guards

- The hinge APIs are iOS 27.1+ and "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo"; Apple recommends "gating iOS 27.1 APIs behind availability checks" (thread 847644). A nil `hinge` is the runtime signal for a device without a hinge.
- Mac Catalyst: iOS 27.1-only APIs produce compile errors for Catalyst targets (185924957); workaround `#if !targetEnvironment(macCatalyst)`. Targeting iOS 27.1 shows no Catalyst run destination (187046347); workaround: add a Mac Catalyst 27.0 minimum deployment ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
- Third-party, unverified: `if #available(iOS 27.1, *)` alone does not compile under Xcode 27.0 because the symbols are absent at compile time; `#if canImport(SwiftUI, _version: 8.0.85)` or a custom flag was used, since `#if compiler(>=6.4)` cannot distinguish SDKs ([blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)). Header forms observed: SwiftUI `@available(anyAppleOS 27.1, *)`, UIKit `API_AVAILABLE(ios(27.1), tvos(27.1), visionos(27.1))` ([blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator)).

Composed guard (minimal):

```swift
// Composed from Apple-documented APIs; type-checked with swiftc against the iOS 27.1 simulator SDK (Xcode 27.1, 27A9275) on 2026-10-27. Not run on a device.
import SwiftUI

struct TiltEffectHost<Content: View>: View {
    @State private var tilt: Angle = .zero
    let content: Content

    var body: some View {
        if #available(iOS 27.1, *) {
            content
                .onHingeChange { _, context in
                    if let hinge = context.hinge, hinge.status == .partiallyOpen {
                        tilt = hinge.angle          // effect input only; layout uses size classes
                    } else {
                        tilt = .zero
                    }
                }
        } else {
            content
        }
    }
}
```

## 6. Motion (Core Motion) on a two-body device

From the DTS Group Lab summary (thread 847644); these names were captured from the summary, not from Core Motion reference pages, so treat the exact signatures as unverified until checked in the SDK:

- Call `startDeviceMotionUpdates(using:)` on `CMMotionManager`.
- Conform the view to `CMBodyIdentifiable` and set `deviceMotionBody`.
- Attitude is corrected for the displaying body only when the app is full screen on that display.
- "Apps don't need to know which face is up. Use size classes."

## 7. Testing the hinge in Device Hub

Apple's documented controls ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)): "To close the iPhone Duo, click the Closed button on the right of the Rotate Right button. / To partially open the iPhone Duo, click the Partially Open button in the middle of the three device pose buttons. / To fully open the iPhone Duo, click the Open button on the far right. — To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel."

Third-party, unverified: the buttons appeared labelled "Rotate Right, Closed, Book, Open" with Book = 127° and Open = 180° ([blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator)). Use Apple's names; do not hard-code those angles.

There is no `simctl` or `XCUIDevice` way to set the hinge; the forum request ([thread 847883](https://developer.apple.com/forums/thread/847883)) has no Apple reply. Community tools exist and are unsupported (duo-test lists them). "Interactions that look fine in the simulator may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution" (thread 847644), so an angle-driven effect needs a device check.

## 8. Gaps

- Resolved 2026-10-27 from the iOS 27.1 SDK (27A9275): `DeviceHinge.Status` has `.closed`, `.partiallyOpen`, `.fullyOpen`; `UIHinge.Status` adds `.unknown`.
- Update rate and precision (system policy; unspecified).
- Angle ranges for tent / laptop / book (none published).
- Whether `angle` on a flat device is exactly 180° / π (third-party only).
- Exact Core Motion signatures for `CMBodyIdentifiable` and `deviceMotionBody`.
- Whether `isEnabled = false` pauses delivery (third-party only).

## 9. Sources

| Source | URL |
|---|---|
| Tech Talk 111464, Leverage multiple displays and scenes on iPhone Duo | https://developer.apple.com/videos/play/tech-talks/111464/ |
| DTS: A Summary of the iPhone Duo Group Lab (thread 847644) | https://developer.apple.com/forums/thread/847644 |
| onHingeChange(isEnabled:_:) | https://developer.apple.com/documentation/swiftui/view/onhingechange(isenabled:_:) |
| DeviceHinge | https://developer.apple.com/documentation/swiftui/devicehinge |
| UIHingeInteraction | https://developer.apple.com/documentation/uikit/uihingeinteraction |
| UIHinge | https://developer.apple.com/documentation/uikit/uihinge |
| Xcode 27.1 Release Notes | https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes |
| Interacting with your app in Device Hub | https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub |
| Forum thread 847883 (simulator fold automation request, no Apple reply) | https://developer.apple.com/forums/thread/847883 |
| iPhone-Duo-by-Examples (third-party) | https://github.com/artemnovichkov/iPhone-Duo-by-Examples |
| ecorpit (third-party) | https://ecorpit.com/iphone-duo-sdk-new-apis-xcode-27-1-developer-guide-2026/ |
| blakecrosley.com, simulator (third-party) | https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator |
| blakecrosley.com, worked example (third-party) | https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo |
