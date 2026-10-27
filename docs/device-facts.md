# iPhone Duo device facts

Last checked: 2026-10-26 (the Technology Overview, the Three steps page and the ASC screenshot specifications were re-fetched on this date and match the figures and wording quoted below)

Numbers, size classes, SDK tiers and dates, each with a Status column that says who established it. "Apple" means an Apple page, Tech Talk, release note, Newsroom post or Apple engineer's Developer Forums post. "third-party, unverified" means a blog, GitHub README, simulator measurement or press report that Apple has not confirmed. "inferred" means a conclusion drawn from the sources rather than stated by them. Never upgrade a guess to a fact; see CONTRIBUTING.md.

The headline: Apple publishes pixel resolutions and App Store Connect screenshot sizes. Apple has not published point dimensions, the vertical bar inset, the fold region width, hinge angle thresholds, the machine identifier, or RAM. Everything in points is third-party.

## Display and hardware facts

| Quantity | Value | Status |
|---|---|---|
| Inner panel | 1878×2670 px, 430 ppi, 7.6" (7.58" actual) | Apple (spec page) |
| Outer panel | 1398×2034 px, 460 ppi, 5.4" (5.36" actual) | Apple (spec page) |
| ASC screenshot, outer | 1398×2034 / 2034×1398 | Apple (App Store Connect) |
| ASC screenshot, inner | 2007×2853 / 2853×2007 | Apple (App Store Connect) |
| Outer points | 466×678 pt @3x | third-party, unverified (simulator profile) |
| Inner points | 669×951 pt @3x (951×669 landscape-native) | third-party, unverified (simulator profile); inferred (matches ASC) |
| Vertical bar inset | 84 pt, one-sided | third-party, unverified (simulator) |
| Fold division region | 40 pt wide (20 pt margins), active only when partially folded | third-party, unverified (simulator) |
| Device Hub hinge angles | Book = 127°, Open = 180° | third-party, unverified |
| Machine identifier | `iPhone19,4`; model A3447 (US); product class V68 | third-party, unverified (simulator profile, Geekbench, EveryMac) |
| RAM | 12 GB | third-party, unverified (single Geekbench entry; Apple does not publish) |

Sources: [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/); [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications); third-party figures from the Xcode 27.1 simulator display profile as read by [blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator), [iPhone-Duo-by-Examples](https://github.com/artemnovichkov/iPhone-Duo-by-Examples) and [skarol.dev](https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/).

Notes on the point figures:

- Inferred: the arithmetic supports the simulator figures. 669×3 = 2007 and 951×3 = 2853 match the ASC inner screenshot size exactly; 466×3 = 1398 and 678×3 = 2034 match the outer. The inner display therefore renders a 2007×2853 logical buffer that the 1878×2670 panel downsamples by about 6.4–6.9% per dimension.
- third-party, unverified: measured window sizes under the 27.1 SDK were closed 466×678 (content 382×562); open 951×669 (content 867×553, with a 40-pt inactive division at x=455); open and rotated 669×951 (content 669×734) ([blakecrosley.com](https://blakecrosley.com/blog/xcode-27-1-beta-iphone-duo-simulator)).
- third-party, unverified: an older 626×890 pt inner figure persists on iphoneduosupport.com (last verified 2026-09-15, before the simulator shipped) and in Progressier's browser simulator. Developers who ran the 27.1 simulator used 669×951 / 951×669, which supersedes it.
- Apple: the HIG Duo page contains no numeric point/pixel dimensions for either display, no margin values, and no hinge/fold width in points ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Apple: Device Hub documents its pose buttons as Closed / Partially Open / Open, and "To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel" ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)). The "Book" label and the 127°/180° angles are third-party, unverified. Prefer Apple's names.
- Apple: no angle thresholds separating poses exist in any Apple source; hinge "Update rate and precision are system policy, so don't depend on specific values" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

Other hardware facts, all Apple (spec page and Newsroom): both displays have Dynamic Island and ProMotion up to 120Hz; Touch ID in the side button (no Face ID); eSIM only; A20 Pro with 7‑core GPU; open dimensions 164.6 × 117.8 × 5.2 mm, closed 84.1 × 117.8 × 11.3 mm; 254 g; "3000 nits of peak outdoor brightness"; Always On; the outer display delivers "90 percent of the screen area of iPhone 18 Pro" and the inner is "50 percent larger than iPhone 18 Pro Max"; Apple Pencil (USB-C) support arrives "Later this year" ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/); [Apple Newsroom](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)). Cameras: outer "12MP Center Stage camera ƒ/2.2", inner "Under-display FaceTime camera ƒ/1.8", rear 48MP Fusion Main (26 mm ƒ/1.6) and 48MP Fusion Ultra Wide (13 mm ƒ/2.2, 120°).

