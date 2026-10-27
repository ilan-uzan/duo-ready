Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Web content and WKWebView on iPhone Duo

Contents
1. What Apple says
2. Safari: the flag-gated APIs and how to feature-detect them
3. WKWebView: the host must pass geometry
4. Hybrid CSS fixes (third-party, unverified)
5. Viewport arithmetic (inferred)
6. PWA and home-screen web apps
7. Gaps

## 1. What Apple says

- "Safari/WebKit exposes Viewport Segments and Device Posture APIs. Both are opt-in experimental features in iOS 27.1, enabled at Settings > Apps > Safari > Advanced > Feature Flags" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "There's no API for web pages to detect iPhone Duo specifically. Use responsive design instead"; web developers "shouldn't detect device type" (same thread).
- For WKWebView: "Query geometry in the host and pass it to the page. Viewport-segment and posture APIs are experimental Safari features, not available in WKWebView. CSS insets don't account for the fold" (Apple UIKit Q&A as summarized by a third party, [Gubarenko Q41](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- Safe areas on the native side "are often asymmetric on iPhone Duo. Handle each side independently" (Tech Talk 111461, "Prepare your app for iPhone Duo"). The fold itself is not part of `safeAreaInsets`: "Custom bottom sheets need fold avoidance using reserved regions. Safe-area insets alone are not enough" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- WWDC26 session 204 (Safari 27) lists no foldable APIs, and Safari 27.1 release notes were not located ([WWDC26 session 204](https://developer.apple.com/videos/play/wwdc2026/204/)).

## 2. Safari: the flag-gated APIs

WebKit's standards-positions issues #327 (Viewport Segments) and #328 (Device Posture) were opened in March 2024 and still carry no formal position; on Sept 20, 2026 a Chrome DevRel asked for a position citing iPhone Duo and then noted the feature "is available behind a flag in the 27.1 Simulator" (third-party, [WebKit standards-positions #327](https://github.com/WebKit/standards-positions/issues/327), [#328](https://github.com/WebKit/standards-positions/issues/328)). The W3C Device Posture proposal "does not expose the raw hinge angle sensor value" (privacy rationale, same issue).

The spec surface, as documented by MDN and Chrome (not Apple):

| Surface | Form |
|---|---|
| CSS media features | `vertical-viewport-segments`, `horizontal-viewport-segments` |
| CSS environment variables | `env(viewport-segment-width/height/top/left/bottom/right)` (each takes segment indices per the spec) |
| JS | `viewport.segments` (array of `DOMRect`) |
| Posture media feature | `@media (device-posture: folded)` / `@media (device-posture: continuous)` |
| Posture JS | `navigator.devicePosture` with a `change` event |

Sources: [MDN Viewport Segments API](https://developer.mozilla.org/en-US/docs/Web/API/Viewport_Segments_API), [MDN Viewport](https://developer.mozilla.org/en-US/docs/Web/API/Viewport), [Chrome: Origin trial for Foldable APIs](https://developer.chrome.com/blog/foldable-apis-ot).

Because the features are opt-in in Safari, expect them to be off for nearly all users at launch and treat them strictly as progressive enhancement (inferred). Feature-detect before use:

```js
// Composed from the MDN/Chrome-documented surface; not tested in Safari on iOS 27.1.
const hasSegments = typeof viewport !== 'undefined' && 'segments' in viewport;
const hasPosture  = 'devicePosture' in navigator;

if (hasPosture) {
  navigator.devicePosture.addEventListener('change', () => {
    relayout();   // the spec's posture values are 'folded' and 'continuous'
  });
}
```

Do not ship CSS that depends on `env(viewport-segment-*)` without a fallback declaration before it; the variable resolves to nothing where the API is absent (inferred from how `env()` fallbacks work; no Apple statement).

## 3. WKWebView: the host must pass geometry

Apple's answer is that the fold APIs are not available in WKWebView and CSS insets do not describe the fold. The pattern the Q&A prescribes is "Query geometry in the host and pass it to the page". Concretely:

1. In the native container that hosts the web view, read the fold and camera regions in the view's coordinate space with `reservedRegions(kind:options:)` on `UIView` (`UIView.ReservedRegion.Kind.occlusion` / `.division`, `UIView.ReservedRegion.QueryOptions.includeInactive`); "UIKit tracks the regions you read in `updateConstraints()` and runs it again when the regions change" ([UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))). In SwiftUI use `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)` ([GeometryProxy.reservedRegions](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:))). "The fold's division region is active only when the device is folded. When flat, it is inactive with a width of zero" (Tech Talk 111463).
2. Read the host view's safe-area insets per side (they are asymmetric) and, if the page needs it, the hinge status from `UIHingeInteraction` / `onHingeChange`.
3. Push those values into the page through whatever native-to-web bridge your app already uses (a message channel, injected script, or framework plugin), as CSS custom properties or a JS object, and re-push whenever they change. The scanner's DUO-021 finding marks the container that needs this.
4. In the page, lay out from those values with responsive CSS; never from `navigator.userAgent`.

Member names on `UIView.ReservedRegion` (`isActive`, `frame`, `margins`) are reported by the community, not confirmed from an Apple reference page (third-party, unverified). Regions arrive only after the first layout pass and inactive regions can return zero-size frames, so check `isActive` first (third-party, unverified).

Cross-platform containers (Capacitor, React Native web views, Flutter web views) need a native plugin for the same handoff; see duo-crossplatform.

## 4. Hybrid CSS fixes (third-party, unverified)

From Capacitor and web-view write-ups ([iphoneduosupport.com Capacitor](https://iphoneduosupport.com/frameworks/capacitor/), [Plurigent](https://plurigent.com/tutorials/iphone-duo/webview)). None of these is an Apple statement:

- `env(safe-area-inset-*)` resolve to zero unless the viewport meta includes `viewport-fit=cover`.
- Apply `env(safe-area-inset-left)` and `env(safe-area-inset-right)` separately; the vertical bar sits on one side only (Apple: asymmetric safe areas, Tech Talk 111461).
- Replace user-agent sniffing with `min-width` media queries or container queries.
- Replace `100vh` with `100dvh`.
- Replace a `window.innerWidth` value cached at load with `ResizeObserver` or `visualViewport` listeners, because the width changes mid-session on a fold.
- Avoid double safe-area padding when the native container already insets the web view and the page also applies `env()` insets.

## 5. Viewport arithmetic (inferred)

CSS px equal points on iOS Safari, and the only point figures available are third-party simulator readings (outer 466×678 pt; inner 669×951 pt portrait, 951×669 pt landscape-native; Apple publishes pixels only: 1398×2034 and 1878×2670). So web viewports land near 466 px wide on the outer display and 669 or 951 px on the inner display, minus browser chrome, and roughly half of those in Split View. Common 600–700 px breakpoints will therefore flip between phone and tablet layouts during a single fold; test that transition for layout thrash, and prefer layouts that resize continuously over ones that swap component trees at a breakpoint (inferred; the native equivalent is the HIG's "Avoid extreme layout changes as people fold the device").

## 6. PWA and home-screen web apps

No Duo-specific guidance exists. They resize like other apps, and the `UIRequiresFullScreen` compatibility mode does not apply to them (inferred). Safari runs two windows side by side on Duo (press report, third-party).

## 7. Gaps

- Safari 27.1 release notes and the exact Feature Flag names were not located; the flag path above is from the Group Lab thread.
- No source documents `env(safe-area-inset-*)` behaviour with the vertical bar or Dynamic Island on the side, nor `visualViewport` behaviour during a fold.
- Apple has not stated whether the flagged APIs will ever be exposed to WKWebView.
- No actual Duo User-Agent string was captured.
- No Apple statement on PWA behaviour.
