Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Device detection and analytics on iPhone Duo

Contents
1. What Apple says about identifying the device
2. Signal table: what each identifier can and cannot tell you
3. The `UIScreen.main` problem for analytics SDKs
4. Observability properties to log yourself (report's recommendation)
5. Composed SwiftUI modifier
6. Composed UIKit scene-delegate hook
7. Vendor and App Store Connect status
8. Feature flags and kill switches
9. Gaps Apple has not closed

## 1. What Apple says about identifying the device

- "iPhone Duo is not a separate device class ... iPhone Duo does not support Stage Manager and does not have its own `UIUserInterfaceIdiom`"; "apps can't require iPhone Duo-specific capabilities"; "Apps don't need iPad support first" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "you are not required to support iPad to support the iPhone Duo as its device idiom is still `.phone`. In iOS 27, iPhone apps on both the iPhone Duo and iPhone Mirroring (in macOS 27) will see iPhone apps have regular size classes when resized" (Apple Frameworks Engineer, [Apple Developer Forums 847945](https://developer.apple.com/forums/thread/847945)).
- "There's no API for web pages to detect iPhone Duo specifically. Use responsive design instead" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "Design from size, traits, and reserved regions, not hardware names or screen dimensions" (Apple UIKit Q&A as summarized by a third party, [Gubarenko Q4](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- From the grep list on [Three steps](https://developer.apple.com/iphone-duo/prepare/): "Don't choose a layout by idiom"; "Don't treat 'regular width' as 'iPad.'" ("an iPhone app can have any combination of size classes"); "Remove checks for specific device sizes".
- The size-class matrix Apple gives (Tech Talk 111461, "Prepare your app for iPhone Duo"): outer display portrait = compact width, regular height; outer display landscape = compact, compact; inner display, either rotation = regular, regular.

The consequence for a backend: the same device is a "compact" client and a "regular" client within one session, so any per-device or per-user layout flag is wrong for part of the session (inferred).

## 2. Signal table

| Signal | What it tells you | Status |
|---|---|---|
| `UIDevice.current.userInterfaceIdiom` | Always `.phone` on Duo; cannot distinguish Duo | Apple ([847945](https://developer.apple.com/forums/thread/847945)) |
| Machine identifier (`utsname.machine`, `sysctl hw.machine`) | `iPhone19,4` | Third-party, unverified: Xcode 27.1 simulator profile (product class V68, model A3447), a Geekbench 7 entry uploaded Oct 14 2026, EveryMac's identifier table. Apple publishes no identifier table |
| Model numbers | A3447 (US/PR), A3719, A3720, A3721; all eSIM-only | Third-party, unverified (TechWalls, which cites no sources) |
| Identifier libraries (iModels, iDevice, ios-device-list, ios-devices) | None had `iPhone19,4` at research time | Third-party, unverified |
| Safari / WKWebView User-Agent | Does not disclose the model; "version numbers don't allow us differentiate between iPhone models" | Third-party (DeviceAtlas, general iOS statement). No source captured an actual Duo UA string |
| `UIScreen.main.bounds` / `.scale` | "ambiguous on two-display devices and will be deprecated in a future release" | Apple (Tech Talk 111461) |
| `horizontalSizeClass` / `verticalSizeClass` | Which layout the app is in right now | Apple; this is the sanctioned signal |
| Scene size in points | Current scene geometry; `coordinateSpace.bounds` of `effectiveGeometry` | Apple ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)) |
| `view.window?.windowScene?.screen` | The display the scene is actually on | Apple (Tech Talk 111461: "Don't store a `UIScreen`") |
| Hinge status via `onHingeChange` / `UIHingeInteraction` | closed, partially open, fully open as high-level status, plus angle | Apple (Tech Talk 111464); only `.partiallyOpen` confirmed as a case name in Apple code |
| App Store Connect analytics Device dimension | iPhone, iPad, Apple TV, iPod, Desktop, Apple Vision; no Duo value | Apple ([ASC analytics filters and dimensions](https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/)) |

Use the first three rows only for counting and incident response, never for layout. The scanner's DUO-015 rule flags `utsname`, `hw.machine`, `UIDevice.current.model`, `localizedModel`, `name`, and literal `"iPhoneNN,N"` strings for exactly this reason.

## 3. The `UIScreen.main` problem for analytics SDKs

Apple's statement is that `UIScreen.main` is ambiguous on two-display devices and will be deprecated (Tech Talk 111461). A developer measured `UIScreen.main.bounds` returning 466×678 while the app ran on the inner display, where the window scene's screen reported 951×669 in book pose (third-party, unverified, blakecrosley.com). The report's inference: any analytics or crash SDK that derives "screen resolution" from `UIScreen.main.bounds` or `UIScreen.main.scale` will mis-report on Duo until the vendor updates. Ask your vendor which API they read; replace your own uses with `traitCollection.displayScale` / `@Environment(\.displayScale)` and `view.window?.windowScene?.screen` ([Three steps](https://developer.apple.com/iphone-duo/prepare/); Tech Talk 111461).

## 4. Observability properties to log yourself

This is the report's recommendation, not an Apple instruction. Apple's crash reports, MetricKit and App Store Connect will not contain pose, so attach these to events and crash breadcrumbs:

| Property | Read from | Notes |
|---|---|---|
| `machine` | `utsname.machine` or `sysctl hw.machine` | Expect `iPhone19,4` (third-party value); use for counts and kill switches only |
| `h_size_class`, `v_size_class` | `@Environment(\.horizontalSizeClass)` / `.verticalSizeClass`; UIKit `traitCollection.horizontalSizeClass` / `.verticalSizeClass` | Re-log on change; use `registerForTraitChanges(_:target:action:)` or `registerForTraitChanges(_:handler:)` in UIKit (TN3192) |
| `scene_w_pt`, `scene_h_pt` | SwiftUI `onGeometryChange(for:of:action:)` on the root view; UIKit `windowScene.effectiveGeometry.coordinateSpace.bounds` in `windowScene(_:didUpdateEffectiveGeometry:)` | Skip samples while `UIWindowScene.Geometry.isInteractivelyResizing` is true (TN3192) |
| `display_scale` | `@Environment(\.displayScale)` / `traitCollection.displayScale` | Both displays are reported as scale 3 by the simulator profile (third-party) |
| `hinge_status` | `onHingeChange { _, ctx in ctx.hinge?.status }`; UIKit `UIHingeInteraction` update's `hinge?.status` | `hinge` is nil on devices without a hinge. Log `String(describing:)`; do not switch over unverified cases |
| `split_view` | scene bounds smaller than `windowScene.screen` bounds | Inferred heuristic; Apple publishes no Split View point sizes |
| `screen_w_pt`, `screen_h_pt` | `view.window?.windowScene?.screen.bounds` | Identifies outer vs inner display indirectly; Apple publishes no point sizes, so compare, do not hard-code |

Do not log the hinge angle for product logic or thresholds: "Update rate and precision are system policy, so don't depend on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). If you transmit hinge data at all, treat it as device data in your privacy label (inferred).

## 5. Composed SwiftUI modifier

```swift
// Composed from Apple-documented APIs; type-checked with swiftc against the iOS 27.1 simulator SDK (Xcode 27.1, 27A9275) on 2026-10-27. Not run on a device.
// Assumes a deployment target of iOS 27.1; otherwise wrap the hinge modifier in
// `if #available(iOS 27.1, *)`, as the Group Lab recommends for all 27.1 APIs.
import SwiftUI

struct PoseTelemetry: ViewModifier {
    @Environment(\.horizontalSizeClass) private var hSize
    @Environment(\.verticalSizeClass) private var vSize
    @Environment(\.displayScale) private var displayScale
    @State private var hinge: DeviceHinge? = nil

    let record: ([String: String]) -> Void   // your analytics SDK's "set properties" call

    func body(content: Content) -> some View {
        content
            .onGeometryChange(for: CGSize.self) { proxy in
                proxy.size
            } action: { size in
                record([
                    "scene_w_pt": "\(Int(size.width))",
                    "scene_h_pt": "\(Int(size.height))",
                    "h_size_class": String(describing: hSize),
                    "v_size_class": String(describing: vSize),
                    "display_scale": "\(displayScale)",
                    "hinge_status": hinge.map { String(describing: $0.status) } ?? "none",
                ])
            }
            .onHingeChange { _, newContext in
                hinge = newContext.hinge
            }
    }
}
```

The `onHingeChange` call shape (`{ _, newContext in hinge = newContext.hinge }`) is Apple's own example from the `DeviceHinge` page ([DeviceHinge](https://developer.apple.com/documentation/swiftui/devicehinge)). `onGeometryChange` is the proxy source Apple names in Three steps and Tech Talk 111463.

## 6. Composed UIKit scene-delegate hook

```swift
// Composed from Apple-documented APIs; type-checked with swiftc against the iOS 27.1 simulator SDK (Xcode 27.1, 27A9275) on 2026-10-27. Not run on a device.
import UIKit

extension SceneDelegate {
    func windowScene(_ windowScene: UIWindowScene,
                     didUpdateEffectiveGeometry previousGeometry: UIWindowScene.Geometry) {
        let geometry = windowScene.effectiveGeometry
        guard !geometry.isInteractivelyResizing else { return }   // TN3192: wait for the resize to finish
        let scene = geometry.coordinateSpace.bounds.size
        let screen = windowScene.screen.bounds.size             // not UIScreen.main
        record([
            "scene_w_pt": "\(Int(scene.width))",
            "scene_h_pt": "\(Int(scene.height))",
            "screen_w_pt": "\(Int(screen.width))",
            "screen_h_pt": "\(Int(screen.height))",
            "split_view": scene.width < screen.width || scene.height < screen.height ? "1" : "0",
        ])
    }
}
```

Log size classes and display scale from a view controller instead, with `registerForTraitChanges(_:handler:)` reading `traitCollection.horizontalSizeClass`, `traitCollection.verticalSizeClass` and `traitCollection.displayScale` (TN3192 names the registration API; Three steps names `displayScale`). `windowScene(_:didUpdateEffectiveGeometry:)`, `effectiveGeometry.coordinateSpace.bounds` and `isInteractivelyResizing` are the APIs TN3192 documents for discrete resizes ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)). The `split_view` comparison is the report's inferred heuristic. For hinge status in UIKit, add a `UIHingeInteraction(updateHandler:)` to a view and read `update.hinge?.status`; Apple's example is on the [UIHingeInteraction](https://developer.apple.com/documentation/uikit/uihingeinteraction) page, and `UIHinge.angle` is in radians ([UIHinge](https://developer.apple.com/documentation/uikit/uihinge)).

## 7. Vendor and App Store Connect status

- App Store Connect analytics: Device dimension values are iPhone, iPad, Apple TV, iPod, Desktop, Apple Vision. There is no Duo breakdown and Apple has made no statement about adding one ([ASC analytics filters and dimensions](https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/)). Derive Duo install share from your own `iPhone19,4` counts (inferred).
- MetricKit: iOS 27 adds memory-exception diagnostics and a termination-category field on crash diagnostics; nothing display- or pose-specific ([WWDC26 session 222](https://developer.apple.com/videos/play/wwdc2026/222/)). `MXCrashDiagnostic` is "not the same as a crash report" and TestFlight/App Store crash reports require user opt-in ([Apple Developer Forums 775774](https://developer.apple.com/forums/thread/775774)).
- Vendors: no Duo-specific release note was found for Firebase, Amplitude, Mixpanel, Crashlytics, Sentry, Datadog or Embrace at research time (third-party, unverified; absence of evidence).

## 8. Feature flags and kill switches

A remote kill switch keyed on machine identifier `iPhone19,4` plus iOS 27.1 or later is reasonable for incident response, for example to disable a feature that misbehaves only on Duo while you ship a fix (inferred). Gating layout on that flag contradicts Apple's guidance in section 1 and will also be wrong whenever the user is on the outer display, which is a compact-width layout like any other iPhone (Tech Talk 111461).

## 9. Gaps

- No official Apple page lists `iPhone19,4`; the mapping rests on the simulator profile, Geekbench and identifier databases.
- No source captured an actual iPhone Duo Safari User-Agent string.
- No analytics or crash vendor had published Duo changes.
- RAM (12 GB) comes from a single Geekbench entry and Apple does not publish it; a ~6 GB per-app memory cap on 12 GB iPhones is a forum anecdote ([Apple Developer Forums 834805](https://developer.apple.com/forums/thread/834805)). Do not size Split View caches on either figure.
- Apple has not said whether a fold ever triggers `sceneWillResignActive` or background execution; the only statement is the multi-window answer in [Apple Developer Forums 847838](https://developer.apple.com/forums/thread/847838).
