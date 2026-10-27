Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Server-driven UI, images, video and networking for iPhone Duo

Apple has published nothing about server-driven UI, remote config, image CDNs, asset catalogs, APNs or networking for iPhone Duo. Every recommendation in this file is labelled (inferred) unless an Apple statement is quoted next to it. Apple's statements are the anchors; the inferences are how the report proposes to honour them from a server.

Contents
1. Apple's two-layout model, as a server contract
2. Layout hints: what the client should declare and what the server may send
3. Toolbar and action metadata
4. Density: the inner display is not an iPad
5. Image and CDN sizing
6. Full-bleed media, focal points, video
7. Asset catalogs and app thinning
8. Networking and state across folds
9. Split View's two instances: backend checklist
10. Biometrics
11. Gaps

## 1. Apple's two-layout model

- "Supporting the device's various poses doesn't mean designing a custom layout for each one: instead, use size classes so your app adapts naturally as it changes size. A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose. Don't reinvent your app when it resizes; allow the existing layout to expand based on the available space instead" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Size classes (Tech Talk 111461, "Prepare your app for iPhone Duo"): outer portrait compact/regular; outer landscape compact/compact; inner display regular/regular in either rotation.
- "Don't tie functionality to a pose" (Tech Talk 111466, "Design for iPhone Duo"); "Don't change your app's functionality based on the space it occupies" ([HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout)).
- Overriding `horizontalSizeClass` "would likely interfere with system updates" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "There's no single pose API. Infer pose from hinge status, angle, orientation, and size class together" (same thread). There is therefore no pose value a client could send and no pose value a server should expect.

Server contract (inferred): the server knows two layouts, compact and regular, plus a width bucket. It never knows "Duo", "folded" or "pose".

## 2. Layout hints (inferred)

What the client declares per request or per session refresh:

| Field | Source on the client | Why |
|---|---|---|
| `h_size_class`, `v_size_class` | `@Environment(\.horizontalSizeClass)` / `traitCollection.horizontalSizeClass` and vertical | Apple's sanctioned layout signal |
| `scene_width_pt` (or a bucket) | `onGeometryChange` / `windowScene.effectiveGeometry.coordinateSpace.bounds` | Lets the server pick density without a device enum |
| `display_scale` | `@Environment(\.displayScale)` / `traitCollection.displayScale` | Image variant selection; never `UIScreen.main.scale` ([Three steps](https://developer.apple.com/iphone-duo/prepare/)) |

What the server may send: hints, not commands. Column count, density tier, hero aspect preference. The client must still be able to re-flow locally, because the same session flips compact and regular many times a minute and Apple says the fold is a trait change, not a reload moment.

Width buckets you can name without lying: the only point figures are third-party simulator readings (outer 466 pt wide; inner 669 pt portrait, 951 pt landscape; roughly half of each in Split View, derived, since Apple says Split View is "a 50/50 layout started from the home gesture" but publishes no point values). Bucket on ranges, not on these exact numbers.

Caching: keep both the compact and the regular variant of each server-driven screen on the client so a fold is not a network round-trip (inferred). This also matches "Avoid extreme layout changes as people fold the device. Move only what's necessary" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Kill switch: a remote flag keyed on machine identifier `iPhone19,4` (third-party value) plus iOS 27.1 or later is reasonable for incident response. Using it to select layout contradicts Apple's guidance above (inferred).

## 3. Toolbar and action metadata

Apple's item rules, verbatim ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):

> The system uses an icon for an item it presents vertically. / The system uses an icon or a title for an item it presents horizontally, preferring an icon. / The system uses an icon and title for an item in an overflow menu. / If your item has a title and doesn't have an icon, the system doesn't present it vertically. / If your item uses a custom view rather than a title or icon, the system doesn't present it vertically.

Consequence for server-supplied actions (inferred): every action object must carry an SF Symbol name and a title. Title-only actions cannot enter the vertical bar and are demoted to overflow. Also "Even if your content is an image, it's still important to provide a title" (Tech Talk 111462, "Raise the bar with iPhone Duo"), so never send symbol-only actions either. If the server also ranks actions, map rank to `visibilityPriority` on the client (`.high`, `.low`) rather than inventing a server-side overflow; the HIG says "If your app has its own overflow menu, move those actions into the system menu". See duo-bars for the client API.

## 4. Density: the inner display is not an iPad

The inner display is regular/regular, and Apple says "On the inner display, your app should look like a natural extension of its iPad layout" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). But its size is roughly 669×951 pt (third-party simulator measurement), which is smaller than an iPad mini at 744×1133 pt (research-note figure, not from an Apple Duo page). Three-column iPad server layouts are therefore likely too dense (inferred). The HIG prefers "an even number of columns so content divides cleanly" around the fold, and Apple's Calculator example shows the outer display using "five columns of four items" versus iPhone 16's "four columns of five items" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Default server hints to two columns in regular width unless the client's width bucket is clearly larger.

## 5. Image and CDN sizing

Apple's figures are pixels only: inner "1878‑by‑2670-pixel resolution at 430 ppi", outer "1398‑by‑2034-pixel resolution at 460 ppi" ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)); App Store Connect screenshot sizes are 1398×2034 (outer) and 2007×2853 (inner) ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). The point sizes come from the Xcode 27.1 simulator display profile (third-party, unverified): outer 466×678 pt @3x; inner 669×951 pt @3x rendering a 2007×2853 logical buffer that the 1878×2670 panel downsamples. The arithmetic matches (669×3 = 2007, 951×3 = 2853), which is the report's inference, not Apple's statement.

CDN variants (inferred): serve @3x assets sized to the scene width in points times three, keyed on a width parameter, not a device enum.

| Scene | Width (pt, third-party) | @3x pixel width | Status |
|---|---|---|---|
| Outer display portrait | 466 | 1398 | matches Apple's outer pixel width |
| Inner display portrait | 669 | 2007 | matches ASC inner screenshot width |
| Inner display landscape, full width | 951 | 2853 | matches ASC inner landscape width |
| Split View half | about 475 or 334 | about 1425 or 1002 | derived from the halves; Apple publishes no Split View sizes |

Request the variant from the scene width you already log (section 2), and re-request when `windowScene(_:didUpdateEffectiveGeometry:)` reports a new `coordinateSpace.bounds.size` with `!geometry.isInteractivelyResizing`, which is the asset-swap hook TN3192 shows ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).

