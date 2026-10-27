# iPhone Duo design review rubric

Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

Score a design, a set of mockups, or screenshots against the criteria below. Every criterion is tied to a sentence Apple published; the sentence is the standard, the criterion is only a restatement you can tick. Where Apple published no rule, the rubric says "no Apple rule" rather than inventing one.

## Contents

1. How to score
2. Section A: Resizing fundamentals
3. Section B: Consistency across displays and poses
4. Section C: Fold transitions and reserved regions
5. Section D: Vertical bars
6. Section E: Outer display and system surfaces
7. Section F: Games
8. Section G: Accessibility
9. Section H: App Store assets
10. Report template
11. Things this rubric deliberately does not score

## 1. How to score

- Mark each criterion **Pass**, **Fail**, **Unclear** (the material does not show it; name what you need to see), or **N/A** (the app has no such element). Never guess a Pass from a single screenshot when the criterion is about behaviour across poses.
- Criteria marked **Blocker** restate an explicit Apple "don't" or a bolded HIG best practice. A Fail on a Blocker should lead the report. Criteria marked **Refinement** restate Apple advice phrased as "consider", "prefer", or an example.
- The summary line is "N of M applicable criteria pass; B blockers failing". This counting convention is ours, not Apple's; the sentences are Apple's.
- Quote the Apple sentence next to every Fail so the designer can check the source. URLs are in `hig-verbatim.md`.
- What you need from the reviewer to score well: the compact-width (closed) screens, the regular-width (open) screens in both rotations, and a note or frame for the partially folded state. If only one of those exists, most of section B and C will be Unclear; say so instead of scoring them.

