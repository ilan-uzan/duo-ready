Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Device Hub and the iPhone Duo simulator

Contents
1. Apple's three test environments
2. Device Hub pose controls (verbatim)
3. Previews "Display" override
4. Toolchain requirements and the SDK stamp
5. Getting the simulator
6. Command line: identifiers and commands (third-party)
7. Per-display screenshots and the conflicting display IDs (third-party)
8. Known issues with IDs (Apple release notes)
9. What the simulator cannot test
10. No supported pose automation; community tools (unsupported)
11. Simulator-only observations that affect how you read results (third-party)

Labelling: facts stated plainly with an Apple link are Apple's. Anything marked "(third-party, unverified)" comes from developer write-ups or simulator measurements and has not been confirmed by Apple. "(inferred)" marks this repo's reasoning.

## 1. Apple's three test environments

Apple's "Three steps" page lists them in this order ([Three steps to make your app shine on iPhone Duo](https://developer.apple.com/iphone-duo/prepare/)):

| Order | Environment | Apple's wording | Use it for |
|---|---|---|---|
| 1 | iOS Resizable simulator in Device Hub | listed first | compact-to-regular resizing of your own layout |
| 2 | iPhone Mirroring on macOS 27 | "resized to extreme sizes in both directions" | continuous resizing with a real app on a real phone |
| 3 | iPhone Duo simulator in Xcode 27.1 | "the best way to test the full native experience" | poses, vertical bars, reserved regions, two displays |

Apple also cautions that "Device Hub's Resizable iPhone / iPhone Mirroring behavior is an approximation, but iPhone Duo-specific behaviors need dedicated testing" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Treat environments 1 and 2 as a way to find resizing bugs early, never as the sign-off.

## 2. Device Hub pose controls (verbatim)

Device Hub is Xcode's manager for run destinations: "when you run your app on a simulated or physical device, Device Hub opens a compact window showing your app on a device screen" ([Device Hub](https://developer.apple.com/documentation/xcode/device-hub)).

Apple's instructions for iPhone Duo ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)):

> To close the iPhone Duo, click the Closed button on the right of the Rotate Right button.
> To partially open the iPhone Duo, click the Partially Open button in the middle of the three device pose buttons.
> To fully open the iPhone Duo, click the Open button on the far right.
> To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel.

Use Apple's names (Closed, Partially Open, Open, Rotate Right) in anything you write. One developer saw the buttons labelled "Rotate Right, Closed, Book, Open" with Book at 127° and Open at 180° in the 27.1 beta (third-party, unverified); Apple publishes no angle for any pose and says hinge "Update rate and precision are system policy, so don't depend on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

Split View is tested by hand: drag "the app by the home indicator to either side of the screen, and check vertically laid-out content on both sides" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

The Xcode 27.2 RC notes list new Device Hub features: Slow Motion Animation, Simulate Shake, Simulate Fall, Simulate Memory Pressure, Hide Device Bezels, App Settings ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). Slow Motion Animation is useful for watching a fold transition frame by frame (inferred).

## 3. Previews "Display" override

Xcode 27.1: "The canvas overrides picker now includes a Display group for previewing content on a device's alternative display. (182598534)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)). This is the fastest way to see a SwiftUI view on the inner display while editing; it does not replace the simulator for poses, Split View or sheets (inferred).

## 4. Toolchain requirements and the SDK stamp