## 6. Full-bleed media, focal points, video

- Apple: "Check full-bleed media (`.scaleAspectFill`, `.aspectRatio(contentMode: .fill)`) for lost content, and choose fill or fit based on size class or aspect ratio, or set a focal point" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). Hero media set to fill "can lose important content on wider displays" (same page). The scanner flags this as DUO-013.
- Aspect ratio (inferred from Apple's pixel figures): 2670/1878 and 2853/2007 are both about 1.42; 2034/1398 is about 1.45; a current tall iPhone is about 2.17. Crops tuned for tall phones lose content on Duo, so ship focal-point metadata from the CMS and crop client-side per scene (inferred). A third-party blog recommends server-side crops per display instead of one oversized image (Appwrite, opinion).
- Hero art under the vertical bar: `backgroundExtensionEffect()` in SwiftUI, `UIBackgroundExtensionView` in UIKit ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- Video: AVKit "scales and resizes the video" automatically and playback position is preserved across folds; PiP "pins to top and the app resizes vertically in real time"; "Audio/video playback is associated with the most recent app that began the playback session" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644); Tech Talk 111466). For games the HIG says "Prefer changing the aspect ratio over letterboxing or pillarboxing ... if you can't avoid letterboxing or pillarboxing, add artwork to the padding area" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). A 16:9 frame in landscape on the inner display "is 951 by 535 points, leaving 134 points (about a fifth of the height) unused" (third-party arithmetic, blakecrosley.com). Fixed 16:9 containers are DUO-014.

## 7. Asset catalogs and app thinning

Both displays are @3x (third-party), so existing `@3x` slices already cover Duo. No asset-catalog, image-set or app-thinning change appears in the Xcode 27.1 release notes ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)), and no Apple page documents one. Treat "no change" as inference from absence, not confirmation.

## 8. Networking and state across folds

