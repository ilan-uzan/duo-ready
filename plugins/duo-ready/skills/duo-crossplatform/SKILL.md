---
name: duo-crossplatform
description: >-
  Get a React Native, Expo, Flutter, Capacitor/Ionic or Unity app working on
  Apple's foldable iPhone Duo: the native-shell fixes every framework needs
  (Xcode 27.1 rebuild, UIScene lifecycle, launch screen), the framework-level
  pitfalls that are known as of October 2026, which community bridges exist
  for hinge/reserved-region/arrangement APIs, and what nobody has verified yet.
  Use it whenever a cross-platform iOS app misbehaves on the new foldable
  iPhone, even if the user never says "Duo": "my RN app crashes on launch on
  the new iPhone simulator", "Expo says UIScene life cycle is required", "my
  Flutter screen stays portrait-shaped when the phone opens", "Dimensions are
  wrong after unfolding", "setPreferredOrientations is ignored", "my Ionic app
  has a gap on the right side", "Unity game letterboxes on the foldable",
  "is there a hinge plugin for Flutter/React Native/Capacitor", "does
  displayFeatures work on iPhone". Also use it when a native iOS developer
  asks how a hybrid/web view or game engine layer should learn about the fold.
---

# duo-crossplatform

## What Apple actually says

Apple publishes nothing framework-specific. Expo is the one framework vendor
found with official guidance: its blog post "Supporting iPhone Duo with Expo: a
developer guide" (2026-10-23, https://expo.dev/blog/supporting-iphone-duo) says Expo SDK 58 plus Xcode 27.1
is required. Meta/React Native, Google/Flutter, Ionic/Capacitor and Unity had
published none as of 2026-10-26 (searched, not exhaustive). Apple's rules reach
these apps through the native shell they ship inside:

