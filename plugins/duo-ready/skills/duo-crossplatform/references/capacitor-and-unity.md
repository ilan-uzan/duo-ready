Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Capacitor/Ionic and Unity on iPhone Duo

State of knowledge (2026-10-26): Ionic/Capacitor had published no iPhone Duo
guidance, and no Unity forum thread, Unity doc, Godot or Unreal statement
about iPhone Duo was found. Apple's own statements about web content,
WKWebView and games are the only official material; the rest is consultancy
guidance (third-party, unverified). Check Capacitor's and Unity's current
release notes before relying on this file.

Contents

1. Shared native-shell rules
2. Capacitor / Ionic: what Apple says about web content
3. Capacitor / Ionic: hybrid pitfalls (third-party, unverified)
4. Capacitor / Ionic: getting fold geometry into the page
5. Unity: what Apple says about games
6. Unity: consultancy guidance (third-party, unverified)
7. What is unverified or missing
8. URLs

## 1. Shared native-shell rules

Both frameworks ship a UIKit app around their content, so the rules in
`SKILL.md` step 2 apply unchanged: build with Xcode 27.1 (27A9275) for the full
inner display ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/));
adopt the scene lifecycle (Apple UIKit Q&A, [third-party summary, Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums));
ship a launch screen ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key));
accept that the inner display ignores supported orientations
([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/));
handle each safe-area side independently ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

Check the generated `ios/App` (Capacitor) or the Xcode project Unity exports
for `UIApplicationSceneManifest`, a launch screen, and
`UIWindow(frame: UIScreen.main.bounds)`; the audit script's DUO-009, DUO-010
and DUO-003 rules report these.

## 2. Capacitor / Ionic: what Apple says about web content

- "There's no API for web pages to detect iPhone Duo specifically. Use
  responsive design instead" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "Safari/WebKit exposes Viewport Segments and Device Posture APIs. Both are
  opt-in experimental features in iOS 27.1, enabled at Settings > Apps >
  Safari > Advanced > Feature Flags" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
  They are off for essentially all users and they are Safari features.
