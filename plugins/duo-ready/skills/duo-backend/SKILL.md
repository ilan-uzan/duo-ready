---
name: duo-backend
description: >-
  Everything outside the view layer for iPhone Duo (iOS 27.1): device
  identification and its limits, which analytics properties to log yourself,
  networking and state across folds and Split View, server-driven UI hints,
  image/CDN sizing, WKWebView and web content, widgets and Live Activities,
  biometrics and privacy. Use it when a backend, data, web or platform engineer
  asks things like "can the server tell if the user is on the folding iPhone",
  "our analytics shows a 466x678 screen resolution", "do I need iPhone19,4 in
  the device table", "will the upload / WebSocket / video survive the phone
  opening", "which image size should the CDN serve on the new iPhone", "the BFF
  wants to send the tablet layout to the big screen", "our web view sits under
  the crease", "can I use CSS viewport segments in the app", "the Live Activity
  is clipped in the side bar", or "our Face ID copy shows on a phone that only
  has Touch ID". Also use it whenever another duo-ready skill reaches a
  question about servers, analytics SDKs, CDNs, web content, or extensions.
---

# duo-backend

## What Apple actually says

- There is no way to identify iPhone Duo as a device class: "iPhone Duo is not a separate device class ... does not have its own `UIUserInterfaceIdiom`", "apps can't require iPhone Duo-specific capabilities", and "There's no API for web pages to detect iPhone Duo specifically. Use responsive design instead" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). The idiom stays `.phone` ([Apple Developer Forums 847945](https://developer.apple.com/forums/thread/847945)).
- A fold is not a lifecycle event: "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Apple's mid-checkout answer "doesn't address how to avoid duplicate network requests" (same thread), so networking advice below is inferred.
- `UIScreen.main` is "ambiguous on two-display devices and will be deprecated in a future release" (Tech Talk 111461, "Prepare your app for iPhone Duo"). Any SDK that reads it for "screen resolution" is reading the wrong display some of the time.
- Web: "Safari/WebKit exposes Viewport Segments and Device Posture APIs. Both are opt-in experimental features in iOS 27.1, enabled at Settings > Apps > Safari > Advanced > Feature Flags" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)); they are "not available in WKWebView" and "CSS insets don't account for the fold" (Apple UIKit Q&A as summarized by a third party, [Gubarenko Q41](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- Apple has published nothing on server-driven UI, image CDNs, asset catalogs, APNs, or background execution for Duo. Everything in those areas below is marked (inferred). Do not upgrade it.

## Workflow

### Step 0: look at the real code first

Ask for, or open, the code that actually makes the decision in question: the analytics bootstrap, the device-info header builder, the BFF request DTO, the image URL builder, the WKWebView container, the widget bundle. Generic advice about "foldables" is worse than useless here because Apple's answer is usually "stop detecting the device".

When a project path is available, run the scanner and read the DUO-001 (`UIScreen.main`), DUO-015 (model string sniffed for layout), DUO-021 (WKWebView cannot see the fold) and DUO-013/014 (fill media, fixed 16:9) findings before advising:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

### Step 1: device identification. Say what cannot be done, then what can

Decide which of two questions the user is really asking.

1. "Which layout should I serve or render?" The answer is never the device. Apple: "Don't choose a layout by idiom", "Don't treat 'regular width' as 'iPad'", "Remove checks for specific device sizes" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). Point them at size classes and scene geometry (duo-layout) and at Step 3 below for server hints.
2. "How do I count or segment Duo users?" This is legitimate observability. Then:
   - The machine identifier is `iPhone19,4` (third-party, unverified: simulator profile, a Geekbench entry, EveryMac; Apple publishes no identifier table). Regional model numbers A3447 (US/PR), A3719, A3720, A3721 are third-party too. Add `iPhone19,4` to your own server-side identifier map now, because none of the common mapping libraries (iModels, iDevice, ios-device-list) had it at research time (third-party, unverified).
   - Safari and WKWebView user agents do not disclose the model (third-party, DeviceAtlas), and Apple says there is no web detection API. A backend cannot infer Duo from a request unless the native app sends it.
   - Prefer sending capability signals, not identity: `horizontalSizeClass`/`verticalSizeClass`, scene size in points, `displayScale`. The same device alternates between compact (outer display) and regular (inner display) within one session, so a per-device flag is wrong half the time (inferred).

Never recommend gating layout on `iPhone19,4`, `UIDevice.current.model`, `utsname`, or `hw.machine`. The scanner flags these as DUO-015. A kill switch keyed on model identifier plus iOS 27.1 is acceptable for incident response only (inferred).

Read `references/device-detection-and-analytics.md` for the full table of what each signal can and cannot tell you.

### Step 2: analytics. Log your own pose properties

App Store Connect analytics exposes only platform-level Device values (iPhone, iPad, Apple TV, iPod, Desktop, Apple Vision) with no Duo breakdown ([ASC App analytics filters and dimensions](https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/)). MetricKit's iOS 27 additions (memory-exception diagnostics, termination category) are not pose-specific ([WWDC26 session 222](https://developer.apple.com/videos/play/wwdc2026/222/)). No analytics or crash vendor had published Duo changes at research time (third-party, unverified). So the report's recommendation is to attach these properties to events and crash breadcrumbs yourself:

| Property | Source | Status |
|---|---|---|
| Machine identifier | `utsname.machine` / `sysctl hw.machine`, expect `iPhone19,4` | identifier value third-party |
| Size classes | `@Environment(\.horizontalSizeClass)` / `traitCollection.horizontalSizeClass`, and vertical | Apple API |
| Scene size in points | `GeometryReader` / `onGeometryChange`; UIKit `windowScene.effectiveGeometry.coordinateSpace.bounds` | Apple API (TN3192) |
| Display scale | `@Environment(\.displayScale)` / `traitCollection.displayScale`, never `UIScreen.main.scale` | Apple (Three steps) |
| Hinge status | `onHingeChange` → `DeviceHingeContext.hinge?.status`; UIKit `UIHingeInteraction` → `UIHinge.status` | Apple API, iOS 27.1+ |
| Split View | scene bounds smaller than `windowScene.screen` bounds | report's recommendation (inferred) |
| Which display | `view.window?.windowScene?.screen` bounds, not `UIScreen.main` | Apple (Tech Talk 111461) |

Rules for the hinge property: log `String(describing:)` of the status rather than mapping cases, because the case set differs between frameworks (the iOS 27.1 SDK declares `.closed`, `.partiallyOpen`, `.fullyOpen` in SwiftUI and adds `.unknown` in UIKit) and may grow. Never log or threshold the raw angle for product logic: "Update rate and precision are system policy, so don't depend on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Gate the hinge call behind availability; the Group Lab recommends "gating iOS 27.1 APIs behind availability checks" (same thread).

Verify with the vendor whether their SDK reads `UIScreen.main.bounds`; a developer measured it returning 466×678 while the app ran on the inner display (third-party, unverified, blakecrosley.com).

The reference file has a composed SwiftUI modifier and a UIKit scene-delegate hook for this.

### Step 3: networking and state across folds and Split View

Start from Apple's statements, then separate the two cases.

Fold or display switch, single scene: nothing is torn down. "Text input, scroll position, and video playback are generally preserved automatically"; "An active editing session survives the hinge transition without getting a new scene"; the app "adapts in place rather than backgrounding" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Therefore (inferred from that statement, Apple is silent on networking) `URLSession` tasks, `URLSessionWebSocketTask`, uploads and `AVPlayer` continue. The real risk is self-inflicted: look for code that cancels requests, recreates view models, or tears down players in `viewWillTransition(to:with:)`, on `UIDevice.orientation` notifications, or in SwiftUI views whose identity is keyed on a size class. Remove the teardown; let the same instance relayout.

Split View, two instances: "iPhone Duo is the first iPhone to support multiple instances of your app's UI ... On the outer display of iPhone Duo, new windows cannot be created ... creation availability is dynamic, so apps must handle errors when requesting scenes" (Tech Talk 111464, "Leverage multiple displays and scenes on iPhone Duo"). Audit, as you would for iPad multi-window (inferred):
- Process-scoped singletons (auth refresh, socket manager, Core Data stack, upload queue) must tolerate two scenes using them at once. Per-scene state belongs in the scene; "`UserDefaults` and `@AppStorage` are app-wide, not per-window" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Write endpoints should accept idempotency keys, because one user can trigger the same action from two instances. Apple did not address duplicate requests; this is the report's inference.
- Treat scene-activation failures as expected on the outer display and fall back to in-scene navigation; use `UIWindowSceneActivationAction`, "which hides automatically when new windows aren't available" (Tech Talk 111464).
- When the device closes during Split View, "the most recently active scene window would be remain active ... the secondary window scene would transition to an inactive state, then backgrounded" ([Apple Developer Forums 847838](https://developer.apple.com/forums/thread/847838)). A visible app can be `inactive` in Split View, so pause media on background, not on resign-active (third-party, unverified).
- For true disconnects "implement `stateRestorationActivity(for:)` and save an `NSUserActivity`" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Apple gave no Duo-specific extension to this.

Say plainly that Apple has not stated whether a fold ever triggers `sceneWillResignActive` or background execution; the report lists this as an open gap. Do not promise `BGTaskScheduler` behaviour; the report only infers it is unchanged.

### Step 4: server-driven UI (inferred throughout)

Apple's design model is two layouts, not two devices: "A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Apple says nothing about server-driven UI, so hold every recommendation here to that anchor and label it inferred:

1. Key layout hints (column count, density, hero aspect) on the client's declared size class and a scene-width bucket, never on device model. The client must still re-flow locally; the same session can flip compact and regular many times a minute.
2. Cache both the compact and the regular variant of a server-driven screen on the client so a fold is not a network round-trip.
3. Server-supplied toolbar actions must carry an SF Symbol name plus a title. Apple's bar rules: "If your item has a title and doesn't have an icon, the system doesn't present it vertically", and overflow items use "an icon and title" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). Title-only server actions will be demoted to overflow on the outer display.
4. Do not reuse three-column iPad server layouts unchanged. The inner display is roughly 669×951 pt (third-party simulator measurement; Apple publishes pixels only), smaller than an iPad mini's 744×1133 pt (research-note figure), and the HIG prefers "an even number of columns so content divides cleanly".
5. Never ship a server flag that changes functionality by pose: "Don't tie functionality to a pose" (Tech Talk 111466, "Design for iPhone Duo").

Read `references/server-driven-ui-and-media.md` for the hint schema sketch and the width buckets.

### Step 5: images, video, CDN (inferred unless marked Apple)

- Apple gives pixel specs only: inner 1878×2670 px at 430 ppi, outer 1398×2034 px at 460 ppi ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)); App Store Connect wants 1398×2034 and 2007×2853 ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). Point sizes 466×678 and 669×951 @3x are third-party simulator readings.
- Serve @3x variants keyed on scene width in points (466, 669, 951, and roughly half for Split View), through width-based CDN parameters rather than a device enum (inferred). Both displays are @3x, so existing `@3x` slices cover Duo; no asset-catalog or app-thinning change appears in the Xcode 27.1 release notes (inferred from absence).
- Apple's own media rule: "Check full-bleed media (`.scaleAspectFill`, `.aspectRatio(contentMode: .fill)`) for lost content, and choose fill or fit based on size class or aspect ratio, or set a focal point" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). Ship focal-point metadata from the CMS; the displays' roughly 1.42 aspect ratio (computed from Apple's pixel figures) loses tall-phone crops (inferred).
- Video: AVKit resizes automatically and playback position is preserved across folds ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). The HIG prefers changing aspect ratio over letterboxing for games and says to "add artwork to the padding area" when unavoidable. A 16:9 frame on the inner display in landscape leaves about a fifth of the height unused (third-party arithmetic, blakecrosley.com).
- Swap resolution-dependent assets in `windowScene(_:didUpdateEffectiveGeometry:)` when `!geometry.isInteractivelyResizing`, which is the hook TN3192 shows ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).