- The inner display you get depends on the SDK the binary links against:
  "iOS 26 SDK or earlier: The app runs but appears centered on the inner
  display with empty space around it ... iOS 27.1 SDK or later: The app uses
  the full display, and toolbars and tab bars move vertically below the status
  bar" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
  Xcode 27.1 final is build 27A9275 ([Apple Software Releases](https://developer.apple.com/news/releases?id=10152026a)).
- Layout comes from size classes and scene geometry, never from `UIScreen.main`,
  orientation or idiom; "The inner display doesn't honor supported interface
  orientations" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/);
  [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle
  each side independently" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Web content: "There's no API for web pages to detect iPhone Duo specifically.
  Use responsive design instead" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644));
  for WKWebView, "Query geometry in the host and pass it to the page.
  Viewport-segment and posture APIs are experimental Safari features, not
  available in WKWebView. CSS insets don't account for the fold" (Apple UIKit
  Q&A, [third-party summary, Q41](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- Games: "You can choose to lock to either portrait or landscape orientation,
  but be sure to fill the screen as the device pose changes ... Prefer
  changing the aspect ratio over letterboxing or pillarboxing in games; if you
  can't avoid letterboxing or pillarboxing, add artwork to the padding area"
  ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Everything framework-specific below comes from GitHub issues, bridge READMEs
and consultancy write-ups. It is labelled (third-party, unverified) and it will
age fast. Before relying on any of it, check the framework's current release
notes and open issues; a fix may have shipped since this file was written.

## Workflow

### 1. Look at the actual project before advising

Ask for, or open, these files; the advice differs by framework and version:

- The framework and version: `package.json` (`react-native`, `expo`),
  `pubspec.yaml`, `capacitor.config.*`, Unity `ProjectSettings/ProjectVersion.txt`.
- The native shell: `ios/<App>/AppDelegate.swift` or `.mm`, `ios/<App>/Info.plist`,
  `ios/Podfile`, the `.xcodeproj`/`.xcworkspace`, and for Expo `app.json` /
  `app.config.*` (is it managed or bare? does it use `expo-build-properties`?).
- Where the JS/Dart/C# layer reads screen size, orientation and safe-area
  insets (grep for the symbols in the per-framework references).

When a project path is available, run the scanner first and triage its output
with the user:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

Rules DUO-009 (no scene lifecycle), DUO-010 (no launch screen), DUO-021
(WKWebView cannot see the fold) and DUO-030 to DUO-033 (React Native, Flutter,
Capacitor/Ionic, Unity project-level advice) are the ones that matter here.
The framework rules fire on config files and are reminders, not proof of a
bug; confirm each against the code.

### 2. Fix the native shell first (every framework)

These are the same for all four frameworks because they are Apple's rules, and
nothing in the JS/Dart/C# layer can compensate for them.

1. Rebuild with Xcode 27.1 (27A9275) so the binary links the iOS 27.1 SDK.
   Explain the three tiers above; a build from Xcode 27.0 fills "most of the
   inner display but still avoids the status bar" and never gets vertical
   bars ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
   Xcode 27.2 beta did not include Duo support despite the higher number
   (third-party, unverified). A developer verified the stamp with
   `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, expecting `sdk 27.1`
   (third-party, unverified).
2. Adopt the UIScene lifecycle. React Native 0.88.0-rc.0 failed to launch on
   the Duo simulator with "Application failed to launch: UIScene life cycle is
   required for apps built with this SDK"; the fix was a `SceneDelegate.swift`,
   the `UIApplicationSceneManifest` Info.plist key, and moving `UIWindow`
   creation out of the AppDelegate; Expo users set `expo-build-properties` →
   `"ios": {"enableSceneSupport": true}`; the issue closed 2026-10-16 as fixed
   in RN 0.88 ([react-native issue #58606](https://github.com/react/react-native/issues/58606),
   third-party). Apple's UIKit Q&A reportedly said "Xcode 27 requires the
   scene lifecycle, so migrate first" ([third-party summary, Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
   Flutter, Capacitor and Unity templates each generate their own
   AppDelegate; check whether the one in the user's project already has a
   scene manifest rather than assuming. Create windows with
   `UIWindow(windowScene:)`, not `UIWindow(frame: UIScreen.main.bounds)`
   ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
3. Provide a launch screen. "Starting in iOS 27 and iPadOS 27, a launch screen
   is required for App Store submission" ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
4. Stop relying on a portrait lock. `UISupportedInterfaceOrientations` is
   honored on the outer display only; "There is no sanctioned way to lock the
   inner display to portrait" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
   Framework orientation APIs (`lockToPortrait()`, `setPreferredOrientations`,
   Unity's orientation setting) sit on top of the same mechanism, so they are
   ignored on the inner display too (third-party, unverified for each
   framework; follows from Apple's statement). The layout must work in a
   regular-by-regular, roughly square-ish window.
5. Remove `UIRequiresFullScreen = YES` from Info.plist; since iOS 27 it only
   switches the app to discrete resizing and no longer prevents resizing
   ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).

Point the user to `duo-audit` for the full Step 2 anti-pattern list that
applies to any Swift/ObjC code in their `ios/` folder.

### 3. Fix the framework layer

Open the matching reference and work through its pitfall table against the
user's code. The headline items, all (third-party, unverified) unless marked:

| Framework | First things to check |
|---|---|
| React Native / Expo | RN 0.88+ or the SceneDelegate fix above; `Dimensions.get('window')` captured at module scope goes stale after a fold, use `useWindowDimensions()`; `Math.max(insets.left, insets.right)` is wrong, read each edge from `useSafeAreaInsets()`; `Platform.isPad` is `false` on Duo, so iPad-only code paths never run; pause media only on `background`, since a visible app can be `inactive` in Split View; `react-native-screens` shipped Duo fixes on 2026-10-13 |
| Flutter | `setPreferredOrientations` ignored on the inner display; `EdgeInsets.symmetric` built from one inset is wrong, use `MediaQuery.paddingOf` left and right separately; pause on `paused`, not `inactive`; `MediaQuery.displayFeatures` is documented for Android only and returns empty on Duo; open P2 bug #193078 (App Switcher preview distorted after switching pose while backgrounded); multi-scene is not supported (#193056 closed as duplicate of #48838) |
| Capacitor / Ionic | `env(safe-area-inset-*)` are zero without `viewport-fit=cover`; apply left/right insets separately; `100vh` → `100dvh`; cached `window.innerWidth` → `ResizeObserver` / `visualViewport`; avoid double safe-area padding when both the native container and CSS inset; no UA sniffing (Apple: no web detection API) |
| Unity | Poll `Screen.width`/`Screen.height` rather than caching them; `Screen.safeArea` works but insets are asymmetric; avoid fixed-aspect letterboxing (Apple HIG rule above is official); `OnApplicationPause` does not fire on a fold, so time-stop logic keyed to it looks frozen; keep HUD elements off the center |

### 4. Decide whether the app needs fold-aware features at all

Apple: "not every app needs to use Arrangement Views or the reserved regions
API" ([Apple Developer Forums 847887](https://developer.apple.com/forums/thread/847887)).
Most cross-platform apps are done after steps 2 and 3 plus a responsive
layout keyed on window width and height. Only continue if the user needs the
fold position (split content around the hinge, hinge-angle effects, a camera
that follows the user, or content on the outer display during capture).

Those APIs (`onHingeChange`/`UIHingeInteraction`, `reservedRegions`,
`ArrangementView`/`UIArrangementViewController`, `AVCaptureDeviceDirectionCoordinator`,
`UISceneAccessory`) are native iOS 27.1 APIs with no first-party JS, Dart,
Capacitor or C# binding as of 2026-10-26. Every framework needs a native
bridge. Options, all third-party and unverified by this repo:

- React Native: `@cawrestler/react-native-duo` v0.1.0 bridges all five
  families (hooks `useDuoHinge`, `useDuoReservedRegions`; components
  `DuoArrangementView`, `DuoAdaptiveToolbar`, `DuoCameraView`,
  `DuoSceneAccessory`); requires the New Architecture, Xcode 27.1+, and does
  not work in Expo Go. `thiagobrez/react-native-arrangement-view` wraps the
  arrangement view only. Details and limits in `references/react-native.md`.
- Flutter: `berkaycatak/foldable` exists (18 stars at research time); its
  API surface was not captured, so read its README before recommending it.
  Otherwise write a platform channel.
- Capacitor: `erkamyaman/capacitor-foldable` exists (44 stars); API surface
  not captured. Otherwise write a plugin that reads geometry in the host and
  posts it to the page, which is exactly what Apple recommends for WKWebView.
- Unity: nothing found; a native plugin is required.

When writing a bridge, implement the Swift side from `duo-layout` (reserved
regions, arrangement views) and `duo-scenes` (hinge, trait changes) and keep
the JS/Dart side a thin event stream. Never expose a "pose" enum to the
framework layer; Apple has none ("There's no single pose API",
[Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

### 5. Verify on the Duo simulator

Xcode 27.1's iPhone Duo simulator is "the best way to test the full native
experience" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
In Device Hub use the Closed, Partially Open and Open buttons and Option-drag
the slider for any angle ([Apple: Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)).
Walk the user through, at minimum:

1. Launch on the outer display, then open the device: does the layout re-read
   width and insets, or does a cached size stay?
2. Fold and unfold mid-session with text input, scroll position and media
   playing; Apple says these are preserved automatically when the app does
   not tear down its hierarchy ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
3. Rotate in both states; check that the "portrait-only" screens are usable
   wide and short.
4. Split View: drag the app by the home indicator to either side
   ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
5. Background the app, switch pose, return: this is the sequence that produced
   Flutter #193078 (third-party).

There is no `simctl` or XCUITest command to set the pose; fold automation
tools are community-only. See `duo-test` for the CI matrix and screenshot
commands, and `duo-ship` for the App Store screenshot sizes.

### 6. Say what is not known

Tell the user plainly: as of 2026-10-26 no framework had official Duo
guidance; the bridges are early (v0.1.0, tens of stars); `displayFeatures`
and similar foldable abstractions designed for Android do not map to Apple's
reserved-region model; and Apple publishes no point dimensions for either
display, so any "466×678 / 669×951 pt" figure in a framework thread is a
simulator measurement (third-party, unverified). Then tell them to re-check
the framework's release notes and issue tracker, because this is the
fastest-moving part of the Duo story.

## Common mistakes

- Shipping a Xcode 27.0 or older build and calling it "Duo support": the app
  is centered or avoids the status bar depending on tier ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- AppDelegate-only app that launches fine on iOS 26 and crashes at launch
  under the iOS 27 SDK (RN #58606, third-party; Apple UIKit Q&A says to
  migrate first, third-party summary).
- Reading window size once at startup, which is the cross-platform shape of
  Apple's "Reading size once at launch" anti-pattern ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
  Module-scope `Dimensions.get`, a cached `MediaQuery` value, a cached
  `window.innerWidth`, cached `Screen.width` in Unity all fail the same way.
- Treating `Platform.isPad` false, idiom `.phone`, or a width breakpoint as
  "it's a phone, use the phone layout"; the inner display is regular by
  regular and idiom stays `.phone` ([Apple Developer Forums 847945](https://developer.apple.com/forums/thread/847945)).
- Symmetric safe-area padding: the vertical bar adds a one-sided inset, and
  Apple says to handle each side independently ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Expecting a framework orientation lock to hold on the inner display
  ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Pausing media whenever the app is not `active`: in Split View a visible app
  can be inactive (third-party, unverified).
- Hoping the web layer can see the fold through CSS or the Viewport Segments
  API inside WKWebView; Apple says to pass geometry from the host (third-party
  summary of Apple UIKit Q&A).
- Inventing pose or hinge-threshold enums in a bridge; Apple exposes none and
  says hinge "Update rate and precision are system policy, so don't depend on
  specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## When to read the references

- `references/react-native.md`: issue #58606 fix details (Info.plist key,
  SceneDelegate, Expo config), the JS pitfall table, both community bridges
  with their requirements and limits, and what is unverified.
- `references/flutter.md`: issues #193056/#48838 and #193078 with status,
  orientation and `MediaQuery` pitfalls, `displayFeatures` reality, the
  platform-channel route, and what is unverified.
- `references/capacitor-and-unity.md`: Apple's web/WKWebView statements, the
  hybrid CSS fixes, the Capacitor plugin route, Apple's HIG game rules, the
  Unity consultancy advice, and the gaps (no Unity, Godot or Unreal statements).

## Related skills

- `duo-audit`: run the scanner and work through Apple's Step 2 grep list on the native `ios/` code.
- `duo-layout`: the Swift side of reserved regions and arrangement views when you write a bridge.
- `duo-scenes`: hinge API, fold-as-trait-change, Split View, scene lifecycle details.
- `duo-bars`: why a JS/Dart-drawn tab bar never becomes a vertical rail and what the native containers do.
- `duo-camera`: `AVCaptureDeviceDirectionCoordinator` and `CameraCaptureAccessory` for camera bridges.
- `duo-test`: Duo simulator, Device Hub, `simctl` screenshots, CI matrix.
- `duo-ship`: App Store Connect screenshots, the April 2027 rule, launch screen.
- `duo-backend`: WKWebView and web-layer behaviour, analytics properties, server-driven UI.
- `duo-design`: HIG rules to hand to the designer of a cross-platform app.
