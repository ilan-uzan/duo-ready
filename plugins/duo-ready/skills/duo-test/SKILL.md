---
name: duo-test
description: >-
  Test an iOS app on iPhone Duo without owning one: drive the iPhone Duo
  simulator through Xcode 27.1 Device Hub (Closed / Partially Open / Open,
  Option-drag hinge slider, Rotate), run Apple's audit checklist in every pose,
  capture per-display simulator screenshots at App Store Connect sizes, build a
  CI matrix, and know what the simulator cannot test. Use it whenever someone
  asks how to test or QA the "new foldable iPhone", "how do I fold the
  simulator", "my screenshots come out black", "can XCUITest open the phone",
  "add the Duo simulator to GitHub Actions / Xcode Cloud / fastlane", "I don't
  have the device, how do I check my layout", "App Store wants new
  screenshots", or "which Xcode do I need". Also use it before any other
  duo-ready skill declares a fix verified.
---

# duo-test: verify an app on iPhone Duo with the tools Apple ships

## What Apple actually says

- Apple names three test environments, in this order: the iOS Resizable simulator in Device Hub; iPhone Mirroring on macOS 27 "resized to extreme sizes in both directions"; and the iPhone Duo simulator in Xcode 27.1, "the best way to test the full native experience" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Device Hub folds the simulator: "To close the iPhone Duo, click the Closed button on the right of the Rotate Right button. / To partially open the iPhone Duo, click the Partially Open button in the middle of the three device pose buttons. / To fully open the iPhone Duo, click the Open button on the far right. — To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel" ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)).
- There is no supported way to set the pose from a script or a test: `xcrun simctl help` lists no fold or posture subcommand, `XCUIDevice` documents only buttons, orientation and Siri, and the forum request for one has no Apple reply ([Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883); [XCUIDevice](https://developer.apple.com/documentation/xcuiautomation/xcuidevice)).
- The simulator is not the device: "Device Hub's Resizable iPhone / iPhone Mirroring behavior is an approximation, but iPhone Duo-specific behaviors need dedicated testing", and "Interactions that look fine in the simulator may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Known simulator issues are listed by ID in the Xcode 27.1 and 27.2 RC release notes (slow first launch, StandBy unavailable, most app extensions unavailable, black screenshots after boot, accessibility tools in Device Hub, modifier keys); see the table in `references/device-hub-and-simulator.md` ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)).

Everything about `simctl` identifiers, display names and point sizes in this skill is third-party (unverified by Apple) and is labelled as such. Do not promote it to fact when talking to the user.

## Workflow

### 1. Look at the project before advising

Ask for, or open, the user's project. You need: the Xcode version they build with, the SDK the binary links against, whether UI tests or snapshot tests exist, and where screenshots are produced today. When a project path is available, run the audit first so the test pass has a list of suspects to confirm:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

Its findings (`UIScreen.main`, orientation and idiom checks, custom bars, symmetric inset math) tell you which screens to watch most closely in step 4.

### 2. Confirm the toolchain

- Duo support requires Xcode 27.1, build 27A9275, which "includes Swift 6.4 and SDKs for iOS 27.1" and "requires a Mac running macOS Tahoe 26.6 or later" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Apple Software Releases](https://developer.apple.com/news/releases?id=10152026a)). A higher Xcode number is not enough: the Xcode 27.2 beta did not include Duo support (third-party, unverified).
- The inner-display behaviour depends on the SDK the binary links against, not the deployment target: iOS 26 SDK apps run centered with empty space, iOS 27 SDK apps fill most of the inner display but avoid the status bar, and only iOS 27.1 SDK apps use the full display with vertical bars ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). Check the stamp with `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, expecting `sdk 27.1` (third-party, unverified; one developer's `swiftc -sdk` build was stamped 27.0 by mistake).
- If the project has a Mac Catalyst target, expect two Apple-documented problems: iOS 27.1-only APIs produce compile errors in Catalyst builds (185924957, workaround `#if !targetEnvironment(macCatalyst)`), and targeting iOS 27.1 shows no Catalyst run destination (187046347, workaround: add a Mac Catalyst 27.0 minimum deployment) ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

### 3. Get the Duo simulator running

- In Xcode, add it from Device Hub ("+" → iPhone → iPhone Duo) or re-download the iOS 27.1 runtime via Settings → Components → Update if it is missing (third-party, unverified; [Apple Developer Forums 847137](https://developer.apple.com/forums/thread/847137) is the thread).
- From the command line (all identifiers third-party, unverified; confirm with `xcrun simctl list devicetypes | grep -i duo` and `xcrun simctl list runtimes`):
  - download: `xcodebuild -downloadPlatform iOS` (about 7.85 GB; one developer retried with `-buildVersion 24A94401`)
  - create: `xcrun simctl create "Duo-27.1" com.apple.CoreSimulator.SimDeviceType.iPhone-Duo com.apple.CoreSimulator.SimRuntime.iOS-27-1`
- Budget time: "Initial Simulator launch can take several minutes. (187708500)" and "Screenshots and recordings in iPhone Duo might be black for up to a few minutes after booting the device. (187146039)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)).
- Previews: Xcode 27.1 added "a Display group for previewing content on a device's alternative display. (182598534)" to the canvas overrides picker, which lets SwiftUI previews show the inner display without booting the simulator ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

### 4. Run Apple's audit checklist in every pose

Use the Device Hub buttons (Closed, Partially Open, Open), the Option-drag slider for intermediate angles, and Rotate. In each pose work through Apple's own list ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):

1. "Confirm your views resize well in each supported orientation and pose."
2. "Inspect how the system presents your app's navigation bars, toolbars, and tab bars vertically on the side of the display."
3. "Identify any views, sheets, or popovers that position awkwardly when you fold or open iPhone Duo."
4. "Identify elements or controls in your views that appear in the fold, and are difficult to see or interact with."

Then run the longer manual pass in `references/manual-test-pass.md` (launch outer then move inner; fold and unfold mid-task and pause at angles; rotate in both states; Split View by dragging the home indicator; sheets, alerts, menus, keyboard; scroll and selection survive; background-then-change-pose). Record every defect with the pose, display, and size classes, and route it to the skill that fixes it (see Related skills).

What to expect while you look: the outer display is compact width / regular height in portrait and compact / compact in landscape; the inner display is regular / regular in either rotation ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)). The inner display "doesn't honor supported interface orientations", so a portrait-only app will still land in a wide layout there ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

### 5. Capture App Store Connect screenshots

App Store Connect accepts outer display 1398×2034 (portrait) / 2034×1398 (landscape) and inner display 2007×2853 / 2853×2007 ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). Third-party reports (unverified) say `xcrun simctl io <udid> screenshot --type=png --display=primary` captures the outer display and `--display=primary-1` the inner one, producing exactly those pixel sizes; a different report saw `--display=1` (cover) and `--display=3` (inner), and a plain `screenshot` with no `--display` shows the inner display, black when folded. Because the identifiers conflict, always run `xcrun simctl io <udid> enumerate` and read the list before trusting a file.