### Step 6: web content and WKWebView

Decide first whether the content runs in Safari or inside your app.

Safari: Viewport Segments and Device Posture exist but are flag-gated, so treat them as progressive enhancement and feature-detect; expect them off for nearly all users. The spec surface (MDN/Chrome, not Apple): CSS `vertical-viewport-segments` / `horizontal-viewport-segments`, `env(viewport-segment-width/height/top/left/bottom/right)`, JS `viewport.segments`, `@media (device-posture: folded | continuous)`, `navigator.devicePosture` with a `change` event. WebKit's standards positions #327 and #328 are still open (third-party).

WKWebView: the fold APIs are not available; "Query geometry in the host and pass it to the page" (Apple UIKit Q&A via Gubarenko Q41). Read `reservedRegions(kind:options:)` on the host `UIView` (or `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)` in SwiftUI) plus the host's safe-area insets and hinge status, and inject them into the page through your existing native-to-web bridge. The scanner's DUO-021 finding marks the container to fix.

Hybrid CSS hygiene (third-party, unverified, from Capacitor and web-view write-ups): `env(safe-area-inset-*)` is zero without `viewport-fit=cover`; apply left and right insets separately because Apple says safe areas "are often asymmetric on iPhone Duo. Handle each side independently" (Tech Talk 111461); replace UA sniffing with `min-width` or container queries; `100vh` → `100dvh`; replace cached `window.innerWidth` with `ResizeObserver` or `visualViewport`; avoid double padding when native and CSS both inset. CSS px equal points on iOS, so viewports land near 466, 669 and 951 px and the common 600–700 px breakpoints will flip during a fold (inferred).

