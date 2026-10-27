# Apple sources

Last checked: 2026-10-26

Re-fetched on that date and confirmed to resolve and match the descriptions below: the Technology Overview (via its `.md` endpoint), the Three steps page, the Oct 5 2026 Developer News post, the ASC screenshot specifications, Developer Forums thread 847644, the Xcode 27.1 release notes (via its `.md` endpoint), and the `ArrangementView` reference (via its `.md` endpoint; availability iOS 27.1.0). Other URLs were last checked during the research that produced this list, also dated 2026-10-26.

Every Apple URL this repo relies on, with a one-line description of what it contains. Pages are grouped by kind. Where a page was referenced but not fetched, or returned an error, that is stated in the description.

Two things to know before you open these links:

- Pages on developer.apple.com are JavaScript-rendered. A plain fetch may return little or nothing. Some pages also expose a Markdown (`.md`) endpoint; the Technology Overview, the Xcode 27.1 release notes and the `ArrangementView` reference were read that way, and the HIG Layout observation below came from a fetched Markdown version of the page.
- Tech Talk quotations in this repo come from transcript summaries. API names and numbers are preserved, but prose wording should be re-checked against the video page before quoting it as verbatim.

Labels: "Apple" means the fact is confirmed on an Apple page, Tech Talk, release note, Newsroom post, or an Apple engineer's Developer Forums post (the DTS "Summary of the iPhone Duo Group Lab", thread 847644, counts as Apple). "third-party, unverified" marks a detail that came from a non-Apple source. "inferred" marks a conclusion drawn from the sources rather than stated by them.

## Technology Overview and hub pages

- https://developer.apple.com/iphone-duo/ — "Get ready for iPhone Duo" developer hub: six Tech Talks, Group Labs, workshops, Q&As, docs, App Store links; mentions the "Made for iPhone Duo" badge.
- https://developer.apple.com/iphone-duo/prepare/ — "Three steps to make your app shine on iPhone Duo": App Resizability skill, grep-able anti-patterns, test environments, SDK tiers, App Store "Go further".
- https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo — Technology Overview "Preparing your app for iPhone Duo": layout/resizing, vertical bars, bar items, arrangement views, reserved regions, camera.
- https://developer.apple.com/hello/october26/ — Hello Developer October 2026: new Duo docs, Group Labs round 2, workshops.
- https://developer.apple.com/events/view/upcoming-events?formats=inperson — In-person "Optimize your app for iPhone Duo" workshops listing.
- https://developer.apple.com/design/resources/ — Apple Design Resources (Figma/Sketch kits, including Duo templates per the hub).
- https://developer.apple.com/app-store/asset-best-practices/ — App Store asset best practices (referenced from hub).

## Human Interface Guidelines

- https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo — HIG "Designing for iPhone Duo" (new Sept 9, 2026; change log: "September 9, 2026 | New page"): poses, best practices, reserved regions, split/arrangement views, vertical controls. Contains no numeric point/pixel dimensions for either display, no margin values, and no hinge/fold width in points.
- https://developer.apple.com/design/human-interface-guidelines/layout — HIG Layout: "Determine layout based on size classes, not device type or orientation"; updated Sept 9, 2026. The fetched Markdown contains no device table.
- https://developer.apple.com/design/human-interface-guidelines/designing-for-ios — HIG Designing for iOS (no Duo mention; still applies per the Duo page).
- https://developer.apple.com/design/human-interface-guidelines/toolbars — HIG Toolbars (no Duo mention; last change Dec 16, 2025).
- https://developer.apple.com/design/human-interface-guidelines/tab-bars — HIG Tab bars (no Duo mention; June 8, 2026 change log).
- https://developer.apple.com/design/human-interface-guidelines/multitasking — HIG Multitasking (no Duo mention).
- https://developer.apple.com/design/human-interface-guidelines/split-views — HIG Split views (no Duo mention).
- https://developer.apple.com/design/human-interface-guidelines/sheets — HIG Sheets (no Duo mention; March 24, 2026 change log).
- https://developer.apple.com/design/human-interface-guidelines/designing-for-games — HIG Designing for games (no Duo mention; Duo game rules live on the Duo page).
- https://developer.apple.com/design/human-interface-guidelines/app-icons — HIG App icons (no Duo mention; 1024×1024 spec unchanged; last change "June 8, 2026 | Refined guidance for Liquid Glass").
- https://developer.apple.com/design/human-interface-guidelines/live-activities — HIG Live Activities: Oct 13, 2026 "limited width" 28pt guidance, `isDynamicIslandLimitedInWidth`. The page never names Duo; the connection to Duo is inferred.

## Tech Talks 111461–111466

All six went live on September 9, 2026 (Apple). Speakers are given only where the transcript summary named them.

