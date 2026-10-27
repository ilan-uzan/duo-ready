Last verified: 2026-10-27 against the report and the Expo guide; Xcode 27.1 (27A9275)

# React Native and Expo on iPhone Duo

State of knowledge (2026-10-27): Expo published an official guide on 2026-10-23
(https://expo.dev/blog/supporting-iphone-duo, third-party to Apple, first-party to
Expo): it requires Expo SDK 58 and Xcode 27.1, recommends Expo Router
`NativeTabs`, and documents `expo-hinge` (`useHinge`; statuses `closed`,
`partiallyOpen`, `fullyOpen`, `unknown`), `react-native-reserved-regions`
(a community package it links to), `ArrangementView` and the rail APIs. Meta had
published no iPhone Duo documentation as of 2026-10-26. One launch crash was
fixed in RN 0.88 (issue #58606). Two community packages bridge the iOS 27.1 fold
APIs. Everything else in this file
about the JS layer is consultancy guidance (third-party, unverified). Check the
current React Native release notes, the Expo SDK changelog, and the issue
tracker before relying on any line below; this is the fastest-aging reference
in the repo.

Contents

1. Apple rules that apply through the native shell
2. Issue #58606: "UIScene life cycle is required" (fixed in 0.88)
3. JS-layer pitfalls (third-party, unverified)
4. Community bridges for the iOS 27.1 APIs (third-party, unverified)
5. What is unverified or missing
6. URLs

## 1. Apple rules that apply through the native shell

React Native renders inside a UIKit window, so every Apple rule for UIKit apps
applies to the `ios/` folder of an RN project:

- SDK tiers: build with Xcode 27.1 (27A9275) to get the full inner display and
  vertical bars; Xcode 27.0 builds avoid the status bar; Xcode 26 and earlier
  are centered ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/);
  [Apple Software Releases](https://developer.apple.com/news/releases?id=10152026a)).
- Scene lifecycle: Apple's UIKit Q&A reportedly said "Xcode 27 requires the
  scene lifecycle, so migrate first" ([third-party summary, Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- Launch screen: "Starting in iOS 27 and iPadOS 27, a launch screen is required
  for App Store submission" ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
- Orientation: "The inner display doesn't honor supported interface
  orientations" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/));
  "There is no sanctioned way to lock the inner display to portrait"
  ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Idiom: "its device idiom is still `.phone`" and iPhone apps "have regular size
  classes when resized" ([Apple Developer Forums 847945](https://developer.apple.com/forums/thread/847945)).
- Safe areas: "Safe areas and layout margins are often asymmetric on iPhone
  Duo. Handle each side independently" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Fold is a trait change: "Opening or closing the device, or switching
  displays, is treated as a size-class and trait change, not a scene
  disconnect or app termination. The process keeps running"
  ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Custom bars never go vertical: "Content from custom `UIToolbar`,
  `UINavigationBar`, or `UITabBar` instances isn't considered"
  ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
  A tab bar drawn in JS is further from the system than that, so it stays
  where you draw it (inferred from Apple's statement).

## 2. Issue #58606: "UIScene life cycle is required" (fixed in 0.88)

Source: [react-native issue #58606](https://github.com/react/react-native/issues/58606)
(third-party; opened 2026-09-19, closed 2026-10-16).

- Symptom: React Native 0.88.0-rc.0 on the Duo simulator failed to launch with
  "Application failed to launch: UIScene life cycle is required for apps built
  with this SDK."
- Fix reported in the issue: add `SceneDelegate.swift`, add the
  `UIApplicationSceneManifest` key to Info.plist, and move `UIWindow` creation
  and `startReactNative` from the AppDelegate into the SceneDelegate.
- Expo: `expo-build-properties` → `"ios": {"enableSceneSupport": true}`.
- Status: "should be fixed in 0.88"; closed 2026-10-16 as fixed in RN 0.88. No
  maintainer comment appears on the issue page, and a user asked why the
  upgrade helper omits the change. Confirm against the 0.88 release notes.

What to check in the user's project:

1. `package.json`: is `react-native` 0.88 or later? If older, either upgrade or
   apply the manual fix.
2. `ios/<App>/Info.plist`: does it contain `UIApplicationSceneManifest`? The
   audit rule DUO-009 reports its absence.
3. `ios/<App>/AppDelegate.swift` (or `.mm`): is a window created with
   `UIWindow(frame: UIScreen.main.bounds)`? Apple's replacement is
   `UIWindow(windowScene:)` ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
4. For Expo managed projects, `app.json` / `app.config.*`: is
   `expo-build-properties` present with `ios.enableSceneSupport: true`?

Minimal shape of the native side when the fix is applied by hand. The RN
bootstrap call differs by RN version and template (the issue names
`startReactNative`), so copy that line from the user's existing AppDelegate
instead of inventing it:

```swift
// Composed from Apple-documented APIs; type-checked with swiftc against the iOS 27.1 simulator SDK (Xcode 27.1, 27A9275) on 2026-10-27. Not run on a device.
// The React Native bootstrap call is template-specific; take it from the project's AppDelegate.
import UIKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene,
               willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        // <- start React Native and set window.rootViewController here,
        //    using the project's existing bootstrap code.
        window.makeKeyAndVisible()
        self.window = window
    }
}
```

Info.plist needs a `UIApplicationSceneManifest` dictionary whose scene
configuration names this class as the delegate. Apple's own pages quoted in
the report do not show the manifest XML, so generate it from Xcode's template
(a fresh iOS App project) rather than from memory.

## 3. JS-layer pitfalls (third-party, unverified)

Source unless stated: [iphoneduosupport.com React Native](https://iphoneduosupport.com/frameworks/react-native/),
consultancy guidance, "verified 2026-09-15" by its author, before the final
SDK shipped.

| Pitfall | Why it fails on Duo | Replacement |
|---|---|---|
| `Dimensions.get('window')` at module scope (`const { width } = Dimensions.get('window')` at file top) | Captured once; a fold resizes the window mid-session (Apple's "Reading size once at launch" anti-pattern, [Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)) | `useWindowDimensions()` inside the component so it re-renders on resize |
| `lockToPortrait()` (orientation-locker style libraries) | Inner display ignores supported orientations (Apple, above) | Make the layout work wide and short; keep the lock only for the outer display if needed |
| `Math.max(insets.left, insets.right)` or one inset applied to both sides | Vertical bar inset is one-sided; Apple says handle each side independently | Read each edge from `useSafeAreaInsets()` and apply per side |
| `Platform.isPad` gating a wide layout | `Platform.isPad` is `false` on Duo (idiom stays `.phone`, Apple) | Branch on `useWindowDimensions()` width and height, or expose size classes through a native module |
| Pausing media whenever the app state is not `active` | A visible app can be `inactive` in Split View, so video freezes while on screen | Pause on `background` only |
| Expecting JS bindings for `ReservedRegion`, `ArrangementView`, `onHingeChange` | None exist in React Native core | Use a bridge (section 4) or a native module |
| `expo-hinge` before SDK 58 | An older community report called the npm package a placeholder; Expo's guide (2026-10-23) now documents it as an SDK 58 library | Use it only on Expo SDK 58+; read its docs at docs.expo.dev/versions/v58.0.0/sdk/hinge/ |

Related: `react-native-screens` shipped Duo fixes on 2026-10-13 (third-party,
unverified; no changelog entry was captured, so check the package release
notes for the version that contains them).

Composed example of the width read, using only symbols named above:

```tsx
// Composed from third-party guidance; not run against RN 0.88.
import { useWindowDimensions } from 'react-native';
// useSafeAreaInsets comes from the safe-area library the project already uses.

export function useDuoFriendlyLayout() {
  const { width, height } = useWindowDimensions(); // re-renders on fold/unfold
  const insets = useSafeAreaInsets();               // read left and right separately
  const wide = width > height;                      // compare width vs height, not a device check
  return { width, height, wide, paddingLeft: insets.left, paddingRight: insets.right };
}
```

Apple's version of the same rule is "Compare available width vs height; use
size classes" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
React Native does not expose UIKit size classes in core; if the app needs
them, bridge `traitCollection.horizontalSizeClass` / `.verticalSizeClass`
from native (Apple symbols; [Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).

## 4. Community bridges for the iOS 27.1 APIs (third-party, unverified)

Neither package has been run or reviewed by this repo. Read the README at the
time of use; v0.1.0 APIs change.

### `@cawrestler/react-native-duo` v0.1.0 (MIT)

Source: [CAWRESTLER/react-native-duo](https://github.com/CAWRESTLER/react-native-duo)
(4 stars at research time).

- Requirements stated by the README: New Architecture (Fabric), Xcode 27.1+,
  iOS 27.1+ for native behavior; tested on RN 0.88.0-rc.1 / React 19.3.0 /
  Expo SDK 58; Expo Go unsupported.
- Bridges: `UIHingeInteraction`, `UIView.reservedRegions`,
  `UIArrangementViewController`, `AVCaptureDeviceDirectionCoordinator`,
  `UISceneAccessory` (all Apple iOS 27.1 symbols; the first four are
  documented at the Apple URLs in `duo-layout`, `duo-scenes`, `duo-camera`).
- JS surface: hooks `useDuoHinge`, `useDuoReservedRegions`; components
  `DuoArrangementView`, `DuoAdaptiveToolbar`, `DuoCameraView`,
  `DuoSceneAccessory`.
- Stated limitations: no photo capture, no independent RN windows, JS tabs do
  not become native rails, Expo Go unsupported.

### `thiagobrez/react-native-arrangement-view`

Source: [react-native-arrangement-view](https://github.com/thiagobrez/react-native-arrangement-view)
(49 stars at research time). Wraps the arrangement view only; its API surface
and requirements were not captured in the report, so read the README.

### Writing your own bridge

Implement the Swift side from Apple's documented APIs (see `duo-layout` for
`UIView.reservedRegions(kind:options:)` and `UIArrangementViewController`,
`duo-scenes` for `UIHingeInteraction`), then emit events to JS. Keep in mind:

- Apple: "Hinge data is ideal for driving interactions and effects. For layout
  decisions, use the arrangement and region APIs" ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)).
- Apple: hinge "Update rate and precision are system policy, so don't depend
  on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
  Do not derive "tent" / "laptop" thresholds in JS.
- Apple: "There's no single pose API" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
  Expose status, angle, active division frames and size classes, not a pose.
- The iOS 27.1 SDK (27A9275) declares `UIHinge.Status` `.unknown`, `.closed`,
  `.partiallyOpen`, `.fullyOpen` (UIKit header, read 2026-10-27); a bridge's own
  status strings are its own choice.
- Reserved regions arrive only after the first layout pass and must not be
  cached (third-party, unverified, simulator observation).

## 5. What is unverified or missing

- No official React Native release notes mentioning iPhone Duo were found.
  Expo's guide exists (see the top of this file); its API names were read from
  the blog text on 2026-10-27, not compiled or run. The "fold API open PR" claim on iphoneduosupport.com carries no
  PR number.
- The exact RN 0.88 change that fixes #58606 (template change vs runtime) was
  not captured; the issue page has no maintainer comment.
- Whether `useWindowDimensions()` fires during the hinge transition or only at
  the end was not measured.
- No measurement of the vertical-bar inset as seen by the
  `useSafeAreaInsets()` hook was found; Apple publishes no point
  figures, and the commonly quoted 84 pt is a simulator measurement
  (third-party, unverified).
- `@cawrestler/react-native-duo` was tested by its author on a release
  candidate (0.88.0-rc.1), not on final 0.88.

## 6. URLs

Apple:
- https://developer.apple.com/iphone-duo/prepare/
- https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo
- https://developer.apple.com/videos/play/tech-talks/111461/
- https://developer.apple.com/videos/play/tech-talks/111462/
- https://developer.apple.com/videos/play/tech-talks/111464/
- https://developer.apple.com/forums/thread/847644
- https://developer.apple.com/forums/thread/847945
- https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key
- https://developer.apple.com/news/releases?id=10152026a

Third-party:
- https://github.com/react/react-native/issues/58606
- https://github.com/CAWRESTLER/react-native-duo
- https://github.com/thiagobrez/react-native-arrangement-view
- https://iphoneduosupport.com/frameworks/react-native/
- https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums (summary of Apple's UIKit Q&A)