Apple's statements ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)):

- "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running."
- "Text input, scroll position, and video playback are generally preserved automatically. Apps usually don't need `scrollPosition(id:)` for LazyVGrid column changes."
- "An active editing session survives the hinge transition without getting a new scene"; keep the edited field visible with `keyboardWillShowNotification`, `keyboardWillHideNotification`, `keyboardWillChangeFrameNotification`.
- "For state that must survive a true scene disconnect/reconnect, implement `stateRestorationActivity(for:)` and save an `NSUserActivity`."
- The mid-checkout answer covered input persistence but "doesn't address how to avoid duplicate network requests".

Inferences from those statements (Apple is silent on networking):

- `URLSession` tasks, `URLSessionWebSocketTask`, uploads and `AVPlayer` continue through a fold because the process and scene persist.
- The real risk is self-inflicted teardown. Grep for request cancellation, view-model recreation or player teardown inside `viewWillTransition(to:with:)`, trait-change handlers, `UIDevice.current.orientation`-driven handlers, or SwiftUI views whose identity is keyed on a size class. Apple's Three steps already says to replace orientation-driven code with size classes; the scanner's DUO-005 marks those sites.
- Background execution: Apple says the app "adapts in place rather than backgrounding", which implies `BGTaskScheduler`, background `URLSession` and push handling are unchanged by a fold. Apple did not address this directly; do not promise it.
- A fold is not a reason to re-fetch. Render from the data you already hold; the only backend-driven re-request should be the image variant swap in section 5.

## 9. Split View's two instances: backend checklist

Apple: "iPhone Duo is the first iPhone to support multiple instances of your app's UI ... On the outer display of iPhone Duo, new windows cannot be created. That behavior is reserved for the inner display"; "creation availability is dynamic, so apps must handle errors when requesting scenes"; use `UIWindowSceneActivationAction`, "which hides automatically when new windows aren't available" (Tech Talk 111464, "Leverage multiple displays and scenes on iPhone Duo"). "`UserDefaults` and `@AppStorage` are app-wide, not per-window" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). When the device closes during Split View, "the most recently active scene window would be remain active when the device closes—the secondary window scene would transition to an inactive state, then backgrounded" ([Apple Developer Forums 847838](https://developer.apple.com/forums/thread/847838)).

Checklist (inferred, the same discipline as iPad multi-window):

1. Singletons that hold network state (auth token refresh, WebSocket manager, upload queue, Core Data stack) must be process-scoped and safe for two scenes to use concurrently. Do not refresh a token twice because two scenes both noticed it expired.
2. Write endpoints should accept idempotency keys; one user can submit the same action from two instances. Apple has not addressed duplicate requests.
3. Expect `requestSceneSessionActivation` to fail on the outer display and fall back to in-scene navigation.
4. A visible scene can be `inactive` in Split View, so pause media and sockets on background, not on resign-active (third-party, unverified observation).
5. Multi-scene support still needs the standard `UIApplicationSupportsMultipleScenes` scene-manifest entry as on iPad; no Duo-specific key appears in any Apple source (inferred).
6. Privacy blurs on resign-active must be per-scene, and content shown through `CameraCaptureAccessory` faces a third party, so keep account data and chat out of it (inferred).
7. If two panes show the same record (list and detail across two instances), an edit in one should reach the other through your normal sync path rather than a manual refresh (third-party opinion, Appwrite).

## 10. Biometrics

Duo has "Touch ID in the side button" and no Face ID ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)). Branch copy, symbols and onboarding on `LAContext.biometryType`. Any server-side risk rule, enrollment flag or marketing string that assumes Face ID on a current iPhone must handle Touch ID devices (inferred).

## 11. Gaps

- Apple has published nothing on server-driven UI, remote config, feature flags, image CDNs, APNs payloads, Live Activity update budgets, or networking across folds.
- No Apple point dimensions for either display; no Split View point sizes.
- No Apple statement on asset catalogs or app thinning for Duo.
- Whether a fold ever triggers `sceneWillResignActive` or background execution is not stated except for the multi-window case above.
- How to avoid duplicate network requests across a fold or across two instances was explicitly not addressed by Apple.