- "Xcode 27.1 includes Swift 6.4 and SDKs for iOS 27.1, iPadOS 27, tvOS 27, watchOS 27, macOS 27, and visionOS 27 ... Xcode 27.1 requires a Mac running macOS Tahoe 26.6 or later" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)). The final build is 27A9275, released October 15, 2026 ([Apple Software Releases](https://developer.apple.com/news/releases?id=10152026a)).
- The Xcode 27.2 beta did not include Duo support despite the higher number (third-party, unverified). Do not tell a user "any Xcode 27.x".
- SDK tiers decide what you will see on the inner display: "iOS 26 SDK or earlier: The app runs but appears centered on the inner display with empty space around it. ... iOS 27 SDK: The app fills most of the inner display but still avoids the status bar. iOS 27.1 SDK or later: The app uses the full display, and toolbars and tab bars move vertically below the status bar" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Verify the stamp (third-party, unverified check): `otool -l <path/to/App.app/App> | grep -A4 LC_BUILD_VERSION` should show `sdk 27.1`. One developer's `swiftc -sdk` build was stamped 27.0 and behaved like a 27.0 build.
- Mac Catalyst, from the same Xcode 27.1 release notes: iOS 27.1-only APIs cause compile errors in Catalyst builds (185924957; workaround `#if !targetEnvironment(macCatalyst)`), and an iOS 27.1 target shows no Catalyst run destination (187046347; workaround: add a Mac Catalyst 27.0 minimum deployment) ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

## 5. Getting the simulator

- In Xcode: Device Hub "+" → iPhone → iPhone Duo; if the device type is missing, re-download the iOS 27.1 runtime via Xcode Settings → Components → Update (third-party, unverified; the thread is [Apple Developer Forums 847137](https://developer.apple.com/forums/thread/847137)).
- "Initial Simulator launch can take several minutes. (187708500)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
- One developer found the Duo simulator heavy enough to make an M1 Mac mini nearly unresponsive (third-party, unverified); warn users on small machines and CI runners.

## 6. Command line: identifiers and commands (third-party)

Every identifier below is third-party and unverified by Apple. They were consistent across the sources the report reviewed, but confirm them on the user's machine with `xcrun simctl list devicetypes | grep -i duo` and `xcrun simctl list runtimes` before writing them into scripts or CI.

| Item | Value (third-party, unverified) |
|---|---|
| Device type | `com.apple.CoreSimulator.SimDeviceType.iPhone-Duo` (alias `com.apple.CoreSimulator.SimDeviceType.V68`) |
| Runtime | `com.apple.CoreSimulator.SimRuntime.iOS-27-1` (build 24A94401) |
| iPhoneOS / iPhoneSimulator SDK build | 24A94403 |
| Model identifier reported by the simulator | `iPhone19,4` |
| Runtime download size | about 7.85 GB |

Commands (third-party, unverified):

```sh
# Download the iOS 27.1 platform; one developer had to retry with -buildVersion 24A94401
xcodebuild -downloadPlatform iOS

# Create a Duo simulator
xcrun simctl create "Duo-27.1" \
  com.apple.CoreSimulator.SimDeviceType.iPhone-Duo \
  com.apple.CoreSimulator.SimRuntime.iOS-27-1

# List the displays a booted device exposes
xcrun simctl io <udid> enumerate
```

`xcrun simctl help` lists no fold, posture or display-selection subcommand ([Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883), a developer's observation in a thread with no Apple reply).

## 7. Per-display screenshots and the conflicting display IDs (third-party)

Apple's pixel sizes for App Store Connect are the only official numbers: outer display 1398×2034 (portrait) / 2034×1398 (landscape); inner display 2007×2853 / 2853×2007 ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).

Two third-party reports describe how to reach each display with `simctl`, and they disagree on the identifier:

| Source (third-party, unverified) | Outer display | Inner display | Notes |
|---|---|---|---|
| blakecrosley.com (Xcode 27.1 beta simulator; worked example) | `--display=primary` | `--display=primary-1` | `xcrun simctl io <udid> enumerate` listed `primary` and `primary-1`; captures were exactly 1398×2034 and 2007×2853 |
| skarol.dev | `--display=1` ("cover") | `--display=3` | a plain `screenshot` with no `--display` showed the inner display, black when the device was folded |
| Apple Developer Forums 847883 (developer post) | — | second display "LCD-1", 2007×2853 | the forum poster's `simctl io screenshot` output |

Command form as reported (third-party, unverified):

```sh
xcrun simctl io <udid> screenshot --type=png --display=primary   outer.png
xcrun simctl io <udid> screenshot --type=png --display=primary-1 inner.png
```

How to proceed without an Apple statement: run `enumerate` first, read the display list on the user's machine, then capture; verify every PNG's pixel size with `sips -g pixelWidth -g pixelHeight <file>` and compare to Apple's table. `scripts/duo_screenshots.sh` in this skill does exactly that and lets you override the display identifiers. The device must be opened in Device Hub by hand before the inner display shows content; no `simctl` flag does it.

Known issue to account for: "Screenshots and recordings in iPhone Duo might be black for up to a few minutes after booting the device. (187146039)" ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)).

## 8. Known issues with IDs (Apple release notes)

| ID | Apple's text | Source | Consequence for testing |
|---|---|---|---|
| 187708500 | "Initial Simulator launch can take several minutes." | [Xcode 27.1 RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes) | pre-warm runtimes on CI; do not time out early |
| 187708663 | "StandBy is unavailable in the iPhone Duo Simulator runtime." | [Xcode 27.1 RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes) | test StandBy on hardware |
| 187708767 | "Running and debugging most app extensions is unavailable in the iPhone Duo Simulator runtime." | [Xcode 27.1 RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes) | widgets, Live Activities and other extensions on a regular iOS 27.1 simulator or hardware |
| 190155353 | "In the iPhone Duo simulator, an app using `CameraCaptureAccessory` can use both displays at the same time without an active camera capture session." | [Xcode 27.1 RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); recorded as fixed in the [27.2 RC RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes) | an accessory that appears in the 27.1 simulator may not appear on a device until a session is active |
| 187146039 | "Screenshots and recordings in iPhone Duo might be black for up to a few minutes after booting the device." | [Xcode 27.2 RC RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes) | wait, or retake, before filing a bug |
| 187148389 | "VoiceOver, the Accessibility Inspector, and other accessibility tools cannot convey screen content on an iPhone Duo within Device Hub." | [Xcode 27.2 RC RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes) | accessibility checks need hardware or another route |
| 189465196 | "When switching between the inner and outer display of the iPhone Duo simulator, modifier keys such as Shift and Command might stop working." | [Xcode 27.2 RC RN](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes) | keyboard shortcut tests after a pose change are unreliable |

## 9. What the simulator cannot test

- Apple: StandBy (187708663) and most app extensions (187708767), above.
- Apple: "Simulator has no camera, so test on a device before shipping" ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)). This covers the two front cameras, the Virtual Front Camera, `AVCaptureDeviceDirectionCoordinator` switching, and `CameraCaptureAccessory` content on the outer display.
- Apple: ergonomics. "Interactions that look fine in the simulator may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution"; validate button targets, vertical bars and navigation on a device ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Apple: hinge values. Rate and precision are system policy ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)); the simulator slider is not evidence of how a real hinge reports.
- Third-party (unverified): camera transitions, capture accessories, reachability, haptics, performance, memory, thermals.
- Devices are scarce: Apple's workshops have devices but "Availability isn't guaranteed" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)); the only TestFlight anecdote is a viewer that went blank in the simulator but "was not affected in TestFlight" (third-party, unverified), so simulator-only bugs exist too.