- https://developer.apple.com/videos/play/tech-talks/111461/ — Tech Talk "Prepare your app for iPhone Duo" (10:10; David Jackson, UI Frameworks): SDK tiers, size classes, `UIScreen.main`, safe areas, App Resizability. Chapters: 0:30 Build with the latest SDK, 1:17 Get started in Xcode, 1:33 Adopt flexible layouts, 2:46 Use size classes, 3:57 Avoid screen assumptions, 5:01 Adopt standard navigation, 6:06 Respect safe areas, 8:08 Use reserved regions, 9:12 Next steps.
- https://developer.apple.com/videos/play/tech-talks/111462/ — Tech Talk "Raise the bar with iPhone Duo" (15:43; Anna, UI Frameworks; Maria, HI Design): vertical bar APIs. Chapters: 0:28 Why bars move, 2:00 Opt in, 3:09 Shared bar region, 4:29 Order items, 5:56 Prepare toolbar content, 8:00 Control axis, 9:00 Prefer symbol-only, 10:07 Adapt custom views, 11:40 Overflow menu, 13:10 Visibility priority, 14:21 When to opt out.
- https://developer.apple.com/videos/play/tech-talks/111463/ — Tech Talk "Strike a pose with adaptive layouts on iPhone Duo" (18:01): reserved regions, displacement, ArrangementView. Names "Book pose" (partially folded) and "Table pose" (propped up).
- https://developer.apple.com/videos/play/tech-talks/111464/ — Tech Talk "Leverage multiple displays and scenes on iPhone Duo" (7:17): hinge, Split View, multiple scenes, scene accessories.
- https://developer.apple.com/videos/play/tech-talks/111465/ — Tech Talk "Build a great camera experience for iPhone Duo" (9:27): two front cameras, Virtual Front Camera, direction coordinator.
- https://developer.apple.com/videos/play/tech-talks/111466/ — Tech Talk "Design for iPhone Duo" (10:45; Apple Design).

None of the six Tech Talk pages links sample code (Apple).

## Other Apple videos

- https://developer.apple.com/videos/all-videos/?q=Duo — Apple video index listing durations and Group Lab replays 285–288.
- https://developer.apple.com/videos/play/meet-with-apple/285/ — iPhone Duo Group Lab Day 1 replay (59:28).
- https://developer.apple.com/videos/play/meet-with-apple/287/ — iPhone Duo Group Lab Day 3 replay (61:48).
- https://developer.apple.com/videos/play/wwdc2026/278/ — WWDC26 "Modernize your UIKit app" (origin of the App Resizability skill; referenced, not fetched).
- https://developer.apple.com/videos/play/wwdc2025/282/ — WWDC25 "Make your UIKit app more flexible" (referenced by the Technology Overview).
- https://developer.apple.com/videos/play/wwdc2026/222/ — WWDC26 session 222: MetricKit additions in iOS 27 (no pose data).
- https://developer.apple.com/videos/play/wwdc2026/204/ — WWDC26 session 204: Safari 27 features (no foldable APIs).

## Developer Forums threads

Threads with an Apple engineer or DTS reply count as Apple. Threads without an Apple reply are listed because they document an open question.

- https://developer.apple.com/forums/thread/847644 — DTS "A Summary of the iPhone Duo Group Lab" (locked; richest official written Q&A on poses, continuity, bars, web, accessibility). Establishes: no single pose API; hinge changes are geometry/trait changes; new APIs available on any iPhone or iPad running iOS 27.1+; the inner display ignores supported orientations; opening/closing is a size-class and trait change, not a scene disconnect; Safari's Viewport Segments and Device Posture APIs are opt-in experimental features in iOS 27.1.
- https://developer.apple.com/forums/thread/847838 — DTS answer on ScenePhase during fold (multi-window scene becomes inactive then backgrounded).
- https://developer.apple.com/forums/thread/847945 — Apple Frameworks Engineer: idiom stays `.phone`; iPad target not required.
- https://developer.apple.com/forums/thread/847912 — Apple Frameworks Engineer: sidebars are opt-in via `tabBarController.sidebar.preferredPlacement = .sidebar`.
- https://developer.apple.com/forums/thread/847887 — DTS reply on compatibility behaviour of unadopted apps; "iPad apps don't run in compatibility mode on iPhone Duo, unlike on Apple Vision Pro"; "not every app needs to use Arrangement Views or the reserved regions API".
- https://developer.apple.com/forums/thread/847883 — Developer request for programmatic simulator fold (no Apple reply; `simctl io screenshot` LCD-1 2007×2853).
- https://developer.apple.com/forums/thread/847137 — Duo simulator missing until runtime re-download.
- https://developer.apple.com/forums/thread/851106 — Unanswered question on April 2027 screenshot scope conflict.
- https://developer.apple.com/forums/thread/731974 — Pre-Duo Xcode Cloud test destinations answer.
- https://developer.apple.com/forums/thread/775774 — DTS on crash reports vs `MXCrashDiagnostic`.
- https://developer.apple.com/forums/thread/834805 — Anecdotal per-app memory cap on 12 GB iPhones.
- https://developer.apple.com/forums/activities/1659080 — Photos & Camera Duo Q&A listing (ended). A thread here requested a `UIRequiresFixedInterfaceOrientation` key; none exists.
- https://developer.apple.com/forums/activities/1664080 — SwiftUI Duo Q&A listing (ended). A thread here reports "XCUITest accessibility snapshot reports stale frames during live scene resize".
- https://developer.apple.com/forums/activities/1670080 — UIKit Duo Q&A listing (ended). A question about `ReservedRegion` inside keyboard extensions had no Apple answer.