Short citation keys used below:
HIG = [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo); HIG-L = [HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout); TO = [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo); 3S = [Three steps](https://developer.apple.com/iphone-duo/prepare/); TT61/62/63/64/66 = Tech Talks [111461](https://developer.apple.com/videos/play/tech-talks/111461/), [111462](https://developer.apple.com/videos/play/tech-talks/111462/), [111463](https://developer.apple.com/videos/play/tech-talks/111463/), [111464](https://developer.apple.com/videos/play/tech-talks/111464/), [111466](https://developer.apple.com/videos/play/tech-talks/111466/); GL = [Group Lab summary, Developer Forums 847644](https://developer.apple.com/forums/thread/847644).

## 2. Section A: Resizing fundamentals

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| A1 | The design has exactly two base layouts: a compact-width layout for the outer display and a regular-width layout for the inner display, and the regular layout is the compact layout expanded, not a different app. | "A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose. Don't reinvent your app when it resizes; allow the existing layout to expand based on the available space instead." (HIG) | Blocker |
| A2 | No element has a fixed width or a position tied to one display's dimensions; layout is expressed with margins and safe area insets. | "Use size classes, layout margins, and safe area insets to lay out controls and content. Avoid fixed widths and display-specific dependencies." (HIG) "Avoid fixed widths, breakpoints, and screen-specific metrics." (TT66) | Blocker |
| A3 | Layout decisions are stated in terms of size class, not "iPhone vs iPad", not orientation, and not pose. | "Determine layout based on size classes, not device type or orientation." (HIG-L) "Don't choose a layout by idiom." "Don't treat 'regular width' as 'iPad.'" (3S) | Blocker |
| A4 | Insets are specified per edge; the spec does not assume the leading and trailing (or top and bottom) insets are equal. | "Safe areas and layout margins are often asymmetric on iPhone Duo, so avoid assuming that insets on opposite sides are equal." (TT61) | Blocker |
| A5 | Hero images and video specify fill vs fit per size class or aspect ratio, or carry a focal point. | "Hero images and video set to `.scaleAspectFill` or `.aspectRatio(contentMode: .fill)` can lose important content on wider displays. Use the current size classes or aspect ratio to choose between fill and fit, or set a focal point." (3S) | Blocker |
| A6 | The regular-width layout reads as "a natural extension" of what the app does on iPad (if it has an iPad layout), while remaining recognisably an iPhone app. | "On the inner display, your app should look like a natural extension of its iPad layout." (3S) "its idiom ... remains the same: keep the layout recognizable and familiar to the platform even when resizing." (HIG-L) | Refinement |
| A7 | The design accounts for Split View on the inner display (two apps side by side, "a 50/50 layout") without a third layout. | "your app can appear at many different sizes" (HIG); Split View is "a 50/50 layout started from the home gesture." (TT66) | Refinement |

## 3. Section B: Consistency across displays and poses

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| B1 | Every feature available on the outer display is available on the inner display and vice versa. | "Keep functionality and the state of elements the same between displays." (HIG) | Blocker |
| B2 | Element state (selection, scroll position, edit in progress, playback) carries over when the device opens or closes; the design does not reset to a home screen. | Same sentence as B1; "Opening or closing the device ... is treated as a size-class and trait change, not a scene disconnect or app termination." (GL) | Blocker |
| B3 | The information hierarchy is the same on both displays; the inner display may show one extra level side by side (Mail: list or message closed, both open). | "Maintain your app's information hierarchy, but show an additional level of hierarchy on the larger inner display if it makes sense for your content. Mail, for example, shows either a list of emails (primary) or an email (secondary) when the device is closed. When it's open, it shows both side by side." (HIG) | Refinement |
| B4 | No control or content exists in only one pose. Controls may move to an overflow menu, but never disappear. | "Provide access to the same controls and content regardless of how someone holds or views the device." (HIG) "Don't tie functionality to a pose." (TT66) "Don't change your app's functionality based on the space it occupies." (HIG-L) | Blocker |
| B5 | If the design has a seated or hands-free variant (for example video on top, controls below when propped up), it keeps the same controls and hierarchy as every other pose. | "An optional special layout can suit seated, hands-free use, but it must keep the same controls and hierarchy as other poses." (TT66) | Blocker |
| B6 | Controls keep roughly the same relative positions across poses. | "keep controls' relative positions as similar as possible so people don't have to relearn where actions live as they change between poses." (HIG) | Refinement |
| B7 | The design does not require the user to rotate the device to reach a layout; it does not assume the inner display can be locked to one orientation. | "The inner display doesn't honor your supported interface orientations." (TT61) "There is no sanctioned way to lock the inner display to portrait." (GL) | Blocker |

## 4. Section C: Fold transitions and reserved regions

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| C1 | When the device is partially folded, the layout is held by a container that adapts on its own (split view, arrangement view, system sheet/alert/menu), or the spec names what moves. | "Adapt your layout when the device folds. Prefer a layout container that adapts automatically, like the split view in Notes that adjusts the width of each pane to stay clearly visible as the device folds." (HIG) | Blocker |
| C2 | Grids on the inner display use an even number of columns. | "In a grid-style layout, prefer an even number of columns so content divides cleanly." (HIG) "prefer an even number of grid columns whenever a division region is present, whether or not it is currently active." (TT63) | Blocker |
| C3 | No interactive element or important content sits across the centre of the inner display in the folded state; custom components that would are flagged for the `ReservedRegion` API. | "Use the `ReservedRegion` API to keep important elements clear of the center if the system doesn't move them automatically." (HIG) "Identify elements or controls in your views that appear in the fold, and are difficult to see or interact with." (TO) | Blocker |
| C4 | The folded layout differs from the flat layout by small adjustments, not a rearrangement; nothing disappears. | "Avoid extreme layout changes as people fold the device. Move only what's necessary to keep elements visible and easy to tap. Controls that disappear or shift dramatically are harder to find and track, so favor small adjustments over rearrangement." (HIG) | Blocker |
| C5 | Scrolling content (feeds, articles, documents, lists) is not displaced around the fold. | "Continuous scrolling content (articles, feeds, documents, lists) does not displace. It already adapts through scrolling, and moving it can interrupt continuity." (TT63) | Refinement |
| C6 | Where the design places elements for the folded state, book pose puts alerts on the trailing side; table pose puts viewing content on top and interactive controls on the bottom. | "Book pose (partially folded): alerts move to the trailing side, closer to where they will appear when the device closes." "Table pose (propped up): the top region suits content viewed at a distance, such as an alert. The bottom region suits interactive controls, such as media controls." (TT63) | Refinement |
| C7 | Elements that work as a unit move together; independent elements move independently; the amount of movement is minimal. | Move elements "independently when they can adapt alone, and together when they work as a unit." "Avoid excessive movement." (TT63) | Refinement |
| C8 | Two-pane layouts become an even split when folded. | Reminders "keeps both columns visible in an even 50/50 split"; Notes' leading pane "is the same width as the trailing pane" when partially folded. (TT63, HIG) | Refinement |
| C9 | Custom bottom sheets or floating panels have a folded-state behaviour; the spec does not assume safe areas handle the fold. | "Custom bottom sheets need fold avoidance using reserved regions. Safe-area insets alone are not enough." (GL) | Blocker |
| C10 | Any primary/secondary pairing (player over controls, main/detail) is a candidate for an arrangement view, and navigation containers sit outside it. | "Consider an arrangement view when your layout already resembles one." "Keep navigation outside of arrangement views." (HIG) | Refinement |
| C11 | The design does not specify behaviour at a hinge angle, and hinge data is used only for effects. | "Hinge data is ideal for driving interactions and effects. For layout decisions, use the arrangement and region APIs." (TT64) "don't depend on specific values." (GL) | Blocker |

## 5. Section D: Vertical bars

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| D1 | Navigation, toolbar, and tab items are drawn as system bars that move to the side on the outer display and in inner-display landscape, not as a custom bar fixed at the top or bottom. | "Follow the system's vertical layout for toolbars, tab bars, and navigation controls." (HIG) "Content from custom `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered." (TT62) | Blocker |
| D2 | The compact-width mockup shows the side column in Apple's order: Dynamic Island, status bar, toolbar (including navigation buttons), tab bar. | "Controls on the side include both system and app elements: the Dynamic Island, the status bar, the toolbar (including navigation buttons), and the tab bar." (HIG) | Refinement |
| D3 | Every bar item has a symbol and a title; text-only buttons are rare and the design accepts that they stay in the horizontal nav bar. | "Keep text-based buttons to a minimum." "Provide both a title and a symbol for each toolbar item that isn't text-only." (HIG) "If your item has a title and doesn't have an icon, the system doesn't present it vertically." (TO) | Blocker |
| D4 | No segmented controls or custom views are expected in the side column. | "Items too wide for the side space, such as text buttons or segmented controls, stay in the nav bar." (TT66) "If your item uses a custom view rather than a title or icon, the system doesn't present it vertically." (TO) | Blocker |
| D5 | Back or Close is at the top of the side column, followed by the prominent action (Done). | "Reserve the top for primary navigation controls, like Back or Close, followed by prominent actions, such as Done." (TO) | Refinement |
| D6 | Related items are grouped; no manual spacing or spacers are drawn between bar items. | "Group related toolbar items instead of spacing them manually... avoid adding fixed spacing yourself." (HIG) "Don't add extra spacing, whether the bar is horizontal or vertical." (TT62) | Blocker |
| D7 | Overflow uses the system menu with the ellipsis symbol; the app has no overflow menu of its own, and other menus use a distinct symbol. | "If your app has its own overflow menu, move those actions into the system menu." "Reserve the ellipsis symbol for overflow, and give other menus a distinct symbol." (HIG) | Blocker |
| D8 | Counts are shown as badges, not inline text in bar items. | Use badges instead of inline counts. (TT62) | Refinement |
| D9 | The design does not override the default bar placement, except for a Calculator-style single-page bottom-heavy layout or a single-item sheet, and the choice is the same on every screen. | "In general, don't override the default bar placement. The position of controls on the vertical axis is one of the core patterns of iPhone Duo." (HIG) Opt-out cases: "Single-page, bottom-heavy layouts such as Calculator" or "Control-heavy sheets with only one item." (TT62) | Blocker |
| D10 | If a screen uses the full display width without bars, nothing overlaps the Dynamic Island or the status bar, and interactive elements are not blocked. | "Consider using the full display width for interfaces where bars aren't necessary... as long as nothing conflicts with the Dynamic Island or the status bar." (HIG) "Immersive, non-scrolling interfaces can center on the full display if interactive elements aren't blocked. Mixing approaches is also fine, such as a full-width header with inset scrollable content." (TT66) | Blocker |
| D11 | Sheets on the outer display are drawn with vertical controls (unless a single-button sheet opts out); sheets on the inner display with horizontal bars; sheets move away from the fold. | "On the outer display, the system presents bars vertically for sheets by default." "For sheets on the inner display, the system presents the toolbar horizontally for centered or leading placements, and vertically for trailing placements." (TO) "When the device is folded, sheets slide away from the fold." (TT66) | Refinement |
| D12 | Inspectors and the sidebar/content columns of a split view keep horizontal bars; only the detail column goes vertical. | "The system presents bars in inspectors horizontally." "the system shows bars horizontally for the sidebar or content view, and vertically for the detail view." (TO) | Refinement |
| D13 | In Split View multitasking, the design tolerates controls on either hardware side. | "each one places controls along its outer edge, so the left app has controls on the left." (HIG) | Refinement |
| D14 | Tab apps that want a sidebar on the inner display say so explicitly; the design does not assume a sidebar appears by default. | "By default, iPhone Duo (and all other iPhones) will not show a sidebar for `UITabBarController` apps, even when its horizontal size class is regular. Sidebars are opt-in" ([Developer Forums 847912](https://developer.apple.com/forums/thread/847912)) | Refinement |

## 6. Section E: Outer display and system surfaces

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| E1 | The compact-width layout is a full iPhone UI that works with content offset from the side column; it is not a watch-style glance surface. | "Most content needs an offset so it isn't hidden behind side controls. Safe area insets handle this automatically." (TT66) "you're still designing for iPhone" (HIG) | Blocker |
| E2 | The design does not plan to show app content on the outer display while the device is open, except as a camera capture accessory during an active capture session. | "Non-camera apps can't draw directly on the outer display." "`CameraCaptureAccessory` appears only while the app is foregrounded with an active capture session." (GL) Conditions: "The app is full screen on the inner display. The app has an active camera session." (TT64) | Blocker |
| E3 | If the app has a Live Activity, its compact and minimal presentations fit a 28pt-diameter circle with a leading view only, and the design accepts that the camera region expands into the Dynamic Island. | "adapt your compact and minimal presentations to fit inside a 28pt-diameter circle... adopt a leading view only" ([HIG Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities); page does not name Duo, link is inferred). "The camera region expands into the Dynamic Island." (GL) | Refinement |
| E4 | Live Activities implement every presentation; widgets use standard families with no Duo-specific size. | "Live Activities must implement compact, minimal, expanded, and Lock Screen presentations." Widget families "systemSmall, systemMedium, systemLarge, systemExtraLargePortrait, accessoryCircular, accessoryRectangular, and accessoryInline." (GL) | Refinement |
| E5 | Landscape on the outer display is supported and designed, since people stand the closed device like a tent. | "Landscape support is still valuable on the outer display, since people may use the device like a tent." (TT61) | Refinement |
| E6 | Any animation can start, pause, and stop at any moment (a fold can interrupt it). | "Animations should be able to start, pause, and stop at any point." (GL) | Refinement |

No Apple rule: Lock Screen, StandBy, Always On, keyboard, Apple Pencil, and Camera Control have no Duo-specific design guidance. Apple only states facts: "Lock Screen controls, the Dock, and app navigation move to the side"; "StandBy works on either display even when it's not charging"; "Accessory bars stay attached to the keyboard and don't move to the vertical axis" (TT62). Do not score what Apple has not ruled on.

## 7. Section F: Games

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| F1 | The game fills the screen in every pose, including after the device opens or closes. An orientation lock is allowed, but it does not excuse an unfilled screen. | "You can choose to lock to either portrait or landscape orientation, but be sure to fill the screen as the device pose changes." (HIG) | Blocker |
| F2 | The design changes aspect ratio rather than letterboxing or pillarboxing; where padding is unavoidable, it contains artwork. | "Prefer changing the aspect ratio over letterboxing or pillarboxing in games; if you can't avoid letterboxing or pillarboxing, add artwork to the padding area to help the experience feel full screen." (HIG) | Blocker |
| F3 | Text and control sizes stay as consistent as possible between the two displays. | "When resizing, keep text and control sizes as consistent as possible." (HIG) | Refinement |
| F4 | The game is playable, not just visible, in every pose. | "Make your game playable in every device pose." (HIG) | Blocker |
| F5 | The design does not rely on `UIRequiresFullScreen` to avoid resizing. | "Use `UIRequiresFullScreen` for immersive apps. The app still resizes." (GL) | Refinement |

## 8. Section G: Accessibility

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| G1 | Dynamic Type reflows in every layout; one-screen layouts do not pin text at the largest standard size. | "For one-screen layouts, don't hold text at the largest standard size. Let it reflow so it stays readable." "holding text at the largest standard size can fail App Store Connect's Larger Text criteria." (GL) | Blocker |
| G2 | Side-by-side content has a stacking behaviour at large text sizes. | "horizontally adjacent views may need to stack vertically." (HIG-L) | Refinement |
| G3 | Layouts that span the fold define a VoiceOver reading order (containers or sort priorities). | "Custom hinge-spanning layouts may need explicit containers or sort priorities." (GL) | Refinement |
| G4 | Content next to the side column stays legible with and without a bar background (Reduce Transparency). | "Vertical bars have no scroll-edge effect by default, but get a background when Reduce Transparency is enabled. Keep content legible either way." (TT62) | Refinement |
| G5 | Every bar item has a title (used by VoiceOver and in overflow). | "Even if your content is an image, it's still important to provide a title." (TT62) | Blocker |
| G6 | The accessibility test plan covers every pose in Device Hub and on hardware. | "Test Dynamic Type, contrast, VoiceOver, and resizing across poses using Xcode and Device Hub." (GL) Note: "VoiceOver, the Accessibility Inspector, and other accessibility tools cannot convey screen content on an iPhone Duo within Device Hub. (187148389)" ([Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)), so VoiceOver on Duo needs hardware. | Refinement |

## 9. Section H: App Store assets

| # | Criterion | Apple sentence | Severity |
|---|---|---|---|
| H1 | Duo screenshot frames exist at Apple's pixel sizes: outer 1398 × 2034 / 2034 × 1398, inner 2007 × 2853 / 2853 × 2007. | [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications) | Refinement now; required "Starting in April 2027" (scope wording differs between Apple pages; see duo-ship) |
| H2 | Screenshots show the app across orientations and poses. | "Share app previews and screenshots that highlight your app across orientations." (3S) | Refinement |
| H3 | The app icon is unchanged: no Duo-specific icon work is requested. | HIG App Icons has no Duo guidance; 1024 × 1024 px. | N/A unless someone asks for a "Duo icon" |

## 10. Report template

```
iPhone Duo design review: <app / screen set>
Material reviewed: <files, frames, screenshots, which poses were shown>
Not shown (scored Unclear): <compact / regular / folded / landscape>

Blockers failing (Apple "don't" or bolded best practice):
- <ID> <one line>. Apple: "<sentence>" (<source>). Fix: <one line>.

Refinements:
- <ID> <one line>. Apple: "<sentence>" (<source>).

Passes worth keeping: <IDs>

Not scorable from Apple's guidance: <what the reviewer asked that Apple has not ruled on, e.g. point dimensions, margins, fold width, angle thresholds>

Summary: <N> of <M> applicable criteria pass; <B> blockers failing.
```

## 11. Things this rubric deliberately does not score

- Point dimensions, margins, grid units, or fold width. Apple has published pixels (inner 1878 × 2670, outer 1398 × 2034; ASC screenshot sizes above) but no point dimensions; the 466 × 678 pt and 669 × 951 pt figures circulating are third-party simulator measurements (third-party, unverified). Do not fail a design for "wrong dimensions".
- Hinge-angle thresholds. None exist in Apple's guidance.
- Whether a pose detection is "correct". There is no pose API.
- Widget, keyboard, Apple Pencil, Lock Screen, StandBy, Always On, and Camera Control design. No Duo-specific HIG exists.
- App icon changes. None are asked for.
- Animation duration or curve of the fold transition. Not published.
