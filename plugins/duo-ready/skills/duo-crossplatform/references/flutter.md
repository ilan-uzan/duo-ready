Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Flutter on iPhone Duo

State of knowledge (2026-10-26): Google/Flutter had published no official
iPhone Duo guidance. Two GitHub issues define what is known: #193056
(multi-scene, closed as duplicate of #48838) and #193078 (App Switcher preview
distorted, open, P2). Everything about widget-level fixes below is consultancy
guidance (third-party, unverified). Check Flutter's current release notes and
both issues before relying on this file.

Contents

1. Apple rules that apply through the native shell
2. Tracked Flutter issues
3. Widget-layer pitfalls (third-party, unverified)
4. `MediaQuery.displayFeatures` and fold detection
5. Bridging the iOS 27.1 APIs with a platform channel
6. What is unverified or missing
7. URLs

## 1. Apple rules that apply through the native shell

Flutter draws into a `FlutterViewController` hosted in a UIKit window, so the
`ios/Runner` folder is subject to every Apple rule for UIKit apps:

- SDK tiers: build with Xcode 27.1 (27A9275); older SDKs are centered or avoid
  the status bar ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Scene lifecycle required: "Xcode 27 requires the scene lifecycle, so migrate
  first" (Apple UIKit Q&A, [third-party summary, Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
  Check `ios/Runner/Info.plist` for `UIApplicationSceneManifest` and
  `ios/Runner/AppDelegate.swift` for `UIWindow(frame: UIScreen.main.bounds)`;
  Apple's replacement is `UIWindow(windowScene:)` ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).
  The Flutter template's own lifecycle has changed across versions; look at
  the user's generated files rather than assuming.
- Launch screen required for iOS 27 SDK submissions ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
  Flutter's template ships `LaunchScreen.storyboard`; confirm it is still
  referenced by `UILaunchStoryboardName` in Info.plist.
- Orientation: "The inner display doesn't honor supported interface
  orientations" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/));
  `UISupportedInterfaceOrientations` is honored on the outer display only
  ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Safe areas are asymmetric; handle each side independently
  ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- A fold is a size-class and trait change, not a scene disconnect; "The
  process keeps running" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Multiple windows: "iPhone Duo is the first iPhone to support multiple
  instances of your app's UI ... On the outer display of iPhone Duo, new
  windows cannot be created" ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)).
  Flutter cannot take advantage of this yet (section 2).

## 2. Tracked Flutter issues

All third-party (GitHub issue text), status as of 2026-10-26.

### #193056 "[iPhone Duo] Support multi scenes" (closed as duplicate)