## Developer News

- https://developer.apple.com/news/?id=nyuppv9r — Developer News, Sept 18 2026: Xcode 27.1 beta "Build for iPhone Duo with new resources".
- https://developer.apple.com/news/?id=kkphp5qo — Developer News, Oct 5 2026: "Prepare and submit your apps for iPhone Duo" (badge, April 2027, preview tool).
- https://developer.apple.com/news/upcoming-requirements/ — Upcoming requirements page (does not yet list the April 2027 Duo screenshot rule; fetched 2026-10-26).

## Release notes, software releases and technotes

- https://developer.apple.com/news/releases?id=10152026a — Software release: Xcode 27.1 (27A9275), October 15, 2026.
- https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes — Xcode 27.1 release notes: SDK list, macOS 26.6 requirement, Previews Display group, simulator known issues, Catalyst issues.
- https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes — Xcode 27.2 RC release notes: Device Hub additions, further Duo simulator known issues.
- https://developer.apple.com/go/?id=xcode-27_1-sdk-rn — Redirect to the Xcode 27.1 release notes.
- https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key — TN3192 (rev. 2026-10-09): `UIRequiresFullScreen` discrete resizing, scene geometry APIs, launch screen requirement.
- https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27_1-release-notes — iOS 27.1 release notes (returned 404 at research time).

## Xcode and Device Hub documentation

- https://developer.apple.com/documentation/xcode/device-hub — Device Hub overview.
- https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub — Device Hub controls including the Closed / Partially Open / Open buttons and Option-drag hinge slider.
- https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices — Running on simulated or physical devices (referenced).
- https://developer.apple.com/documentation/xcuiautomation/xcuidevice — `XCUIDevice` reference (no hinge/fold API).

## API reference pages

SwiftUI:

- https://developer.apple.com/documentation/swiftui/arrangementview — `ArrangementView` reference (styles, modifiers, examples).
- https://developer.apple.com/documentation/swiftui/view/onhingechange(isenabled:_:) — `onHingeChange(isEnabled:_:)` reference.
- https://developer.apple.com/documentation/swiftui/devicehinge — `DeviceHinge` reference with example.
- https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:) — `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)` reference.
- https://developer.apple.com/documentation/swiftui/cameracaptureaccessory — `CameraCaptureAccessory` reference.
- https://developer.apple.com/documentation/swiftui/view/toolbarverticalbehavior(_:) — `toolbarVerticalBehavior(_:)` reference (URL reported by a third party).

UIKit:

- https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller — `UIArrangementViewController` reference.
- https://developer.apple.com/documentation/uikit/uihingeinteraction — `UIHingeInteraction` reference with example.
- https://developer.apple.com/documentation/uikit/uihinge — `UIHinge` reference (`angle` in radians, `status`).
- https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:) — `UIView.reservedRegions(kind:options:)` reference.
- https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge — `UITraitCollection.verticalBarEdge` reference.
- https://developer.apple.com/documentation/uikit/uisceneaccessory — `UISceneAccessory` reference (iOS 27.0+).

AVKit, AVFoundation and others:

- https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces — AVKit article: `AVCaptureDeviceDirectionCoordinator`, descriptors, mirroring rules. Note the module: a guessed AVFoundation URL for this article returned 404.
- https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo — AVFoundation article: `UISceneAccessory.cameraCapture`, registration, session role, no Info.plist entry.
- https://developer.apple.com/documentation/widgetkit — WidgetKit (generic; no Duo content).
- https://developer.apple.com/documentation/activitykit — ActivityKit (generic; no Duo content).

## App Store Connect help pages

- https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications — ASC screenshot specifications (Duo sizes, April 2027 wording, badge).
- https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications — ASC app preview specifications (Duo 886×1920 / 1920×886).
- https://developer.apple.com/help/app-store-connect/manage-app-information/upload-app-previews-and-screenshots — ASC help on uploading previews and screenshots (no Duo text captured).
- https://developer.apple.com/help/app-store-connect/reference/reporting/app-analytics-filters-and-dimensions/ — ASC analytics Device dimension values (no Duo).

## Newsroom and specs

- https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/ — Newsroom, Sept 9 2026: hardware, displays, iOS 27.1, pricing, Apple Pencil "later this year".
- https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/ — Newsroom, Oct 22 2026: 60+ optimized apps, "Made for iPhone Duo" badge, workshops in 19 cities.
- https://www.apple.com/iphone-duo/specs/ — iPhone Duo technical specifications (pixel resolutions, ppi, cameras, Touch ID, dimensions).

## Keeping this file current

Apple updates these pages. If you notice a change, open an issue with the URL and the diff, or a PR that updates the affected reference and the "Last checked" date at the top of this file. See CONTRIBUTING.md.
