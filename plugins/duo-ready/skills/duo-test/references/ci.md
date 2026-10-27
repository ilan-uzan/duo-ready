Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# CI for iPhone Duo: what is documented, what is inferred

Contents
1. The state of vendor documentation
2. The inferred CI matrix
3. The xcodebuild destination (unconfirmed)
4. Runtime provisioning and boot time
5. Screenshot job
6. Snapshot baselines (inferred, third-party sizes)
7. Extensions, widgets, Live Activities, StandBy
8. UI tests on the Duo simulator
9. Community fold automation: unsupported
10. SDK stamp and Catalyst checks
11. Xcode Cloud, fastlane, App Store Connect API gaps

Labelling: Apple statements carry an Apple link. "(third-party, unverified)" marks developer reports. "(inferred)" marks this repo's reasoning. Most of this file is inferred, because Apple has published nothing about Duo in CI; say so to the user.

## 1. The state of vendor documentation

No Xcode Cloud, fastlane, Bitrise or Codemagic documentation mentioned iPhone Duo at research time (third-party searches, unverified). The Xcode 27.1 release notes do not mention Device Hub, `simctl`, `xcodebuild` or Xcode Cloud in connection with Duo ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)). The only Apple-adjacent Xcode Cloud material is a pre-Duo forum answer that a Test action's "Destinations" section selects which simulators run ([Apple Developer Forums 731974](https://developer.apple.com/forums/thread/731974)).

So every row below is a proposal. Present it as "a defensible matrix today", not as Apple's recommendation.

## 2. The inferred CI matrix

| Job (inferred) | Destination | What it covers | Why |
|---|---|---|---|
| Unit + UI tests on Duo | Duo simulator, default pose (closed, outer display) | compact-width layout, vertical bars on the outer display, launch under the iOS 27.1 SDK | the only automated way to see Duo-specific bars; the pose cannot be changed by tests (see 8) |
| Regular-width coverage | Resizable iPhone simulator sized to 669×951 and 951×669 pt (sizes third-party, unverified) | regular / regular layouts the inner display produces | Apple lists the Resizable simulator first among its test environments ([Three steps](https://developer.apple.com/iphone-duo/prepare/)); it approximates the inner display without a pose API |
| Previews | SwiftUI Previews with the Display override (182598534) | inner-display rendering during development | [Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes) |
| Snapshot baselines | @3x at 466×678, 669×951, 951×669 and a Split View half-width variant (sizes third-party, unverified) | regressions in both size-class layouts | see 6 |
| Extensions and StandBy | regular iOS 27.1 simulator and hardware | widgets, Live Activities, StandBy | unavailable in the Duo runtime ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)) |
| App Store screenshots | Duo simulator, opened by hand in Device Hub, then `scripts/duo_screenshots.sh` | 1398×2034 and 2007×2853 PNGs | sizes from [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications); display IDs third-party |
| Manual pass | Device Hub, human | fold transitions, Split View, sheets, keyboard | no automation exists (see 8 and 9) |

## 3. The xcodebuild destination (unconfirmed)

A plausible destination is:

```
xcodebuild test -scheme <Scheme> \
  -destination 'platform=iOS Simulator,name=iPhone Duo,OS=27.1'
```

The `name=` string is not recorded in any source the report reviewed; it is inferred from the device type id `com.apple.CoreSimulator.SimDeviceType.iPhone-Duo` (third-party, unverified). Before committing it, run on a machine with Xcode 27.1:

```sh
xcrun simctl list devicetypes | grep -i duo
xcrun simctl list runtimes
xcrun simctl list devices available | grep -i duo
```

and copy the name exactly as printed. If you create the device yourself with `simctl create "Duo-27.1" ...`, you can target it by that name or by UDID (`-destination 'platform=iOS Simulator,id=<udid>'`), which sidesteps the naming question (inferred).

## 4. Runtime provisioning and boot time

- Download: `xcodebuild -downloadPlatform iOS`; one developer retried with `-buildVersion 24A94401` and reports the runtime at about 7.85 GB (third-party, unverified). Cache the runtime on ephemeral runners or the download dominates the job (inferred).
- "Initial Simulator launch can take several minutes. (187708500)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)). Boot the device in a setup step with `xcrun simctl boot <udid>` and wait with `xcrun simctl bootstatus <udid> -b` before the test step, and raise the job timeout (inferred; `bootstatus` is a standard `simctl` subcommand, not Duo-specific).
- A Duo simulator was heavy enough to make an M1 Mac mini nearly unresponsive for one developer (third-party, unverified). Do not run it alongside other simulators on small runners.

## 5. Screenshot job

- Apple's sizes: outer 1398×2034 (portrait) / 2034×1398 (landscape); inner 2007×2853 / 2853×2007; up to 10 per device size; `.jpeg`/`.jpg`/`.png`; no alpha ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
- The device must be opened in Device Hub by hand before the inner display shows content. There is no `simctl` pose flag ([Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883)), so a fully unattended inner-display screenshot job is not possible with supported tools today. Run the outer capture unattended if you want, and the inner capture as a semi-manual step (inferred).
- Wait after boot: screenshots "might be black for up to a few minutes after booting the device. (187146039)" ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). `scripts/duo_screenshots.sh` prints each PNG's pixel size but cannot tell a black frame from a real one; look at the files.
- Display identifiers conflict between third-party reports (`primary` / `primary-1` versus `1` / `3`); the script prints `xcrun simctl io <udid> enumerate` so the operator can confirm, and accepts `--outer-display` / `--inner-display` overrides.
- Screenshots must show the real app; a forum poster paraphrased App Review 2.3.3 to that effect ([Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106)). Do not generate Duo screenshots by compositing other devices' captures.

