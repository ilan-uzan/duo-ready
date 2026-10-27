Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# App Store Connect facts for iPhone Duo

Contents

1. Timeline and toolchain
2. SDK tiers (what "optimized" means to Apple)
3. Screenshot specifications (verbatim figures)
4. App preview specifications (verbatim figures)
5. Badge, preview tool, featuring nomination
6. Other submission facts
7. Automation and analytics: what is undocumented
8. Capturing the pixels (third-party commands, Apple pose controls)

Labels: facts stated plainly are Apple's and carry an inline citation. "(third-party, unverified)" and "(inferred)" mark everything else. Do not upgrade a label.

## 1. Timeline and toolchain

| Date | Event | Source |
|---|---|---|
| September 9, 2026 | iPhone Duo announced; HIG "Designing for iPhone Duo" published | [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) |
| September 18, 2026 | Xcode 27.1 beta announced | [Apple Developer News](https://developer.apple.com/news/?id=nyuppv9r) |
| October 5, 2026 | App Store Connect begins accepting iPhone Duo-optimized submissions | [Apple Developer News](https://developer.apple.com/news/?id=kkphp5qo) |
| October 15, 2026 | Xcode 27.1 final, build 27A9275 | [Apple Software Releases](https://developer.apple.com/news/releases?id=10152026a) |
| October 23, 2026 | Device ships with iOS 27.1 | [Apple Newsroom](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/) |
| April 2027 | Duo screenshots become required (scope disputed; see `april-2027.md`) | both pages below |

Toolchain floor, verbatim: "Xcode 27.1 includes Swift 6.4 and SDKs for iOS 27.1, iPadOS 27, tvOS 27, watchOS 27, macOS 27, and visionOS 27 ... Xcode 27.1 requires a Mac running macOS Tahoe 26.6 or later" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

Xcode 27.2 beta did not include Duo support despite the higher number (third-party, unverified: [ecorpit](https://ecorpit.com/iphone-duo-sdk-new-apis-xcode-27-1-developer-guide-2026/)). Pin release archives to 27.1 until Apple's 27.2 notes say otherwise.

Mac Catalyst known issues in 27.1 that affect a shared target: iOS 27.1-only APIs produce compile errors (185924957; workaround `#if !targetEnvironment(macCatalyst)`), and targeting iOS 27.1 shows no Catalyst run destination (187046347; workaround: add a Mac Catalyst 27.0 minimum deployment) ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

## 2. SDK tiers

Verbatim from [Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/):

> **iOS 26 SDK or earlier:** The app runs but appears centered on the inner display with empty space around it. Closed, it sits beside the status bar and camera. **iOS 27 SDK:** The app fills most of the inner display but still avoids the status bar. **iOS 27.1 SDK or later:** The app uses the full display, and toolbars and tab bars move vertically below the status bar. Before shipping with this SDK, confirm your content adapts to the vertical bars.

The Technology Overview says the same thing more tersely: "When you build with Xcode 26 and earlier, your app doesn't extend under the status bar and camera" ([Apple: Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).

DTS on the compatibility mode: closed, the app uses the region outside the vertical bar; fully open, it is centered at a familiar aspect ratio with letterboxing; partially open, it is shifted to one side; and "iPad apps don't run in compatibility mode on iPhone Duo, unlike on Apple Vision Pro" ([Apple Developer Forums 847887](https://developer.apple.com/forums/thread/847887); [847644](https://developer.apple.com/forums/thread/847644)).

Tier is decided by the build SDK, not the deployment target; there is no Info.plist key to request the older mode (third-party summary of Apple's UIKit Q&A, [Gubarenko Q23](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)). Verify the stamp with `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, expecting `sdk 27.1` (third-party, unverified: [blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)).

The new APIs are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo"; Apple recommends "gating iOS 27.1 APIs behind availability checks" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). A lower deployment target is fine.

## 3. Screenshot specifications

Source: [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications).

| Device size | Portrait (px) | Landscape (px) |
|---|---|---|
| iPhone Duo, outer display | 1398×2034 | 2034×1398 |
| iPhone Duo, inner display | 2007×2853 | 2853×2007 |

General rules on the same page: up to 10 screenshots per device size; `.jpeg`, `.jpg`, or `.png`; no alpha. Duo is not currently a required size; the required sizes are "iPhone with Dynamic Island (medium display)" and "iPad 13-inch" if applicable. The page's display-scaling rule (supply only the highest required resolution) is stated for ordinary sizes; no fallback or scaling rule is given for Duo (gap). Whether one or both Duo displays will be required in April 2027 is not stated (gap).

Verbatim April 2027 sentence on this page: "Starting in April 2027, screenshots will be required for any app using the iOS 27.1 SDK or later."

Verbatim badge sentence on this page: "When you submit iPhone Duo screenshots in App Store Connect, your App Store product page will display a badge to let people know your app is optimized for iPhone Duo."

Context for the numbers (inferred, with the third-party source): the simulator renders the inner display into a 2007×2853 buffer at scale 3 (669×951 pt) and the outer at 1398×2034 (466×678 pt), so `simctl` screenshots land on the ASC sizes exactly; the physical inner panel is 1878×2670 px ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/); point figures are third-party simulator measurements, [blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator)). Apple publishes no point dimensions.

## 4. App preview specifications

Source: [ASC app preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications).

| Item | Value |
|---|---|
| Position on page | iPhone Duo listed first under iPhone; the only device with two device resolutions |
| Device resolutions printed | 2034×1398 and 2853×2007 |
| Ratio label printed | "19.5:9" (fits neither display; Apple page error) |
| Accepted upload resolutions | 886×1920 (portrait) / 1920×886 (landscape) |
| Duration | 15–30 seconds |
| File size | up to 500 MB |
| Frame rate | up to 30 fps |
| Codec | H.264 or ProRes 422 |
| Count | up to three per device size and language |
| Processing | up to 24 hours |
| Required | No |

The "19.5:9" label: 2853/2007 ≈ 1.42 and 2034/1398 ≈ 1.45, so the label is wrong on Apple's page; use the pixel figures ([report Appendix C]). The page initially said upload support "will be available later this year" (third-party, [blakecrosley.com, Day Two](https://blakecrosley.com/blog/iphone-duo-day-two)); confirm the slot exists in App Store Connect before promising a preview.

## 5. Badge, preview tool, featuring nomination

From [Apple Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo), verbatim:

- "Recompile existing apps with Xcode 27.1, which adds development support for iPhone Duo"
- "You can submit iPhone Duo-optimized apps and games in App Store Connect now"
- "If you submit iPhone Duo screenshots, your App Store product page displays a badge indicating the app is optimized for iPhone Duo"
- "A new preview tool in App Store Connect shows how screenshots, product page headers and other metadata will look on an iPhone Duo product page"
- "Starting April 2027, any apps or games submitted will need to include screenshots for iPhone Duo"

Badge name: "Made for iPhone Duo" ([Apple Newsroom, Oct 22 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/); also the image alt text on the [developer hub](https://developer.apple.com/iphone-duo/)).

Featuring: submit a featuring nomination in App Store Connect and note in "Helpful Details" that the app "is optimized for iPhone Duo, including support for all device poses" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).

Inference, labelled: the badge is triggered purely by uploading Duo screenshots, not by SDK or any capability flag, so an unoptimized app could technically earn it. The constraint is App Review: a forum poster paraphrases Guideline 2.3.3 as screenshots must show the app in use on that device, from the running app or simulator, not mockups, and raises 2.1(a) rejection risk if the UI is broken on Duo ([Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106)). The App Review Guidelines text itself was not fetched; quote 2.3.3 as a paraphrase.

Apple's related asset pages, linked from the hub: [App Store asset best practices](https://developer.apple.com/app-store/asset-best-practices/) and [Apple Design Resources](https://developer.apple.com/design/resources/) (Figma/Sketch kits). The ASC Help page [Upload app previews and screenshots](https://developer.apple.com/help/app-store-connect/manage-app-information/upload-app-previews-and-screenshots) was fetched without any Duo text, so how the UI labels inner versus outer slots is unconfirmed.

## 6. Other submission facts

| Fact | Source |
|---|---|
| "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" (cross-references TN3208) | [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key) |
| TN3192 migration checklist: provide a launch screen, support all interface orientations, remove `UIRequiresFullScreen`; build setting `INFOPLIST_KEY_UIRequiresFullScreen` | [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key) |
| "Starting in iOS 27 and iPadOS 27, `UIRequiresFullScreen` no longer opts your app out of resizing on either platform. Instead, the system resizes your app's scene discretely" (applies when built with the iOS 27 SDK or later and the key is `YES`, "unless `UIRequiresFullScreenIgnoredStartingWithVersion` specifies version 27 or earlier") | [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key) |
| Scene lifecycle required for iOS 27 SDK builds: "Application failed to launch: UIScene life cycle is required for apps built with this SDK"; fix was `SceneDelegate.swift`, `UIApplicationSceneManifest`, moving `UIWindow` creation out of the AppDelegate; Expo: `expo-build-properties` → `"ios": {"enableSceneSupport": true}` | third-party: [react-native #58606](https://github.com/react/react-native/issues/58606); "Xcode 27 requires the scene lifecycle, so migrate first" via [Gubarenko Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums) |
| "apps can't require iPhone Duo-specific capabilities"; "iPhone Duo is not a separate device class"; no own `UIUserInterfaceIdiom` | [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644) |
| App Store Connect "Larger Text" criteria apply: "For fixed one-screen layouts, holding text at the largest standard size can fail App Store Connect's Larger Text criteria" (thread cites scales past 200% at AX3 and over 300% at AX5) | [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644) |
| App icon: no Duo-specific guidance; 1024×1024 px; last change "June 8, 2026 \| Refined guidance for Liquid Glass" | [HIG App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) |
| No new permission, privacy-manifest entry, or Required Reason API tied to Duo was found (inferred from absence; Upcoming Requirements lists none) | [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) |
| Touch ID, not Face ID: branch biometric copy on `LAContext.biometryType` | [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/) |

## 7. Automation and analytics: what is undocumented

| Item | Status |
|---|---|
| fastlane `deliver` support for Duo sizes | Yes since 2.241.1 (2026-10-15): fastlane: PR #30444 "[deliver] add iphone duo screenshot sizes" merged 2026-10-14 and shipped in fastlane 2.241.1 (2026-10-15); `deliver` maps `DisplayType::APP_IPHONE_DUO` (display name "iPhone Duo") to 1398×2034, 2034×1398, 2007×2853 and 2853×2007 and matches screenshot files to display types by pixel size, so any filename works (third-party, read from fastlane's source on 2026-10-27: https://github.com/fastlane/fastlane/pull/30444). Older fastlane versions reject the sizes. `snapshot` and `frameit` Duo support: not verified. The string `APP_IPHONE_DUO` is what fastlane sends to the App Store Connect API; Apple's own API documentation for it was not located (gap). |
| App Store Connect API `ScreenshotDisplayType` value for Duo | `APP_IPHONE_DUO` is the value fastlane's spaceship sends (third-party source code, 2026-10-27). Apple's API documentation for it was not located (gap). |
| Xcode Cloud, Bitrise, Codemagic Duo destinations | No documentation mentions Duo (gap). [Bitrise](https://docs.bitrise.io/en/bitrise-ci/testing/testing-ios-apps/building-an-ios-app-for-testing) recommends generic simulator destinations. |
| TestFlight | Nothing Duo-specific exists; a Duo build is an ordinary iOS build. Only anecdote: a viewer that went blank in the simulator "was not affected in TestFlight" (third-party, [blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)). |
| App Store Connect analytics | Device dimension values are iPhone, iPad, Apple TV, iPod, Desktop, Apple Vision; no Duo breakdown ([ASC App analytics filters and dimensions](https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/)). Log your own properties (duo-backend). |
| iOS 27.1 release notes | URL returned 404 at research time ([link](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27_1-release-notes)). |

## 8. Capturing the pixels

Apple's pose controls in Device Hub, verbatim: "To close the iPhone Duo, click the Closed button on the right of the Rotate Right button. / To partially open the iPhone Duo, click the Partially Open button in the middle of the three device pose buttons. / To fully open the iPhone Duo, click the Open button on the far right. — To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel" ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)). There is no supported way to set the pose programmatically: `xcrun simctl help` lists no fold subcommand and the forum request has no Apple reply ([Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883)).

Command-line capture (third-party, consistent across sources; [blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator)):

```sh
# Third-party commands; verify display names on your machine first.
xcrun simctl io <udid> enumerate                      # lists primary (outer) and primary-1 (inner)
xcrun simctl io <udid> screenshot --type=png --display=primary   outer.png   # 1398×2034
xcrun simctl io <udid> screenshot --type=png --display=primary-1 inner.png   # 2007×2853
```

Another developer reports `--display=1` for the cover and `--display=3` for the inner display, and that a plain screenshot shows the inner display, black when folded (third-party, [skarol.dev](https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/)). Device type `com.apple.CoreSimulator.SimDeviceType.iPhone-Duo`, runtime `com.apple.CoreSimulator.SimRuntime.iOS-27-1` (third-party).

Apple known issues to plan around: "Screenshots and recordings in iPhone Duo might be black for up to a few minutes after booting the device. (187146039)" ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)); "Initial Simulator launch can take several minutes. (187708500)" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

Validation before upload (inferred from the spec rules): exact pixel size from section 3; no alpha channel (`sips -g hasAlpha <file>` on macOS should report `no`); `.png`/`.jpeg`/`.jpg`; at most 10 per device size. The duo-test skill owns the batch capture script.