## 10. No supported pose automation; community tools (unsupported)

- `xcrun simctl help` lists no fold/posture/display subcommand; `XCUIDevice` documents only buttons, orientation and Siri; the forum thread "Supported way to put an iPhone Duo simulator into the unfolded state programmatically" has no Apple reply ([Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883); [XCUIDevice](https://developer.apple.com/documentation/xcuiautomation/xcuidevice)).
- XCUITest runs on the Duo simulator but cannot change posture (third-party, unverified). A SwiftUI Q&A thread title reports "XCUITest accessibility snapshot reports stale frames during live scene resize" ([Apple Forums activity 1664080](https://developer.apple.com/forums/activities/1664080)); the thread body was not fetched, so treat it as a warning rather than a confirmed bug.

Community workarounds exist. All are unsupported, drive Device Hub's UI or undocumented mechanisms, and can break with any Xcode update. Mention them only as local conveniences and never as CI dependencies:

| Tool (third-party, unsupported) | What it claims | Mechanism as described |
|---|---|---|
| skarol/duoctl | fold, rotate, tap the simulator | Device Hub's accessibility tree |
| EvanBacon/serve-sim | `fold <angle> -d <udid>` (0/130/180); reads hinge via `xcrun devicectl device motion hinge-angle --device <udid>`; detects active panel via SpringBoard `DisplayContentMode` events (`.cover:pri` / `.inner:pri`) | undocumented; "Device Hub can shadow input" per its own notes |
| artemnovichkov/hinge | CLI for the same | not documented in the report |
| blakecrosley.com | drove the Device Hub buttons via accessibility `AXPress` | script against Device Hub UI |

## 11. Simulator-only observations that affect how you read results (third-party)

These are simulator measurements, not Apple statements. They help you interpret what you see; do not quote them as specifications.

- Window sizes under the 27.1 SDK: closed 466×678 pt (content 382×562); open 951×669 pt (content 867×553, with a 40 pt inactive division at x=455); open and rotated 669×951 pt (content 669×734). The display profile lists `primary` (outer) 1398×2034 px at scale 3 and `primary-1` (inner) 2007×2853 px at scale 3, native orientation 270 (third-party, unverified). Apple publishes pixels only ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)).
- The vertical bar adds an 84 pt trailing safe-area inset with zero leading on the outer display; `prefersStatusBarHidden = true` hides icons but not the inset (third-party, unverified).
- The fold's division region is 40 pt wide (20 pt margins each side) and active only while partially folded; regions arrive after the first layout pass; the folded outer display reports no reserved regions (third-party, unverified). Apple's rule is that the fold region "is active when iPhone Duo is partially open, but inactive when it is fully open" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- `UIScreen.main.bounds` returned 466×678 while the app ran on the inner display (third-party, unverified), which matches Apple's warning that `UIScreen.main` is "ambiguous on two-display devices and will be deprecated in a future release" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)). If a test asserts on `UIScreen.main`, the assertion is wrong, not the device.
- `openWindow` on iPhone opened the new window full screen, not in Split View, and a visible app in Split View can be `inactive` (third-party, unverified). Pause media on background, not on resign-active, when you test Split View.