Read `references/web-and-wkwebview.md` for the feature-detection snippet and the gap list.

### Step 7: widgets, Live Activities, StandBy

- Widget families are the standard ones: `systemSmall`, `systemMedium`, `systemLarge`, `systemExtraLargePortrait`, plus `accessoryCircular`, `accessoryRectangular`, `accessoryInline`; no new sizes ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Live Activities "must implement compactLeading, compactTrailing, minimal, expanded, and Lock Screen presentations" (same thread). The outer camera region "expands into the Dynamic Island for Live Activities" ([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)), and the side column shares its vertical space with toolbars (Tech Talk 111466).
- The HIG Live Activities page (updated October 13, 2026, "Added guidance for limited width layouts") says to fit compact and minimal presentations "inside a 28pt-diameter circle", adopt a leading view only, and read the `isDynamicIslandLimitedInWidth` environment value ([HIG: Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities)). That page never names Duo; the connection is inferred.
- Server side (inferred): ActivityKit push updates are unchanged; keep pushed content short because the compact presentations are tiny. Apple has published nothing on Live Activity budgets or concurrent counts on Duo.
- StandBy "works on either display even when it's not charging" ([Apple Newsroom](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)) and "StandBy is unavailable in the iPhone Duo Simulator runtime. (187708663)"; "Running and debugging most app extensions is unavailable in the iPhone Duo Simulator runtime. (187708767)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)). Test extensions on a regular iOS 27.1 simulator and on hardware (see duo-test).

