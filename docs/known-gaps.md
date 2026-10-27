# Known gaps

Last checked: 2026-10-26 (the Oct 5 news post, the ASC screenshot specifications, and forum thread 847644 were re-fetched on this date and match the wording quoted below)

These are the things the duo-ready skills refuse to guess about: places where Apple has not published a number or a name, where two Apple pages disagree, or where the only source is third-party. If you can close one with an Apple source (a documentation page, Tech Talk, release note, Newsroom post, or an Apple engineer's Developer Forums reply), please open a PR that cites it and updates the affected reference and its "Last checked" date. See CONTRIBUTING.md.

Status labels: "Apple" means confirmed by Apple; "third-party, unverified" means it came from a blog, repo, simulator measurement or press report; "inferred" means a conclusion drawn from the sources; "Gap" means no source says.

| Item | What the sources say | Status |
|---|---|---|
| Point dimensions and scale factor | Apple publishes pixels only; 466×678 / 669×951 pt @3x are simulator-derived | third-party, unverified; consistent with ASC math |
| April 2027 screenshot scope | News post: "any apps or games submitted"; specs page: "any app using the iOS 27.1 SDK or later"; forum question unanswered; Upcoming Requirements page silent | Unresolved (Apple source vs Apple source) |
| Inner vs outer screenshot sets required | Not specified | Gap |
| App preview "19.5:9" label on the Duo row | Fits neither 1.42 nor 1.45 | Apple page error (Apple) |
| Orientation on the inner display | Apple's Group Lab thread 847644 gives two answers. To "Is there a sanctioned way to lock the inner display to portrait only?": "No. The inner display doesn't honor your supported interface orientations — avoid checking orientation for layout decisions and use size classes instead." To a compatibility-mode question: "Yes, iPhone Duo still honors UISupportedInterfaceOrientations, but the expected behavior for this device differs from previous iPhone devices in certain hinge states and orientations." | Apple vs Apple wording; operative guidance (matching Tech Talk 111461) is to use size classes and not rely on orientation locks on the inner display Tech Talk 111461 contains the same tension in consecutive sentences: "iPhone Duo respects your supported interface orientations, but your app will scale on the inner display, including in Split View multitasking" and "The inner display doesn't honor your supported interface orientations" (re-checked 2026-10-27). |
| `UIView.ReservedRegion` vs `UIViewReservedRegion` | Resolved 2026-10-26 from Apple's reference page: the Swift name is `UIView.ReservedRegion`; `UIViewReservedRegion` is the Objective-C name | Resolved (Apple) |
| `leftItemsSupplementBackButton` vs spoken `leftItemSupplementsBackButton` | Slide vs narration in Tech Talk 111462 | Verify in headers |
| `DeviceHinge.Status` / `UIHinge.Status` cases | Only `.partiallyOpen` in Apple code; `.closed`, `.fullyOpen`, `.unknown` third-party | Partially unverified |
| `ReservedRegion` member names (`isActive`, `frame`, `margins`, identifier) | Resolved 2026-10-26 from Apple's reference pages: SwiftUI `ReservedRegion` has `id`, `kind`, `frame: CGRect`, `margins: EdgeInsets`, `isActive: Bool`; `UIView.ReservedRegion` has `frame`, `isActive`, `kind`, `margins: UIEdgeInsets`. The frame already includes the margins | Resolved (Apple) |
| `AVCaptureDeviceDirectionCoordinator` init signature and availability; presence in beta headers | Inferred from Apple example; one repo found it absent from 27A9269 headers | Verify against 27A9275 |
| `UIVerticalBarEdge` / `UIVerticalBarBehavior` cases beyond `.disabled` | Not enumerated in fetched payloads | Gap |
| Device Hub button names | Apple docs: Closed / Partially Open / Open; Crosley: Closed / Book / Open with 127°/180° | Prefer Apple names; angles third-party, unverified |
| `xcodebuild -destination name=` string for Duo | Not recorded anywhere | Confirm via `xcrun simctl list devicetypes` |
| `simctl` / XCUITest pose control | None; forum request unanswered | Use community tools, label unsupported |
| 626×890 vs 669×951 inner points | Older third-party figure superseded by simulator measurement | Use 669×951 |
| `contentMargins(for: .container)` as Duo API | Only in one community repo | Unverified |
| Split View exact point sizes; three-column split views on inner display | Not stated by Apple | Gap |
| RAM (12 GB) and per-app memory cap (~6 GB) | Geekbench and forum anecdotes | third-party, unverified |
| iOS 27.1 public release notes / release date for non-Duo iPhones | URL 404; press says 27.1 shipped Duo-only initially | Gap |
| Whether fold ever triggers `sceneWillResignActive`/background | Not stated except the multi-window DTS answer | Gap |
| Fastlane / ASC API `ScreenshotDisplayType` values for Duo | fastlane 2.241.1 (2026-10-15, PR #30444) added `APP_IPHONE_DUO` with the four Duo sizes; Apple's API documentation for the value was not located | Partly resolved (third-party source code) |
| Safari 27.1 flag names; WKWebView exposure of fold APIs; `env(safe-area-inset-*)` with vertical bars | Not documented | Gap |

Where to look for each item:

- April 2027 scope: [Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo); [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications); [Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106); [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/).
- App preview label: [ASC app preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications).
- Orientation on the inner display: [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644) (both quotations); [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/); [TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key) on how the system intersects supported orientations with what the device supports.
- Reserved region spelling and members: [UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)); [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/).
- Bar item property name: [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/).
- Hinge status cases: [DeviceHinge](https://developer.apple.com/documentation/swiftui/devicehinge); [UIHinge](https://developer.apple.com/documentation/uikit/uihinge).
- Camera coordinator: [Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces); [Tech Talk 111465](https://developer.apple.com/videos/play/tech-talks/111465/).
- Device Hub names: [Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub).
- Simulator pose control: [Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883); [XCUIDevice](https://developer.apple.com/documentation/xcuiautomation/xcuidevice).
- Fold and scene lifecycle: [Apple Developer Forums 847838](https://developer.apple.com/forums/thread/847838); [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644).
- Web APIs: [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644) (Viewport Segments and Device Posture are opt-in experimental features in iOS 27.1, enabled at Settings > Apps > Safari > Advanced > Feature Flags; the flag names themselves were not captured).