`scripts/duo_screenshots.sh` does this defensively: it finds or creates a Duo simulator, boots it, prints the `enumerate` output, captures `outer-portrait-1398x2034.png` and `inner-portrait-2007x2853.png`, and prints each file's pixel size with `sips -g pixelWidth -g pixelHeight` so a mismatch is visible. Run `scripts/duo_screenshots.sh --help` for options. Hand the results to duo-ship for upload; remind the user that screenshots "must show the app in use" (App Review 2.3.3 as paraphrased on the forums, [Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106)) and that no `simctl` flag changes the pose, so the inner-display capture needs the device opened in Device Hub first.

### 6. Decide what goes into CI

Nothing from Apple, Xcode Cloud, fastlane, Bitrise or Codemagic documents a Duo destination (third-party searches, unverified). Offer the user the inferred matrix in `references/ci.md`, labelled as inferred:

- a Duo simulator job for unit and UI tests; the exact `xcodebuild -destination 'platform=iOS Simulator,name=iPhone Duo,OS=27.1'` string is unconfirmed, so tell the user to confirm the name with `xcrun simctl list devicetypes | grep -i duo` before committing it;
- the default (closed) pose on the Duo simulator plus a Resizable iPhone simulator sized to the inner-display point sizes for regular-width coverage, because tests cannot fold;
- snapshot baselines at @3x for 466×678, 669×951, 951×669 and a Split View half-width variant (all point sizes third-party, unverified);
- widgets, Live Activities and StandBy on a regular iOS 27.1 simulator and hardware, since StandBy and most app extensions are unavailable in the Duo runtime ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes));
- community fold automation (duoctl, serve-sim, hinge) only as unsupported, local convenience; never as a CI dependency.