[flutter issue #193056](https://github.com/flutter/flutter/issues/193056),
opened 2026-09-19.

- The engine "does not fully support multi-scene"; `FlutterEngine` supports 0
  or 1 `FlutterViewController`.
- The Info.plist template defaults `UIApplicationSupportsMultipleScenes` to
  false.
- Closed 2026-09-24 as a duplicate of #48838 "Support multiple windows on
  iPad/iPhone Duo". Track #48838 for progress.

Consequence: a Flutter app participates in Split View (Apple: "Every app
participates in side-by-side multitasking", [Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/))
but cannot open a second window of itself. Do not promise a two-window
feature to a Flutter team.

### #193078 App Switcher preview distorted (open, P2)

[flutter issue #193078](https://github.com/flutter/flutter/issues/193078),
opened 2026-09-21, labelled P2 and triaged-ios.

- Symptom: the App Switcher preview is "distorted or bulged" after switching
  Duo pose while the app is backgrounded.
- Reported on Flutter 3.47.4 with the Xcode 27.1 beta; related issues #193057
  and #193035; no root cause posted.
- Test implication: add "background the app, change pose, return" to the
  manual pass. There is no workaround recorded in the issue.

### Related community requests

- `cupertino_native_better` issue #102 asks for Duo side-navbar support
  ([GitHub](https://github.com/gunumdogdu/cupertino_native_better/issues/102)),
  which illustrates the general point: a Flutter-drawn navigation bar never
  becomes Apple's vertical bar, because Apple only moves bars provided by its
  own navigation containers ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).

## 3. Widget-layer pitfalls (third-party, unverified)

Source unless stated: [iphoneduosupport.com Flutter](https://iphoneduosupport.com/frameworks/flutter/),
consultancy guidance written before the final SDK shipped.

| Pitfall | Why it fails on Duo | Replacement |
|---|---|---|
| `setPreferredOrientations` (portrait only) as the layout strategy | Ignored on the inner display (follows from Apple: the inner display ignores supported orientations) | Lay out from the available size; keep the call only for the outer display's behaviour |
| `EdgeInsets.symmetric(horizontal: padding.left)` or any single inset mirrored to both sides | Vertical bar inset is one-sided (Apple: handle each side independently) | `MediaQuery.paddingOf(context).left` and `.right` applied separately |
| Pausing playback or timers when the lifecycle state becomes `inactive` | A visible app can be inactive in Split View (third-party) | Pause on `paused` only |
| Caching `MediaQuery` size in a field at build time or at startup | The window is resized by a fold mid-session (Apple's "Reading size once at launch" anti-pattern, [Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)) | Read `MediaQuery` inside `build` so a fold triggers a rebuild |
| Expecting `MediaQuery.displayFeatures` to describe the fold | See section 4 | Platform channel to Apple's reserved-region API |
| Expecting Apple's `ArrangementView` or vertical bars in Flutter widgets | No Flutter binding exists; "ArrangementView/vertical bars need platform channels" | Platform channel plus a native view, or accept Flutter-drawn layout |

Apple's underlying rule for all rows: "Size your views relative to their
container rather than to fixed iPhone dimensions" ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
Flutter's `MediaQuery` already gives the window size;
the failure mode is caching the value or branching on a device check.

Composed example of per-side insets, using only symbols named above:

```dart
// Composed from third-party guidance; not run against Flutter 3.47.
import 'package:flutter/widgets.dart';

class DuoFriendlyPadding extends StatelessWidget {
  const DuoFriendlyPadding({super.key, required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final padding = MediaQuery.paddingOf(context); // re-evaluated when the window resizes
    return Padding(
      padding: EdgeInsets.only(left: padding.left, right: padding.right), // never symmetric
      child: child,
    );
  }
}
```

## 4. `MediaQuery.displayFeatures` and fold detection

- iphoneduosupport.com: `MediaQuery.displayFeatures` on iOS is
  "unconfirmed ... Flutter has announced nothing" (third-party).
- mirzaaghazadeh/iphone-duo-skills states that `displayFeatures` is documented
  only for Android and returns empty on Duo (third-party, unverified;
  [GitHub](https://github.com/mirzaaghazadeh/iphone-duo-skills)).
- Apple's model is different from Android's hinge feature list: the fold is a
  reserved region of kind division that "is active when iPhone Duo is
  partially open, but inactive when it is fully open", and the cameras are
  occlusions ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
  The fold is also not part of `safeAreaInsets`; "Safe-area insets alone are
  not enough" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

So a Flutter app that must avoid the fold needs the Apple API through a
platform channel (section 5). A Flutter app that only needs to adapt its
columns can follow the HIG without any fold data: "In a grid-style layout,
prefer an even number of columns so content divides cleanly"
([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

## 5. Bridging the iOS 27.1 APIs with a platform channel

- Community package: `berkaycatak/foldable` for Flutter existed at research
  time (18 stars). Its API surface, requirements and repository URL were not
  captured in the report, so locate it and read its README before
  recommending it (third-party, unverified).
- Hand-written channel: implement the Swift side in `ios/Runner` from Apple's
  documented symbols, then stream to Dart:
  - `UIView.reservedRegions(kind:options:)` with
    `UIView.ReservedRegion.Kind.occlusion` / `.division` and
    `UIView.ReservedRegion.QueryOptions.includeInactive`; "UIKit tracks the
    regions you read in `updateConstraints()` and runs it again when the
    regions change" ([UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))).
    Read them on the `FlutterViewController`'s view and send frames in that
    view's coordinate space, which Flutter's logical pixels match at scale 1
    (inferred; verify on the simulator).
  - `UIHingeInteraction(updateHandler:)` with `UIHinge.angle` ("The current
    angle of the hinge, in radians.") and `UIHinge.status`
    ([UIHingeInteraction](https://developer.apple.com/documentation/uikit/uihingeinteraction);
    [UIHinge](https://developer.apple.com/documentation/uikit/uihinge)).
  - Size classes: `traitCollection.horizontalSizeClass` /
    `.verticalSizeClass` with `registerForTraitChanges(_:target:action:)`
    ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- Rules for the bridge: "Hinge data is ideal for driving interactions and
  effects. For layout decisions, use the arrangement and region APIs"
  ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/));
  "There's no single pose API" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
  Send status, angle, division frames and size classes to Dart; do not invent
  a pose enum or angle thresholds.
- Gate the Swift side with `if #available(iOS 27.1, *)`; Apple recommended
  "gating iOS 27.1 APIs behind availability checks" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

See `duo-layout` and `duo-scenes` for Apple's verbatim Swift examples of these
APIs.

## 6. What is unverified or missing

- No Flutter release note, Flutter blog post, or `flutter.dev` doc mentioning
  iPhone Duo was found.
- Whether `MediaQuery.displayFeatures` is empty on Duo is a third-party claim;
  measure it on the Xcode 27.1 simulator before telling a user it is empty.
- The App Switcher distortion (#193078) has no root cause or workaround.
- `berkaycatak/foldable`: API, requirements and URL not captured.
- The Medium article "iPhone Duo is coming and your Flutter app is probably
  going to break" returned 403 and was not read; do not cite it.
- No measurement of Flutter's `MediaQuery.padding` values beside the vertical
  bar was found; Apple publishes no point figures.

## 7. URLs

Apple:
- https://developer.apple.com/iphone-duo/prepare/
- https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo
- https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo
- https://developer.apple.com/videos/play/tech-talks/111461/
- https://developer.apple.com/videos/play/tech-talks/111464/
- https://developer.apple.com/forums/thread/847644
- https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key
- https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)
- https://developer.apple.com/documentation/uikit/uihingeinteraction
- https://developer.apple.com/documentation/uikit/uihinge

Third-party:
- https://github.com/flutter/flutter/issues/193056
- https://github.com/flutter/flutter/issues/193078
- https://github.com/gunumdogdu/cupertino_native_better/issues/102
- https://github.com/mirzaaghazadeh/iphone-duo-skills
- https://iphoneduosupport.com/frameworks/flutter/
- https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums (summary of Apple's UIKit Q&A)