Aspect ratio, inferred: 2670/1878 = 1.42 and 2853/2007 = 1.42 (inner), 2034/1398 = 1.45 (outer), versus roughly 2.17 on an iPhone 18 Pro (402×874 pt). Apple's own framing never uses "1.42"; its position is "Don't assume fixed ratios. Resize to fit each pose, favor changing aspect ratio over letterboxing, and add artwork to unavoidable padding" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## Size-class matrix

Apple, from Tech Talk 111461 ([Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/)):

| Display / pose | Horizontal size class | Vertical size class |
|---|---|---|
| Outer display, portrait | compact | regular ("like other iPhone models") |
| Outer display, landscape | compact | compact |
| Inner display, either rotation | regular | regular ("leaving room for sidebars") |

Related Apple statements:

- The device idiom is still `.phone`: "you are not required to support iPad to support the iPhone Duo as its device idiom is still `.phone`" ([Apple Developer Forums 847945](https://developer.apple.com/forums/thread/847945)). "iPhone Duo is not a separate device class ... iPhone Duo does not support Stage Manager and does not have its own `UIUserInterfaceIdiom`" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "The inner display doesn't honor supported interface orientations, so use size classes rather than orientation for layout decisions" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)). "There is no sanctioned way to lock the inner display to portrait" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "Don't treat 'regular width' as 'iPad.'" and "an iPhone app can have any combination of size classes" ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)).

## SDK tiers

What an app gets on the inner display depends on which SDK the binary links against, not its deployment target. Apple, from the Three steps page ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/)):

| Build SDK | Behaviour on iPhone Duo (Apple's wording) |
|---|---|
| iOS 26 SDK or earlier | "The app runs but appears centered on the inner display with empty space around it. Closed, it sits beside the status bar and camera." |
| iOS 27 SDK | "The app fills most of the inner display but still avoids the status bar." |
| iOS 27.1 SDK or later | "The app uses the full display, and toolbars and tab bars move vertically below the status bar. Before shipping with this SDK, confirm your content adapts to the vertical bars." |

Related Apple statements:

- Toolchain floor: "Xcode 27.1 includes Swift 6.4 and SDKs for iOS 27.1, iPadOS 27, tvOS 27, watchOS 27, macOS 27, and visionOS 27 ... Xcode 27.1 requires a Mac running macOS Tahoe 26.6 or later" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
- The new APIs are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo"; Apple recommends "gating iOS 27.1 APIs behind availability checks" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Compatibility mode for unadopted apps, per DTS: closed, the app uses the region outside the vertical bar; fully open, it is centered at a familiar aspect ratio with letterboxing; partially open, it is shifted to one side; "iPad apps don't run in compatibility mode on iPhone Duo, unlike on Apple Vision Pro" ([Apple Developer Forums 847887](https://developer.apple.com/forums/thread/847887); [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- There is no Info.plist key to request the older mode; compatibility depends on the build SDK. This comes from a third-party summary of Apple's UIKit Q&A ([Gubarenko, Q23](https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)).
- "Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store submission" ([Apple TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
- third-party, unverified: Xcode 27.2 beta did not include Duo support despite the higher number ([ecorpit](https://ecorpit.com/iphone-duo-sdk-new-apis-xcode-27-1-developer-guide-2026/)). Verify the SDK stamp with `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, which should read `sdk 27.1` ([blakecrosley.com](https://blakecrosley.com/blog/prepare-your-app-for-iphone-duo)).

## Timeline

| Event | Date | Status |
|---|---|---|
| iPhone Duo announced; HIG "Designing for iPhone Duo" published; Tech Talks 111461–111466 go live | September 9, 2026 | Apple ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo); [hub](https://developer.apple.com/iphone-duo/); [Newsroom](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)) |
| Xcode 27.1 beta announced | September 18, 2026 | Apple ([Developer News](https://developer.apple.com/news/?id=nyuppv9r)) |
| App Store Connect begins accepting Duo-optimized submissions | October 5, 2026 | Apple ([Developer News](https://developer.apple.com/news/?id=kkphp5qo)) |
| Xcode 27.1 final, build 27A9275 | October 15, 2026 | Apple ([Software Releases](https://developer.apple.com/news/releases?id=10152026a)) |
| Pre-orders open | October 16, 2026 | Apple ([Newsroom](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)) |
| Device ships with iOS 27.1, from $1,999 | October 23, 2026 | Apple ([Newsroom](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)) |
| Duo screenshots become required in App Store Connect | April 2027 | Apple ([Developer News](https://developer.apple.com/news/?id=kkphp5qo)); scope unresolved, see known-gaps.md |

third-party, unverified additions to the timeline: iOS 27.0/Xcode 27 shipped September 14 with no Duo SDK content; the 27.1 beta was build 27A9269; the October 5 RC was already 27A9275 ([blakecrosley.com](https://blakecrosley.com/blog/iphone-duo-for-developers)). MacRumors reports a day-one iOS 27.1 update (build 24A94425 replacing 24A94232) ([MacRumors](https://macrumors.com/2026/10/13/iphone-duo-day-one-update)). Apple's own iOS 27.1 release notes URL returned 404 at research time.