## 6. Snapshot baselines (inferred, third-party sizes)

Apple publishes pixel sizes only; it has not published point dimensions for either display ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/); [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) contains no numeric dimensions). The point sizes below are simulator measurements (third-party, unverified) whose arithmetic matches Apple's App Store Connect pixel sizes at @3x (inferred: 466×3 = 1398, 678×3 = 2034, 669×3 = 2007, 951×3 = 2853).

| Baseline (inferred) | Points (third-party, unverified) | Pixels @3x | Size classes (Apple, [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)) |
|---|---|---|---|
| Outer portrait | 466×678 | 1398×2034 | compact / regular |
| Outer landscape | 678×466 | 2034×1398 | compact / compact |
| Inner portrait | 669×951 | 2007×2853 | regular / regular |
| Inner landscape | 951×669 | 2853×2007 | regular / regular |
| Split View half | not published by Apple | — | Apple: Split View is "a 50/50 layout" ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)); exact point sizes are a gap |

Snapshot libraries that render a view at a fixed size with injected traits can produce the first four without a Duo simulator (inferred). They will not reproduce vertical bars, the 84 pt side inset (third-party, unverified) or reserved regions; those need the Duo simulator. An older third-party figure of 626×890 pt for the inner display predates the simulator and is superseded (third-party, unverified).

## 7. Extensions, widgets, Live Activities, StandBy

- "StandBy is unavailable in the iPhone Duo Simulator runtime. (187708663)" and "Running and debugging most app extensions is unavailable in the iPhone Duo Simulator runtime. (187708767)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
- Widget families on Duo are the standard ones (`systemSmall`, `systemMedium`, `systemLarge`, `systemExtraLargePortrait`, `accessoryCircular`, `accessoryRectangular`, `accessoryInline`), and Live Activities "must implement compactLeading, compactTrailing, minimal, expanded, and Lock Screen presentations" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Test them on a regular iOS 27.1 simulator in CI and on hardware for the outer display's vertical Dynamic Island (inferred).

## 8. UI tests on the Duo simulator

- XCUITest runs on the Duo simulator but cannot change posture (third-party, unverified). `XCUIDevice` documents buttons, orientation and Siri only ([XCUIDevice](https://developer.apple.com/documentation/xcuiautomation/xcuidevice)).
- A SwiftUI Q&A thread title reports "XCUITest accessibility snapshot reports stale frames during live scene resize" ([Apple Forums activity 1664080](https://developer.apple.com/forums/activities/1664080)); the thread body was not fetched. Avoid asserting frames during an animated resize; wait for layout to settle (inferred).
- One field report had a UI test tap the wrong key because the keyboard covered the bottom tab rail on the outer display (third-party, unverified). Expect existing UI tests that assume a bottom tab bar to need updating for the vertical rail.
- Modifier keys "might stop working" after switching displays in the simulator (189465196, [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)); keyboard-shortcut tests after a pose change are unreliable.
- Tests that read `UIScreen.main.bounds` are testing the wrong thing on Duo; Apple calls it "ambiguous on two-display devices" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

## 9. Community fold automation: unsupported

skarol/duoctl, EvanBacon/serve-sim (`fold <angle> -d <udid>`, `xcrun devicectl device motion hinge-angle --device <udid>`), artemnovichkov/hinge and accessibility-`AXPress` scripts drive Device Hub's UI or undocumented mechanisms (third-party, unsupported). They need a logged-in GUI session and can break with any Xcode update. If a team wants fold transitions in CI, the honest options are: run them locally with one of these tools and treat the results as exploratory, or do the manual pass (inferred). Do not add them as a required CI step.

## 10. SDK stamp and Catalyst checks

- Add a build-verification step (third-party, unverified check): `otool -l <App.app/App> | grep -A4 LC_BUILD_VERSION` must show `sdk 27.1`. Only the iOS 27.1 SDK gives the full inner display with vertical bars ([Three steps](https://developer.apple.com/iphone-duo/prepare/)); a 27.0-stamped build will pass every test and still ship the wrong tier.
- The Xcode 27.2 beta did not include Duo support (third-party, unverified); pin CI to Xcode 27.1 (27A9275) until a later Xcode's release notes say otherwise.
- Catalyst jobs: iOS 27.1-only APIs cause compile errors in Mac Catalyst builds (185924957; workaround `#if !targetEnvironment(macCatalyst)`), and an iOS 27.1 target shows no Catalyst run destination (187046347; workaround: add a Mac Catalyst 27.0 minimum deployment) ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
- Launch screen: "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)); a CI archive step that validates the upload will surface this before App Store Connect does (inferred).

## 11. Xcode Cloud, fastlane, App Store Connect API gaps

- Xcode Cloud: Duo is a standard simulator device type in Xcode 27.1, so it should become selectable in a Test action's Destinations once Xcode Cloud offers the 27.1 toolchain; no Apple document confirms this (inferred).
- fastlane `snapshot` and `deliver`: documentation has no Duo mention; the `screenshot_display_type` values and the App Store Connect API `ScreenshotDisplayType` enum values for Duo are undocumented (third-party searches, unverified). Until they appear, upload Duo screenshots through App Store Connect's web UI, where the new preview tool shows how they will look ([Apple Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo)).
- TestFlight: nothing Duo-specific exists; a Duo build is an iOS build. Include at least one physical Duo among internal testers given Apple's hardware caution (inferred; [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Deadline that makes all of this matter: "Starting April 2027, any apps or games submitted will need to include screenshots for iPhone Duo" ([Apple Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo)), while the specs page scopes it to "any app using the iOS 27.1 SDK or later" ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). The two pages conflict and Apple has not resolved it; duo-ship owns that discussion.