### 7. Say what still needs hardware

The simulator cannot exercise camera transitions, capture accessories, reachability, haptics, performance, memory or thermals (third-party, unverified), nor StandBy (Apple, 187708663). Apple's own camera guidance is blunt: "Simulator has no camera, so test on a device before shipping" ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)). Hinge "Update rate and precision are system policy, so don't depend on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)), so angle-driven effects also need a device. List these explicitly in your answer so the user can plan a device session; Apple's in-person workshops offer devices but "Availability isn't guaranteed" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## Common mistakes

- Treating the Resizable iPhone simulator or iPhone Mirroring as a Duo test. Apple calls them an approximation; vertical bars, reserved regions and scene accessories need the Duo simulator ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Reading a black screenshot as an app bug. For a few minutes after boot the Duo simulator can return black screenshots and recordings (187146039, [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)); a plain screenshot of a folded device is also black because it captures the inactive inner display (third-party, unverified).
- Trying to fold from XCUITest or `simctl`. There is no API; XCUITest runs on the Duo simulator but cannot change posture, and one forum report says the accessibility snapshot "reports stale frames during live scene resize" (third-party, unverified; [Apple Forums activity 1664080](https://developer.apple.com/forums/activities/1664080)).
- Debugging extensions or StandBy in the Duo runtime. Both are unavailable there (187708767, 187708663, [Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)); use a regular iOS 27.1 simulator or hardware.
- Running VoiceOver or Accessibility Inspector against the Duo simulator inside Device Hub and concluding the app is inaccessible: those tools "cannot convey screen content on an iPhone Duo within Device Hub" (187148389, [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)).
- Forgetting the background-then-change-pose case. A Flutter app showed a distorted App Switcher preview only after the pose changed while backgrounded (third-party, unverified; [flutter issue #193078](https://github.com/flutter/flutter/issues/193078)); add it to every manual pass.
- Assuming a `CameraCaptureAccessory` that appears in the simulator will appear on hardware. In Xcode 27.1 the simulator showed it "without an active camera capture session" (190155353, listed as fixed in the 27.2 RC notes); the device requires an active session ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)).
- Testing with the wrong SDK stamp and reporting "it already fills the inner display". Only an iOS 27.1 SDK build moves bars vertically; confirm `sdk 27.1` with `otool` first (third-party check, Apple tiers).

## When to read the references

- `references/device-hub-and-simulator.md`: Apple's three environments verbatim, the Device Hub controls, Previews Display override, the full known-issue table with IDs, every `simctl` identifier and command (labelled third-party), the conflicting display IDs, what the simulator cannot test, and why there is no pose automation.
- `references/manual-test-pass.md`: the pose-by-pose checklist with what to look for at each step, which Apple rule each check enforces, and the hardware-only list.
- `references/ci.md`: the inferred CI matrix, the unconfirmed destination string and how to confirm it, runtime pre-warming, snapshot sizes, extension and StandBy coverage, the fastlane and App Store Connect API gaps.

## Related skills

- duo-audit: run the scanner before testing so you know which screens to watch.
- duo-layout: fixes for views that do not resize, content in the fold, grids with odd column counts.
- duo-bars: fixes for bars that stay horizontal, empty side rails, items that overflow.
- duo-scenes: fold-as-trait-change, state that does not survive, Split View, scene accessories.
- duo-camera: everything the simulator cannot show about cameras.
- duo-ship: uploading the screenshots this skill captures, the April 2027 rule and the badge.
- duo-design: the HIG rubric to score what you see in each pose.
- duo-crossplatform: React Native, Flutter, Capacitor and Unity specifics seen during the pass.
