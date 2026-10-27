Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# SDK tiers and Apple's three steps

Everything quoted here is Apple text as captured in the research report. The
research notes flag that the fetch tool summarised the Three steps page and
the Tech Talk transcripts, so API names and numbers are preserved but prose
wording should be re-checked against the page before being quoted externally.
Third-party material is marked (third-party, unverified).

Contents

1. The three SDK tiers
2. What decides the tier
3. Toolchain facts and dates
4. Step 1: run Apple's App Resizability skill
5. Step 2: fix common patterns (the grep list)
6. Step 3: test resizing
7. "Go further": the App Store half
8. Apple's audit checklist and priority order
9. What Apple has not published

## 1. The three SDK tiers

From "Three steps to make your app shine on iPhone Duo"
(https://developer.apple.com/iphone-duo/prepare/):

> "**iOS 26 SDK or earlier:** The app runs but appears centered on the inner
> display with empty space around it. Closed, it sits beside the status bar
> and camera. **iOS 27 SDK:** The app fills most of the inner display but
> still avoids the status bar. **iOS 27.1 SDK or later:** The app uses the
> full display, and toolbars and tab bars move vertically below the status
> bar. Before shipping with this SDK, confirm your content adapts to the
> vertical bars."

A longer capture of the same page, as recorded in the research notes:

> "Apps built with the iOS 26 SDK or earlier run on iPhone Duo, but won't
> adapt to all layouts. When the device is open, your app will appear in the
> center of the display, with empty space surrounding the window. When the
> device is closed, the outer display will show your app's content to the left
> of the status bar and camera." iOS 27 SDK: "resize to fill most of the inner
> display ... but still avoid the status bar on the right edge." iOS 27.1 SDK:
> "extend to use the full display, with toolbars and tab bars appearing
> vertically below the status bar ... make sure your app's content adapts to
> the bars becoming vertical."

Tech Talk 111461, "Prepare your app for iPhone Duo"
(https://developer.apple.com/videos/play/tech-talks/111461/):

> "Apps run on iPhone Duo without rebuilding with the iOS 27 SDK. When closed,
> the app uses the space left of the status bar and camera. When open, it has
> a familiar size and aspect ratio. With the iOS 27 SDK, the app extends left
> of the status bar on the inner display. With the iOS 27.1 SDK, the app
> extends to the edge of the screen, and standard navigation and toolbar
> buttons lay out vertically under the status bar."

Technology Overview, "Preparing your app for iPhone Duo"
(https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

> "When you build with Xcode 26 and earlier, your app doesn't extend under the
> status bar and camera."

DTS, "A Summary of the iPhone Duo Group Lab"
(https://developer.apple.com/forums/thread/847644) and the DTS reply on
compatibility behaviour (https://developer.apple.com/forums/thread/847887):
unadopted apps run in a compatibility mode. Closed, the app uses the region
outside the vertical bar; fully open, it is centered at a familiar aspect ratio
with letterboxing; partially open, it is shifted to one side. "iPad apps don't
run in compatibility mode on iPhone Duo, unlike on Apple Vision Pro."

In every tier the app still resizes when the device opens or closes: "The app
continues to honor `UIRequiresFullScreen`, but still resizes when the device
opens or closes" (Tech Talk 111461).

What users see when the tier is wrong (third-party, unverified): a day-one
press report described un-updated apps showing "a black bar on the outside
screen and appear centered on a black background inside".

## 2. What decides the tier

- The SDK the binary links against, not its deployment target. An app with an
  iOS 16 deployment target built with Xcode 27.1 is on the iOS 27.1 tier.
- There is no Info.plist key to request the older mode; compatibility depends
  on the build SDK (Gubarenko summary of Apple's UIKit Q&A, Q23,
  https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums; a
  third-party summary of Apple answers).
- There is no Duo idiom, no Duo Info.plist key and no Duo device capability:
  "iPhone Duo is not a separate device class ... iPhone Duo does not support
  Stage Manager and does not have its own `UIUserInterfaceIdiom`", and "apps
  can't require iPhone Duo-specific capabilities"
  (https://developer.apple.com/forums/thread/847644).
- The scanner's DUO-019 reads `LastUpgradeCheck` from `project.pbxproj` and
  flags values below 2710. That is a proxy for the Xcode version that last
  upgraded the project, not evidence about the SDK of any particular build.
- Checking a built binary (third-party, unverified):
  `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, which should read
  `sdk 27.1`. The same developer reported a `swiftc -sdk` build accidentally
  stamped 27.0.

## 3. Toolchain facts and dates

| Fact | Status | Source |
|---|---|---|
| iPhone Duo announced September 9, 2026; HIG page "Designing for iPhone Duo" and six Tech Talks (111461 to 111466) published the same day | Apple | https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo ; https://developer.apple.com/iphone-duo/ |
| Xcode 27.1 beta announced September 18, 2026 | Apple | https://developer.apple.com/news/?id=nyuppv9r |
| App Store Connect accepts Duo-optimized submissions from October 5, 2026 | Apple | https://developer.apple.com/news/?id=kkphp5qo |
| Xcode 27.1 final, build 27A9275, released October 15, 2026 | Apple | https://developer.apple.com/news/releases?id=10152026a |
| "Xcode 27.1 includes Swift 6.4 and SDKs for iOS 27.1, iPadOS 27, tvOS 27, watchOS 27, macOS 27, and visionOS 27 ... Xcode 27.1 requires a Mac running macOS Tahoe 26.6 or later" | Apple | https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes |
| Device shipped October 23, 2026 with iOS 27.1 | Apple | https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/ |
| The new APIs are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo"; Apple recommends "gating iOS 27.1 APIs behind availability checks" | Apple | https://developer.apple.com/forums/thread/847644 |
| Mac Catalyst builds using iOS 27.1-only APIs produce compile errors (185924957); workaround `#if !targetEnvironment(macCatalyst)` | Apple | https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes |
| Xcode 27.2 beta did not include Duo support despite the higher number | third-party, unverified | reported by ecorpit.com |
| `#available(iOS 27.1, *)` alone does not compile under Xcode 27.0 because the symbols are absent; `#if canImport(SwiftUI, _version: 8.0.85)` suggested | third-party, unverified | blakecrosley.com |

Two iOS 27 SDK requirements that become launch-blocking on Duo:

- "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store
  submission" (TN3192, cross-referencing TN3208,
  https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key).
- The scene lifecycle: Apple's UIKit Q&A reportedly said "Xcode 27 requires
  the scene lifecycle, so migrate first" (Gubarenko Q20, third-party summary of
  Apple answers). React Native 0.88.0-rc.0 failed to launch on the Duo
  simulator with "Application failed to launch: UIScene life cycle is required
  for apps built with this SDK"; fixed in RN 0.88
  (https://github.com/react/react-native/issues/58606, third-party).

## 4. Step 1: run Apple's App Resizability skill

From https://developer.apple.com/iphone-duo/prepare/: in Xcode 27.1 ask the
coding assistant to "get my app ready for iPhone Duo"; for other agents, run
`xcrun agent skills export` in Terminal. Apple: "The skill finds most issues,
but not all of them."

The skill introduced at WWDC26 as the "Modernize your UIKit app" skill is
renamed App Resizability in Xcode 27.1 and covers SwiftUI and iPhone Duo
(Tech Talk 111461).

Apple publishes no sample project for iPhone Duo; the App Resizability skill is
its only runnable artifact (https://developer.apple.com/iphone-duo/).

## 5. Step 2: fix common patterns (the grep list)

From https://developer.apple.com/iphone-duo/prepare/, with the scanner rule
that approximates each row:

| Anti-pattern (search for) | Apple's replacement | Scanner rule |
|---|---|---|
| `UIScreen.main.bounds` | `view.bounds`, `window.bounds`; SwiftUI `GeometryReader` or `onGeometryChange` | DUO-001 |
| Reading size once at launch or in `viewIsAppearing` | Re-read in `layoutSubviews` / `viewDidLayoutSubviews`; use `viewWillTransition(to:with:)` for work that must run on resize, "because a fold can resize your app in the middle of a session" | DUO-023 (heuristic), partly DUO-001 |
| `UIScreen.main.scale` | `traitCollection.displayScale` / `@Environment(\.displayScale)` | DUO-002 |
| `UIWindow(frame: UIScreen.main.bounds)` | `UIWindow(windowScene:)` | DUO-003 |
| Storing a `UIScreen` | "Don't store a `UIScreen`"; access via `view.window?.windowScene?.screen` | not detected; read the code |
| Layout from `UIDevice.current.orientation`, `statusBarOrientation`, `interfaceOrientation`, `windowScene.effectiveGeometry.interfaceOrientation` | Compare available width vs height; use size classes | DUO-005 |
| `userInterfaceIdiom == .phone` / `== .pad` | "Don't choose a layout by idiom" | DUO-004 |
| `horizontalSizeClass == .regular` treated as iPad | "Don't treat 'regular width' as 'iPad.'" ("an iPhone app can have any combination of size classes") | not detected; read the code |
| `bounds.height == 844`-style checks | "Remove checks for specific device sizes" | DUO-011 (heuristic), DUO-012 (heuristic) |
| `.scaleAspectFill` / `.aspectRatio(contentMode: .fill)` hero media | "Check full-bleed media ... choose fill or fit based on size class or aspect ratio, or set a focal point" | DUO-013 (heuristic) |

Tech Talk 111461 shows the code form of each fix, including the safe-area
anti-pattern `view.bounds.width - view.safeAreaInsets.left * 2` replaced by
`view.bounds.inset(by: view.safeAreaInsets).width` (DUO-022), and warns that
`UIScreen.main` is "ambiguous on two-display devices and will be deprecated in
a future release".

## 6. Step 3: test resizing

From https://developer.apple.com/iphone-duo/prepare/, in Apple's order:

1. The iOS Resizable simulator in Device Hub.
2. iPhone Mirroring on macOS 27, "resized to extreme sizes in both directions".
3. The iPhone Duo simulator in Xcode 27.1, "the best way to test the full
   native experience".

Device Hub controls (https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub):
"To close the iPhone Duo, click the Closed button on the right of the Rotate
Right button. / To partially open the iPhone Duo, click the Partially Open
button in the middle of the three device pose buttons. / To fully open the
iPhone Duo, click the Open button on the far right. — To fold the device to
any angle, hold the Option key while dragging the slider that appears below
the bezel."

The Group Lab cautions that "Device Hub's Resizable iPhone / iPhone Mirroring
behavior is an approximation, but iPhone Duo-specific behaviors need
dedicated testing" (https://developer.apple.com/forums/thread/847644). There
is no supported way to set the pose programmatically; `xcrun simctl help`
lists no fold subcommand and the forum request has no Apple reply
(https://developer.apple.com/forums/thread/847883). See `duo-test`.

## 7. "Go further": the App Store half

From https://developer.apple.com/iphone-duo/prepare/: submit iPhone Duo
screenshots to earn the badge, use the new App Store Connect preview tool, and
nominate for featuring noting in "Helpful Details" that the app "is optimized
for iPhone Duo, including support for all device poses".

From https://developer.apple.com/news/?id=kkphp5qo (October 5, 2026): "If you
submit iPhone Duo screenshots, your App Store product page displays a badge
indicating the app is optimized for iPhone Duo"; "Starting April 2027, any apps
or games submitted will need to include screenshots for iPhone Duo".

From https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications:
outer display 1398x2034 (portrait) / 2034x1398 (landscape); inner display
2007x2853 / 2853x2007; "Starting in April 2027, screenshots will be required
for any app using the iOS 27.1 SDK or later."

The two Apple pages differ on scope ("any apps or games submitted" versus "any
app using the iOS 27.1 SDK or later"); a forum question has no Apple reply
(https://developer.apple.com/forums/thread/851106) and the Upcoming
Requirements page did not list the item as of 2026-10-26
(https://developer.apple.com/news/upcoming-requirements/). Whether both
screenshot sets (inner and outer) will be required is unstated. See
`duo-ship`.

## 8. Apple's audit checklist and priority order

Technology Overview checklist for what to look at while testing
(https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

> "Confirm your views resize well in each supported orientation and pose. /
> Inspect how the system presents your app's navigation bars, toolbars, and
> tab bars vertically on the side of the display. / Identify any views, sheets,
> or popovers that position awkwardly when you fold or open iPhone Duo. /
> Identify elements or controls in your views that appear in the fold, and are
> difficult to see or interact with"

Its recommendations, which read as a priority order:

> "Prefer system-provided layouts and containers, such as split views, tab
> bars, arrangement views, and navigation stacks ... Size your views relative
> to their container rather than to fixed iPhone dimensions ... Make layout
> calculations based on your scene or containing view's bounds rather than
> screen dimensions ... Adopt Auto Layout in UIKit ... Use automatic trait
> tracking to observe `UITraitCollection.horizontalSizeClass` and
> `UITraitCollection.verticalSizeClass` changes ... Don't use
> `UIDevice.userInterfaceIdiom` or `UIInterfaceOrientation` for layout
> decisions in your UIKit app"

Tech Talk 111463's closing audit adds: "Audit your app's centered layouts.
Consider a two-column layout or a displacement pattern. Identify your
highest-priority manually laid-out controls and adopt the reserved regions
API" (https://developer.apple.com/videos/play/tech-talks/111463/).

## 9. What Apple has not published

Say these are gaps rather than filling them:

- Point dimensions of either display. Apple gives pixels only: inner
  1878x2670 at 430 ppi, outer 1398x2034 at 460 ppi
  (https://www.apple.com/iphone-duo/specs/). The 466x678 pt and 669x951 pt
  figures are third-party simulator measurements.
- A pose API, a Duo idiom, a Duo Info.plist key, a `simctl` fold command, a
  sample project. None exist ("There's no single pose API",
  https://developer.apple.com/forums/thread/847644).
- The `xcodebuild -destination name=` string for the Duo simulator; confirm
  with `xcrun simctl list devicetypes`.
- Whether the April 2027 screenshot rule applies to every submission or only
  to iOS 27.1 SDK builds, and whether both display sets are required.
- Public iOS 27.1 release notes (the URL returned 404 at research time).