### Step 8: biometrics and privacy

- Duo has "Touch ID in the side button" and no Face ID ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)). Branch biometric copy, symbols and onboarding on `LAContext.biometryType`; any server-side "Face ID enabled" copy or risk rule must handle Touch ID devices (inferred).
- No new permission, Info.plist key, privacy-manifest entry or Required Reason API tied to Duo was found. The camera-accessory article documents registration without any permission text ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)) and the Upcoming Requirements page lists nothing Duo-related ([Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/)). Say "none found", not "none exists".
- If you transmit hinge status for analytics, treat it as device data in your privacy label (inferred). Accessory content on the outer display faces a third party, so keep sensitive UI out of it, and make privacy blurs on resign-active per-scene because Split View runs two instances (inferred).

### Step 9: verify

- Run the scanner again; DUO-001, DUO-015 and DUO-021 should be gone or suppressed with a reason.
- In the iPhone Duo simulator (Xcode 27.1, Device Hub Closed / Partially Open / Open buttons), watch the logged properties change through a fold and confirm no request is cancelled and no socket reconnects.
- Drag the app "by the home indicator to either side of the screen" to enter Split View (Tech Talk 111461) and confirm two instances do not double-post.
- Widgets, Live Activities and StandBy cannot be exercised in the Duo simulator; use a regular iOS 27.1 simulator and hardware.

## Common mistakes

- Treating `horizontalSizeClass == .regular` as "iPad client" in a BFF and sending a three-column layout. Apple: "an iPhone app can have any combination of size classes" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Trusting the analytics SDK's screen resolution. `UIScreen.main` is ambiguous (Apple); measured as the outer size while on the inner display (third-party).
- Adding `iPhone19,4` to a layout branch. The identifier is third-party and Apple forbids device-keyed layout (DUO-015).
- Cancelling uploads or sockets in `viewWillTransition(to:with:)` or on orientation notifications. The fold is a trait change, not a teardown (Apple).
- Assuming one instance per device. Split View runs two; singletons and write endpoints must cope (Apple on instances, inferred on endpoints).
- Expecting `env(safe-area-inset-*)` or viewport segments to describe the fold inside WKWebView. Apple's Q&A says they do not; the host must pass geometry.
- Server toolbar actions without an SF Symbol. They cannot go vertical under Apple's item rules.
- Implementing only the expanded Live Activity presentation. Apple requires all of them.
- Face ID-specific copy. Duo has Touch ID only.

## When to read the references

- `references/device-detection-and-analytics.md`: what each identification signal can tell you, the full observability property table with a composed SwiftUI modifier and UIKit hook, the vendor and ASC analytics status, and the gap list.
- `references/web-and-wkwebview.md`: Safari flag status, the spec surface and feature-detection snippet, the WKWebView host-bridge pattern, hybrid CSS fixes, and what Apple has not documented.
- `references/server-driven-ui-and-media.md`: the two-layout model as a server contract, hint schema and width buckets, toolbar action metadata rules, CDN variant sizes, focal points, video aspect, networking and Split View backend checklist. Every recommendation there is labelled inferred unless Apple said it.

## Related skills

- duo-audit: run the scanner and triage DUO-001/015/021 before changing anything.
- duo-layout: size classes, scene geometry and reserved regions, which replace every device check this skill tells you to delete.
- duo-scenes: fold-as-trait-change, Split View and scene accessories in depth; read it before touching scene delegates.
- duo-bars: the icon/title rules your server-driven toolbar metadata must satisfy.
- duo-camera: camera direction and `CameraCaptureAccessory`, which is the only way to put content on the outer display.
- duo-test: the CI matrix and what the Duo simulator cannot test (extensions, StandBy).
- duo-ship: App Store Connect screenshots and the April 2027 rule.
- duo-crossplatform: React Native, Flutter, Capacitor and Unity bridges for the host-to-web geometry handoff.
- duo-design: the HIG rubric behind "two layouts, not two devices".
