Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# iPhone Duo release checklist

Walk this with the user item by item. For each item record one of: done, not applicable, blocked (with the reason). Every item names its Apple source or the duo-audit rule that detects it; items marked (inferred) are the research team's recommendation, not Apple's rule.

## A. Toolchain

- [ ] A1. The archive that goes to App Store Connect is built with Xcode 27.1 (27A9275) on macOS Tahoe 26.6 or later. Check the CI config, not only the local machine. ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Software Releases](https://developer.apple.com/news/releases?id=10152026a))
- [ ] A2. The archive step is not on the Xcode 27.2 beta, which lacked Duo support (third-party, unverified: [ecorpit](https://ecorpit.com/iphone-duo-sdk-new-apis-xcode-27-1-developer-guide-2026/)).
- [ ] A3. The team has decided which SDK tier to ship (iOS 27 SDK fills most of the inner display; iOS 27.1 SDK is edge-to-edge with vertical bars) and accepts the consequence. ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/))
- [ ] A4. duo-audit DUO-019 (project not upgraded to 27.1) is clear: `python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>`.
- [ ] A5. (Optional, third-party) SDK stamp verified: `otool -l <binary> | grep -A4 LC_BUILD_VERSION` shows `sdk 27.1` ([blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)).
- [ ] A6. If a Mac Catalyst target shares the code, iOS 27.1-only API is wrapped in `#if !targetEnvironment(macCatalyst)` (Apple known issue 185924957; DUO-020).

## B. Submission blockers in the binary

- [ ] B1. Launch screen present: `UILaunchScreen` dictionary or `UILaunchStoryboardName` in Info.plist, or `INFOPLIST_KEY_UILaunchScreen_Generation`. "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission." ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key); DUO-010)
- [ ] B2. Scene lifecycle adopted: `UIApplicationSceneManifest` in Info.plist, a `UIWindowSceneDelegate`, window created with `UIWindow(windowScene:)` (third-party evidence: [react-native #58606](https://github.com/react/react-native/issues/58606), [Gubarenko Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums); DUO-009; Expo: `expo-build-properties` → `"ios": {"enableSceneSupport": true}`)
- [ ] B3. `UIRequiresFullScreen` reviewed: it no longer opts out of resizing and only yields discrete resizing on iOS 27 SDK builds; TN3192's checklist says remove it, support all orientations, provide a launch screen. ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key); DUO-008)
- [ ] B4. Nothing Duo-specific added to `UIRequiredDeviceCapabilities`: "apps can't require iPhone Duo-specific capabilities" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- [ ] B5. No Info.plist key added to "opt out" of the Duo tier; none exists (third-party summary of Apple's Q&A, [Gubarenko Q23](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).

## C. Verify what the screenshots will show

Apple's own audit list, verbatim ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):

- [ ] C1. "Confirm your views resize well in each supported orientation and pose."
- [ ] C2. "Inspect how the system presents your app's navigation bars, toolbars, and tab bars vertically on the side of the display."
- [ ] C3. "Identify any views, sheets, or popovers that position awkwardly when you fold or open iPhone Duo."
- [ ] C4. "Identify elements or controls in your views that appear in the fold, and are difficult to see or interact with."
- [ ] C5. If shipping the iOS 27.1 SDK: "Before shipping with this SDK, confirm your content adapts to the vertical bars." ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)) Route defects to duo-bars.
- [ ] C6. Tested in Apple's three named environments: iOS Resizable simulator in Device Hub; iPhone Mirroring on macOS 27 "resized to extreme sizes in both directions"; the iPhone Duo simulator in Xcode 27.1 ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)). duo-test owns the manual pass.
- [ ] C7. Dynamic Type checked; text reflows rather than being held at the largest standard size (App Store Connect "Larger Text" criteria; [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- [ ] C8. Camera features, StandBy, widgets and app extensions checked on hardware or a regular iOS 27.1 simulator, because the Duo simulator cannot run them ("StandBy is unavailable in the iPhone Duo Simulator runtime. (187708663)"; "Running and debugging most app extensions is unavailable in the iPhone Duo Simulator runtime. (187708767)"; "Simulator has no camera, so test on a device before shipping") ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Registering a camera capture accessory](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)).

## D. Screenshots

- [ ] D1. Sets chosen. At minimum outer portrait 1398×2034 and inner portrait 2007×2853 (inferred safe plan; Apple has not said whether one or both displays will be required). Landscape variants 2034×1398 and 2853×2007 if the app's story needs them. ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications))
- [ ] D2. Captured from the running app in the iPhone Duo simulator (or device), pose set with Device Hub's Closed / Partially Open / Open buttons ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)); not mockups (Guideline 2.3.3 as paraphrased in [Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106)).
- [ ] D3. Waited after boot; no black frames ("Screenshots and recordings in iPhone Duo might be black for up to a few minutes after booting the device. (187146039)", [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)).
- [ ] D4. Each file validated: exact pixel size; `.png`/`.jpeg`/`.jpg`; no alpha; at most 10 per device size ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
- [ ] D5. Screenshots show the layout the shipped SDK tier actually produces (vertical bars for a 27.1 SDK build; letterboxing is what users see for a 26 SDK build, per third-party launch-week reports).
- [ ] D6. Localized sets planned where the app is localized (the count limit is per device size; previews are per device size and language).

## E. App previews (optional)

- [ ] E1. Upload at 886×1920 (portrait) or 1920×886 (landscape); 15–30 s; up to 500 MB; up to 30 fps; H.264 or ProRes 422; up to three per device size and language ([ASC app preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications)).
- [ ] E2. Ignore the "19.5:9" label on the Duo row (Apple page error); use the pixel figures.
- [ ] E3. Allow up to 24 hours of processing before release.

## F. App Store Connect metadata

- [ ] F1. Duo screenshot sets uploaded in the Duo slots; the badge follows ("When you submit iPhone Duo screenshots in App Store Connect, your App Store product page will display a badge ...", [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). Read the slot labels in ASC; how inner versus outer slots are labelled was not captured.
- [ ] F2. Product page checked in the new ASC preview tool ([Apple Developer News](https://developer.apple.com/news/?id=kkphp5qo)).
- [ ] F3. Featuring nomination submitted only if true, with "Helpful Details" stating the app "is optimized for iPhone Duo, including support for all device poses" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)). duo-design's rubric decides whether that claim holds.
- [ ] F4. App icon unchanged: no Duo-specific guidance; 1024×1024 px ([HIG App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)).
- [ ] F5. Biometric copy in release notes and onboarding handles Touch ID (Duo has no Face ID; [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)).

## G. Automation

- [ ] G1. fastlane `deliver`/`snapshot` and ASC API uploads of Duo sets are either done manually or use display-type values the team has read from the live API; none are documented (gap). Do not guess enum names.
- [ ] G2. CI runs tests on the Duo simulator if available; the exact `xcodebuild -destination name=` string is unrecorded, confirm with `xcrun simctl list devicetypes | grep -i duo` (inferred; device type `com.apple.CoreSimulator.SimDeviceType.iPhone-Duo` is third-party).
- [ ] G3. TestFlight build includes at least one tester with a physical Duo if possible; Apple warns simulator-functional interactions "may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## H. After release

- [ ] H1. Own analytics properties logged for Duo adoption, because App Store Connect analytics has no Duo device value ([ASC App analytics filters and dimensions](https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/)); see duo-backend.
- [ ] H2. April 2027 item on the roadmap: both portrait sets uploaded before April 2027 under either reading of the rule (inferred); re-check [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) and `references/april-2027.md`.
- [ ] H3. Someone watches the two Apple pages for a scope clarification ([news post](https://developer.apple.com/news/?id=kkphp5qo); [specs page](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)) and [forum thread 851106](https://developer.apple.com/forums/thread/851106).