- For WKWebView, which is what Capacitor renders into: "Query geometry in the
  host and pass it to the page. Viewport-segment and posture APIs are
  experimental Safari features, not available in WKWebView. CSS insets don't
  account for the fold" (Apple UIKit Q&A, [third-party summary, Q41](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- iOS Safari and WKWebView user agents do not disclose the iPhone model
  (third-party, [DeviceAtlas](https://deviceatlas.com/blog/mobile-browser-user-agent-strings)),
  so UA sniffing cannot find a Duo even if you wanted to.

Consequences: a Capacitor app cannot learn about the fold from CSS or the
web platform inside the app. It can be responsive to width and height, and it
can receive geometry from a plugin (section 4).

## 3. Capacitor / Ionic: hybrid pitfalls (third-party, unverified)

Sources: [iphoneduosupport.com Capacitor](https://iphoneduosupport.com/frameworks/capacitor/)
("Ionic has published no iPhone Duo guidance") and [Plurigent](https://plurigent.com/tutorials/iphone-duo/webview).

| Pitfall | Why it fails on Duo | Replacement |
|---|---|---|
| `env(safe-area-inset-*)` reading zero | They are zero without `viewport-fit=cover` in the viewport meta tag | Add `viewport-fit=cover`, then pad with `env(safe-area-inset-left)` and `env(safe-area-inset-right)` separately |
| One horizontal inset mirrored to both sides | The vertical bar inset is one-sided (Apple: handle each side independently) | Per-side `env()` values |
| UA sniffing to choose phone vs tablet layout | No detection API; UA does not expose the model | `min-width` media queries or container queries |
| `100vh` for full-height panels | Viewport height changes with pose and bars | `100dvh` |
| `window.innerWidth` cached at load | Fold resizes the viewport mid-session | `ResizeObserver` on the root element, or `visualViewport` events |
| Double safe-area padding | Native container already insets and CSS insets again | Pick one layer to own the inset |
| SPA scroll restoration fights Safari 27.0 scroll anchoring | Reported conflict | `overflow-anchor: none` on the scrolling container (Plurigent) |

The Capacitor status bar and keyboard plugins were reported to "behave
normally" (iphoneduosupport.com, third-party, unverified).

Inferred breakpoint warning: CSS px equal points on iOS Safari, Apple
publishes no point dimensions, and the simulator-measured widths are roughly
466 pt (outer) and 669 / 951 pt (inner), all third-party. Common 600 to 700 px
breakpoints will therefore flip between phone and tablet layouts during a
single fold; test that transition for layout thrash (inferred).

Composed example of the meta tag and per-side padding, using only the
properties named above:

```html
<!-- Composed from third-party guidance; not tested in a Capacitor build. -->
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
  .app-shell {
    min-height: 100dvh;
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right); /* never copy left to right */
  }
</style>
```

## 4. Capacitor / Ionic: getting fold geometry into the page

Apple's instruction for WKWebView is to query geometry in the host and pass it
to the page (third-party summary of Apple's UIKit Q&A, Q41). In Capacitor
terms that is a plugin:

- Community option: `erkamyaman/capacitor-foldable` existed at research time
  (44 stars; [GitHub](https://github.com/erkamyaman/capacitor-foldable)).
  Its API surface and requirements were not captured in the report; read its
  README before recommending it (third-party, unverified).
- Hand-written plugin: on the Swift side read Apple's documented symbols and
  post events to the web view:
  - `UIView.reservedRegions(kind:options:)` with `.division` / `.occlusion`
    and `.includeInactive`, tracked in `updateConstraints()`
    ([UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))).
  - `UIHingeInteraction(updateHandler:)`, `UIHinge.angle` (radians) and
    `UIHinge.status` ([UIHingeInteraction](https://developer.apple.com/documentation/uikit/uihingeinteraction);
    [UIHinge](https://developer.apple.com/documentation/uikit/uihinge)).
  - `traitCollection.horizontalSizeClass` / `.verticalSizeClass`
    ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
  Convert region frames to the web view's coordinate space before sending
  them; CSS px equal points at the web view's default scale (inferred).
- Apple's rules for what you send: hinge data is for effects, regions and
  arrangements for layout ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/));
  "There's no single pose API" and hinge "Update rate and precision are system
  policy, so don't depend on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
  Send frames, status, angle and size classes; do not invent a pose string.
- Progressive enhancement in the page: if the plugin is absent (web build,
  older iOS), fall back to responsive layout. Feature-detect the Safari APIs
  only for the browser build (`'segments' in window.viewport`,
  `'devicePosture' in navigator`, `@media (device-posture: folded)`); the
  spec surface is `vertical-viewport-segments` / `horizontal-viewport-segments`,
  `env(viewport-segment-width/height/top/left/bottom/right)`,
  `viewport.segments`, `navigator.devicePosture` with a `change` event
  (third-party, [MDN Viewport Segments API](https://developer.mozilla.org/en-US/docs/Web/API/Viewport_Segments_API);
  [Chrome foldable APIs](https://developer.chrome.com/blog/foldable-apis-ot)).
  WebKit's standards positions #327 and #328 were still open with no formal
  position ([WebKit standards-positions #327](https://github.com/WebKit/standards-positions/issues/327);
  [#328](https://github.com/WebKit/standards-positions/issues/328)).

## 5. Unity: what Apple says about games

Apple has no Unity-specific material. Its game rules are in the HIG and the
Group Lab and apply to any engine:

- "Make your game playable in every device pose" (bolded HIG best practice,
  [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- "You can choose to lock to either portrait or landscape orientation, but be
  sure to fill the screen as the device pose changes ... Prefer changing the
  aspect ratio over letterboxing or pillarboxing in games; if you can't avoid
  letterboxing or pillarboxing, add artwork to the padding area"
  ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- "Don't assume fixed ratios. Resize to fit each pose, favor changing aspect
  ratio over letterboxing, and add artwork to unavoidable padding"; Split View
  and PiP "mean apps may run at varying aspect ratios, so they should be
  freely resizable" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644);
  [Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)).
- Orientation: the outer display honors supported orientations, the inner
  display ignores them ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
  A landscape-locked game will therefore run in whatever shape the inner
  display gives it; "fill the screen" is the requirement, not the lock.
- `UIRequiresFullScreen` no longer prevents resizing; TN3192's sample shows the
  intended hook for swapping assets on a discrete resize: compare
  `coordinateSpace.bounds.size` in `windowScene(_:didUpdateEffectiveGeometry:)`
  and act when `!geometry.isInteractivelyResizing`
  ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
- Safe areas are asymmetric, each side independently ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Apple's October 2026 newsroom post lists games among the 60+ optimized apps
  (Asphalt Legends, Deck-Man named in the report; Zenless Zone Zero and
  UnGodly in the notes) without naming the engines
  ([Apple Newsroom, Oct 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/)).
  Do not tell a user "Unity games are confirmed working" on that basis.

## 6. Unity: consultancy guidance (third-party, unverified)

Source: [iphoneduosupport.com Unity](https://iphoneduosupport.com/frameworks/unity/).
No Unity forum thread or official document was found; the only other Unity
hit was Microsoft's Surface Duo guide, which is a different device.

| Pitfall | Why it fails on Duo | Replacement |
|---|---|---|
| Caching `Screen.width` / `Screen.height` at `Start` | A fold resizes the view mid-session | Poll each frame and call `RebuildLayout()` on affected canvases when the values change |
| Symmetric safe-area math | `Screen.safeArea` works, but its insets are asymmetric beside the vertical bar | Apply the `Screen.safeArea` rect as given, per edge |
| Fixed-aspect letterboxing | Apple's HIG rule above; the consultancy adds it "looks dated" | Change aspect ratio; if padding is unavoidable, add artwork (Apple HIG) |
| Orientation lock as the layout strategy | Allowed "for games if the game still fills the screen" (consultancy paraphrase of the HIG rule) | Keep the lock if you want, but fill whatever shape the inner display gives |
| Pausing game time in `OnApplicationPause` and expecting it on a fold | `OnApplicationPause` is reported not to fire on a fold, so a time-stop keyed to it looks frozen | Drive pause from explicit resize handling, not from the pause callback |
| Cached input regions | Touch regions computed once go stale after a resize | Recompute with the size poll |
| HUD elements centered on screen | The fold divides the inner display when partially open ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)) | Keep HUD off the center; anchor to edges |
| Reading the hinge from C# | No Unity API | Native plugin wrapping `UIHingeInteraction` (Apple symbol) |

Apple's "Reading size once at launch" anti-pattern and its "because a fold
can resize your app in the middle of a session" rationale cover the first and
sixth rows ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).

Composed example of the size poll, using only the symbols named above:

```csharp
// Composed from third-party guidance; not run in Unity against the iOS 27.1 SDK.
using UnityEngine;

public class DuoResizeWatcher : MonoBehaviour
{
    int lastWidth, lastHeight;
    Rect lastSafeArea;

    void Update()
    {
        if (Screen.width != lastWidth || Screen.height != lastHeight || Screen.safeArea != lastSafeArea)
        {
            lastWidth = Screen.width;
            lastHeight = Screen.height;
            lastSafeArea = Screen.safeArea; // asymmetric: apply each edge as given
            // Re-anchor HUD canvases here (project-specific), then rebuild their layout.
        }
    }
}
```

## 7. What is unverified or missing

- No Ionic, Capacitor, Unity, Godot or Unreal statement about iPhone Duo was
  located.
- No source on how `env(safe-area-inset-*)` behaves beside the vertical bar
  and the Dynamic Island on the side, or on `visualViewport` during a fold
  (report Appendix C).
- Apple did not state whether the Safari feature flags affect WKWebView;
  assume they do not (the UIKit Q&A summary says they are not available).
- `erkamyaman/capacitor-foldable`: API and requirements not captured.
- `OnApplicationPause` behaviour on fold, `Screen.safeArea` values, and the
  `RebuildLayout()` advice are consultancy claims, not measurements shared
  with code.
- Whether the Unity-built titles Apple showcased changed anything beyond a
  rebuild is unknown.
- No Apple statement on Metal, SpriteKit or game-engine behaviour beyond
  "prefer changing aspect ratio" (notes, KQ4 gaps).

## 8. URLs

Apple:
- https://developer.apple.com/iphone-duo/prepare/
- https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo
- https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
- https://developer.apple.com/videos/play/tech-talks/111461/
- https://developer.apple.com/videos/play/tech-talks/111464/
- https://developer.apple.com/videos/play/tech-talks/111466/
- https://developer.apple.com/forums/thread/847644
- https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key
- https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)
- https://developer.apple.com/documentation/uikit/uihingeinteraction
- https://developer.apple.com/documentation/uikit/uihinge
- https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/

Third-party:
- https://iphoneduosupport.com/frameworks/capacitor/
- https://iphoneduosupport.com/frameworks/unity/
- https://plurigent.com/tutorials/iphone-duo/webview
- https://github.com/erkamyaman/capacitor-foldable
- https://github.com/WebKit/standards-positions/issues/327
- https://github.com/WebKit/standards-positions/issues/328
- https://developer.mozilla.org/en-US/docs/Web/API/Viewport_Segments_API
- https://developer.chrome.com/blog/foldable-apis-ot
- https://deviceatlas.com/blog/mobile-browser-user-agent-strings
- https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums (summary of Apple's UIKit Q&A)
