---
name: duo-ship
description: >-
  Get an iOS build through App Store Connect with iPhone Duo covered: the
  right Xcode/SDK tier, the launch-screen and scene-lifecycle submission
  requirements, the exact Duo screenshot and app-preview sizes, the "Made for
  iPhone Duo" badge, the April 2027 screenshot mandate and what Apple has and
  has not said about it, and a release checklist the model walks the user
  through. Use it whenever someone is about to submit, is asked for new
  screenshots, or asks about release timing, even if they never say "Duo":
  "App Store Connect is showing new screenshot sizes", "what size screenshots
  for the foldable", "do I need new screenshots in April", "how do I get the
  optimized badge", "release checklist for the new iPhone", "App Store wants a
  launch screen now", "which Xcode do I need to ship", "fastlane deliver has
  no slot for these screenshots", "app preview 886x1920".
---

# duo-ship: getting a Duo-ready build through App Store Connect

## What Apple actually says

- App Store Connect has accepted iPhone Duo-optimized apps and games since October 5, 2026; Apple's instruction is "Recompile existing apps with Xcode 27.1, which adds development support for iPhone Duo", and "If you submit iPhone Duo screenshots, your App Store product page displays a badge indicating the app is optimized for iPhone Duo" ([Apple Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo)). The badge is named "Made for iPhone Duo" ([Apple Newsroom, Oct 22 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/)).
- Duo screenshot sizes are the only Apple-published pixel figures besides the panel specs: outer display 1398×2034 / 2034×1398, inner display 2007×2853 / 2853×2007; up to 10 per device size; `.jpeg`/`.jpg`/`.png`; no alpha; Duo is not currently a required size ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
- Screenshots become mandatory in April 2027, but Apple's two pages disagree on scope: the news post says "any apps or games submitted", the specs page says "any app using the iOS 27.1 SDK or later". Nobody from Apple has resolved it ([Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106); [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) does not list it yet).
- How much of the inner display a build gets depends on the SDK it links against, not its deployment target: iOS 26 SDK letterboxed, iOS 27 SDK fills most, iOS 27.1 SDK edge-to-edge with vertical bars ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)). Xcode 27.1 (build 27A9275, released October 15, 2026) carries the iOS 27.1 SDK and "requires a Mac running macOS Tahoe 26.6 or later" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes); [Software Releases](https://developer.apple.com/news/releases?id=10152026a)).
- Two iOS 27 SDK rules become launch-blocking on Duo: "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key), cross-referencing TN3208), and the scene-based lifecycle is required for apps built with this SDK (third-party reports of Apple's UIKit Q&A and a React Native launch failure; see Common mistakes).

Everything below follows from those five points. Where Apple is silent (fastlane enum values, inner-vs-outer set requirement, review guideline text), say so instead of guessing.

## Workflow

Work from the user's actual project, not from a generic answer. Ask for the repo path, the Xcode version they build with, and whether CI builds the archive that goes to App Store Connect.

### Step 1: establish the SDK tier the archive will be in

The tier is decided by the build SDK, and there is no Info.plist opt-out or opt-in (third-party summary of Apple's UIKit Q&A, [Gubarenko Q23](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)). Apple's description of the three tiers, verbatim from the Three steps page:

> **iOS 26 SDK or earlier:** The app runs but appears centered on the inner display with empty space around it. Closed, it sits beside the status bar and camera. **iOS 27 SDK:** The app fills most of the inner display but still avoids the status bar. **iOS 27.1 SDK or later:** The app uses the full display, and toolbars and tab bars move vertically below the status bar. Before shipping with this SDK, confirm your content adapts to the vertical bars.

What to do:

1. Check which Xcode produces the App Store archive. Local `xcodebuild -version` is not enough if CI archives; read the CI config (Xcode Cloud workflow, `.github/workflows/*.yml`, `bitrise.yml`, `codemagic.yaml`, Fastfile) for the selected Xcode. The floor for the top tier is Xcode 27.1 (27A9275) on macOS Tahoe 26.6 or later. If CI runners are on an older macOS they cannot run Xcode 27.1.
2. Warn that a higher version number is not safer: the Xcode 27.2 beta did not include Duo support (third-party, unverified: [ecorpit](https://ecorpit.com/iphone-duo-sdk-new-apis-xcode-27-1-developer-guide-2026/)). Pin the archive step to 27.1 until Apple's 27.2 release notes say otherwise.
3. If a project path is available, run `python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>`. Rule DUO-019 flags a project whose `LastUpgradeCheck` is below 2710, and DUO-020 flags iOS 27.1-only API in a Mac Catalyst target, which Apple lists as a known compile error (185924957; workaround `#if !targetEnvironment(macCatalyst)`) ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
4. After archiving, the SDK stamp can be verified with `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, expecting `sdk 27.1` (third-party, unverified; one developer's build was accidentally stamped 27.0: [blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)).

Explain the consequence to the user: shipping an iOS 27.1 SDK build means vertical bars appear on the outer display, so this step is only safe once duo-bars and duo-layout work is done. Shipping an iOS 27 SDK build avoids that but caps you at "fills most of the inner display".

### Step 2: clear the two iOS 27 SDK submission blockers

Both apply to any iOS 27 or 27.1 SDK build, not only on Duo, and both are caught by the audit tool:

- **Launch screen (DUO-010).** TN3192: "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission." Look in `Info.plist` for a `UILaunchScreen` dictionary or `UILaunchStoryboardName`, or for `INFOPLIST_KEY_UILaunchScreen_Generation` in build settings. TN3192's migration checklist is: provide a launch screen, support all interface orientations, remove `UIRequiresFullScreen` ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
- **Scene lifecycle (DUO-009).** Look for `UIApplicationSceneManifest` in `Info.plist` and a `UIWindowSceneDelegate`; an AppDelegate that creates `UIWindow(frame:)` is the failure pattern. The evidence is third-party: React Native 0.88.0-rc.0 failed to launch on the Duo simulator with "Application failed to launch: UIScene life cycle is required for apps built with this SDK" ([react-native #58606](https://github.com/react/react-native/issues/58606)), and a third-party summary of Apple's UIKit Q&A records "Xcode 27 requires the scene lifecycle, so migrate first" ([Gubarenko Q20](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)). For Expo projects the fix recorded there is `expo-build-properties` → `"ios": {"enableSceneSupport": true}`.
- **`UIRequiresFullScreen` (DUO-008).** Not a blocker, but its meaning changed: "Starting in iOS 27 and iPadOS 27, `UIRequiresFullScreen` no longer opts your app out of resizing on either platform. Instead, the system resizes your app's scene discretely" ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)). Tell the user it will not keep their app at a fixed size on Duo; the app "still resizes when the device opens or closes" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

There is no Duo device capability to declare: "apps can't require iPhone Duo-specific capabilities" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Do not add anything to `UIRequiredDeviceCapabilities` for Duo.

### Step 3: decide the screenshot plan

Read `references/app-store-connect.md` for the full tables. The decisions:

1. **Which sets.** Apple publishes four Duo sizes (outer portrait/landscape, inner portrait/landscape) and has not said whether one or both displays will be required in April 2027 (gap, [Appendix C of the report]). The safe plan (inferred) is to produce at minimum outer portrait (1398×2034) and inner portrait (2007×2853), because those are the two displays' native portrait captures and cover either reading of the rule.
2. **Capture, don't compose.** The constraint is App Review: a forum poster paraphrases Guideline 2.3.3 as screenshots must show the app in use on that device, from the running app or simulator, not mockups, and raises 2.1(a) rejection risk if the UI is broken on Duo ([Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106); the guideline text itself was not fetched, so quote it as a paraphrase). The badge is triggered by uploading Duo screenshots alone, not by SDK or any flag (inferred from the Oct 5 news post wording), which is exactly why Apple can and will check that the screenshots show the real app.
3. **Where the pixels come from.** The iPhone Duo simulator in Xcode 27.1 is Apple's named test environment ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)); Device Hub's Closed / Partially Open / Open buttons set the pose ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)). The command-line capture path is third-party but consistent across sources: `xcrun simctl io <udid> enumerate` lists `primary` (outer) and `primary-1` (inner); `xcrun simctl io <udid> screenshot --type=png --display=primary outer.png` and `--display=primary-1 inner.png` yield exactly 1398×2034 and 2007×2853 ([blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator); another developer reports `--display=1` / `--display=3`, [skarol.dev](https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/)). There is no `simctl` fold command, so set the pose in Device Hub first. The duo-test skill owns the capture script; point the user there for the batch workflow.
4. **Known simulator trap.** "Screenshots and recordings in iPhone Duo might be black for up to a few minutes after booting the device. (187146039)" ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). Boot, wait, verify a capture is not black before running a batch.
5. **Validate before upload.** Check each file: exact pixel size from the table, no alpha channel (`sips -g hasAlpha` or `file` on macOS), `.png` or `.jpeg`, no more than 10 per device size. Apple also uses a "display scaling" rule for ordinary iPhone sizes (supply only the highest required resolution) but gives no fallback or scaling rule for Duo, so do not promise that another size will be scaled into the Duo slot.

### Step 4: app previews (optional)

Apple lists iPhone Duo first under iPhone with two device resolutions, 2034×1398 and 2853×2007, and accepts uploads at 886×1920 (portrait) / 1920×886 (landscape); 15–30 seconds; up to 500 MB; up to 30 fps; H.264 or ProRes 422; up to three per device size and language; optional; processing up to 24 hours ([ASC app preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications)). The page labels the Duo row "19.5:9", which fits neither display's ratio (2853/2007 and 2034/1398 are both about 1.42–1.45); treat that label as an Apple page error and use the pixel figures. Previews are not part of the April 2027 requirement as published.

### Step 5: App Store Connect metadata and the badge

- Upload the Duo screenshot sets. The badge follows from that: "When you submit iPhone Duo screenshots in App Store Connect, your App Store product page will display a badge to let people know your app is optimized for iPhone Duo" ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
- Use the new preview tool: "A new preview tool in App Store Connect shows how screenshots, product page headers and other metadata will look on an iPhone Duo product page" ([Apple Developer News](https://developer.apple.com/news/?id=kkphp5qo)). The ASC Help page on uploading previews and screenshots was fetched without any Duo text, so how the UI labels the inner versus outer slots is unconfirmed; tell the user to read the slot labels in ASC rather than assume an order.
- If the app genuinely supports every pose, submit a featuring nomination and write in "Helpful Details" that the app "is optimized for iPhone Duo, including support for all device poses" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)). Do not claim this for an app that only passes the SDK tier.
- Accessibility: App Store Connect's "Larger Text" criteria apply, and "For fixed one-screen layouts, holding text at the largest standard size can fail App Store Connect's Larger Text criteria" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Let text reflow.
- App icon: the HIG App Icons page has no Duo-specific guidance and the spec remains 1024×1024 px (last change "June 8, 2026 | Refined guidance for Liquid Glass") ([HIG App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)). Nothing to do.

### Step 6: plan for April 2027

Read `references/april-2027.md` and give the user both quotes. The honest position:

- Date is firm: April 2027 appears on both Apple pages.
- Scope is unresolved: "any apps or games submitted" (news post) versus "any app using the iOS 27.1 SDK or later" (specs page). The forum question about iOS 27.0 SDK builds has no Apple reply, and the Upcoming Requirements page (fetched 2026-10-26) does not list the item; its latest entries are September 9, 2026 and April 28, 2026.
- Inner versus outer sets: unspecified.
- Safe plan (inferred): capture both portrait sets from the simulator and upload before April 2027. That satisfies either reading and earns the badge now. Tell the user to re-check the Upcoming Requirements page before relying on any narrower reading.

### Step 7: automation and analytics, honestly

- fastlane `deliver` / `snapshot` and the App Store Connect API: no documentation records the `ScreenshotDisplayType` or `screenshot_display_type` values for Duo ([fastlane snapshot](https://docs.fastlane.tools/actions/snapshot/) has no Duo mention). Do not invent an enum case such as `APP_IPHONE_DUO`. Have the user upload the Duo sets manually in App Store Connect, or inspect the API's live enum for the new values and quote what they find.
- App Store Connect analytics exposes only platform-level Device values (iPhone, iPad, Apple TV, iPod, Desktop, Apple Vision), with no Duo breakdown ([ASC App analytics filters and dimensions](https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/)). If they need Duo adoption numbers, they must log their own properties; duo-backend covers that.
- Xcode Cloud, Bitrise and Codemagic documentation mention nothing Duo-specific (gap); a Duo build is an ordinary iOS build to TestFlight. No TestFlight-specific guidance exists.

### Step 8: walk the release checklist

Open `references/release-checklist.md` and go through it item by item with the user, marking each as done, not applicable, or blocked. Don't hand over the list and stop; the point is that each item is answered from their project.

## Common mistakes

- Setting the deployment target to 27.1 and expecting edge-to-edge. The tier comes from the SDK the archive links against ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)); deployment target does not matter, and there is no plist key either way (third-party summary of Apple's Q&A).
- Shipping with the 27.1 SDK before checking vertical bars. Apple's own sentence: "Before shipping with this SDK, confirm your content adapts to the vertical bars." Field reports describe sheets with a text-only Done button that "reserved the side rail and left it empty" (third-party, [blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)). Route to duo-bars.
- AppDelegate-only apps that launch fine on iOS 26 and fail at launch under the iOS 27 SDK ("UIScene life cycle is required", third-party, [react-native #58606](https://github.com/react/react-native/issues/58606)).
- Uploading composed or mock-up screenshots to get the badge. The badge is earned by upload alone (inferred), but 2.3.3 requires the real app (forum paraphrase), and launch-week press described unoptimized apps as visibly letterboxed (third-party, [Macworld](https://www.macworld.com/article/3267488/6-iphone-duo-highs-and-lows-that-defined-my-day-one-experience.html)); the mismatch is what gets a rejection.
- Trusting the "19.5:9" label on the app preview page. Use the pixel figures.
- Taking simulator screenshots right after boot and getting black images (Apple known issue 187146039).
- Guessing fastlane / ASC API display-type values. Undocumented; say so.
- Assuming the April 2027 rule only applies to 27.1 SDK builds because the specs page says so. The news post says all submissions; Apple has not reconciled them.
- Treating "Duo screenshots uploaded" as "optimized". Apple's own tiers put optimization at the iOS 27.1 SDK, and the featuring wording asks for "support for all device poses".

## When to read the references

- `references/app-store-connect.md`: every screenshot and app preview number with its Apple URL, the badge wording, the submission facts (launch screen, scene lifecycle, Larger Text, icon, analytics, capability flags), and the automation gaps. Read it before quoting any size.
- `references/release-checklist.md`: the item-by-item checklist to walk the user through, with the audit rule id or Apple source for each item.
- `references/april-2027.md`: the two Apple quotes side by side, the forum thread, the Upcoming Requirements page state, what is and is not known, and the inferred safe plan.

## Related skills

- duo-audit: run the scanner first; DUO-008/009/010/019/020 are the submission-relevant rules.
- duo-bars: make vertical bars right before shipping an iOS 27.1 SDK build.
- duo-layout and duo-scenes: the layout and lifecycle work that makes the screenshots honest.
- duo-test: Device Hub poses, the simulator capture script, what cannot be automated.
- duo-design: the HIG rubric for judging whether "all device poses" is a true claim.
- duo-backend: logging your own Duo properties because App Store Connect analytics has no Duo breakdown.
- duo-crossplatform: React Native, Flutter, Capacitor and Unity scene-lifecycle and build fixes before submission.
