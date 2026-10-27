# Apple's design rules for iPhone Duo, quoted

Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

Every quotation below is Apple's own text, copied from the page named in the citation. The HIG page and the Technology Overview were read as published text. Tech Talk quotations (111461, 111462, 111463, 111464, 111466) and Group Lab quotations (Developer Forums thread 847644) come from transcript summaries; API names and numbers are preserved, but re-check the prose wording against the video page before quoting it as verbatim in a document that leaves your team. Where Apple's own pages disagree or say nothing, this file says so instead of filling the gap.

## Contents

1. The HIG page, section by section
2. Tech Talk 111466 "Design for iPhone Duo"
3. Tech Talk 111463 "Strike a pose with adaptive layouts on iPhone Duo"
4. Tech Talk 111462 "Raise the bar with iPhone Duo" (design-side rules only)
5. Tech Talk 111461 "Prepare your app for iPhone Duo" (design-relevant rules only)
6. Technology Overview "Preparing your app for iPhone Duo" (design-relevant rules only)
7. Group Lab Q&A (Apple engineers, Developer Forums 847644)
8. Outer display, Lock Screen, StandBy, Live Activities (Newsroom and HIG)
9. Games
10. Accessibility
11. App Store assets and design resources
12. Apple's consolidated "don't" list
13. What Apple has not published

---

## 1. The HIG page, section by section

Page: [HIG, Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo). Change log: "September 9, 2026 | New page. Introduces the fundamental concepts of designing for iPhone Duo, including device poses, dynamic layouts across dual displays, and toolbars and tab bars on the vertical axis." Sections in order: Discussion; Anatomy (with "Device poses"); Best practices; Dynamic layouts (Reserved regions, Split views, Arrangement views); Vertical controls; Resources.

### Discussion

- Abstract: "An app designed for iPhone Duo adapts seamlessly to both displays, providing a continuous experience as the device opens and closes."
- "iPhone Duo has two displays, each with its own front-facing camera. A hinge in the center lets people open and close the device, and supports a variety of ways to hold and position it. This range of display sizes and poses makes an adaptable layout more important than ever. If your app uses standard system components and you've designed it to support resizing, it automatically adapts to the device's poses with little adjustment required."
- "Although iPhone Duo is a new form factor, keep in mind that you're still designing for iPhone, and Designing for iOS patterns and best practices still apply."

### Anatomy

- "People interact with the outer display when the device is closed, and the system places toolbars and tab bars on the side to maximize the vertical space for content. The controls remain on the side when the device opens in landscape to ensure a consistent experience as people move between displays."
- "A center hinge supports a range of ways to hold and position the device. The hinge also impacts the space available for your content as the device folds."
- "The outer front-facing camera is in the corner and is always visible, vertically aligned with controls on the side. The inner camera is behind the display and stays hidden until the camera is active."
- Side column, callouts "from top to bottom": the Dynamic Island, the status bar, the toolbar, the tab bar. "Controls on the side include both system and app elements: the Dynamic Island, the status bar, the toolbar (including navigation buttons), and the tab bar."

### Device poses

- "People hold iPhone Duo and set it down in a number of ways: partially folded like a book, placed down on a surface, or standing on its edges." (Illustration alt text: "An illustration of six device poses.")
- "Supporting the device's various poses doesn't mean designing a custom layout for each one: instead, use size classes so your app adapts naturally as it changes size. A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose. Don't reinvent your app when it resizes; allow the existing layout to expand based on the available space instead."
- "You can use Device Hub in Xcode to preview your app on iPhone Duo and test how your app appears in its various poses."

### Best practices (the five bolded rules)

1. "**Build your app to resize.** Because the device has two displays and supports a wide range of poses and Split View multitasking, your app can appear at many different sizes. Use size classes, layout margins, and safe area insets to lay out controls and content. Avoid fixed widths and display-specific dependencies."
2. "**Create a consistent experience across displays.** Keep functionality and the state of elements the same between displays. Maintain your app's information hierarchy, but show an additional level of hierarchy on the larger inner display if it makes sense for your content. Mail, for example, shows either a list of emails (primary) or an email (secondary) when the device is closed. When it's open, it shows both side by side."
3. "**Maintain the same functionality across device poses.** Controls may overflow and content may move or change size as the interface adapts to the available area. Provide access to the same controls and content regardless of how someone holds or views the device."
4. "**Follow the system's vertical layout for toolbars, tab bars, and navigation controls.** Because the outer display is wider and shorter than the display on other iPhone devices, the system moves controls to the side to preserve vertical space for content and reflect the asymmetry of the display. On the inner display, controls remain on the side in landscape to preserve a continuous experience at the same vertical height. If you use standard system components, you receive this layout automatically, but you may want to refine it based on the needs of your app."
5. "**Make your game playable in every device pose.** You can choose to lock to either portrait or landscape orientation, but be sure to fill the screen as the device pose changes. When resizing, keep text and control sizes as consistent as possible. Prefer changing the aspect ratio over letterboxing or pillarboxing in games; if you can't avoid letterboxing or pillarboxing, add artwork to the padding area to help the experience feel full screen."

### Dynamic layouts

- "Designing for iPhone Duo means accounting for a variety of hardware and software configurations. As with all iOS devices, build your layouts with layout margins and safe area insets, and steer clear of fixed widths or anything tied to a specific display."

### Reserved regions

- "In addition to standard considerations for safe areas, available space on iPhone Duo is shaped by *reserved regions*. These represent areas within the display that content avoids covering, or that components adapt to accommodate. These are familiar if your layout adapts to similar areas on other platforms, such as the window controls on iPad."
- "**The outer front-facing camera.** This region is always present, and expands into the Dynamic Island for Live Activities. When controls are on the side, the system automatically accounts for it and arranges elements accordingly."
- "**The inner front-facing camera.** This region is only present when the camera is active. When it's inactive, the camera isn't visible; when the camera activates, the UI moves aside to indicate the presence of the camera."
- "**The folding region.** This region is conditional based on how a person uses the device. When the device is partially open, the folding region divides the inner display into multiple usable regions, excluding the region at the center as the display folds."
- "Many system components automatically adapt to reserved regions. Components like alerts, context menus, and sheets automatically move to account for the fold, while larger components like split views adapt their columns' width and margins to match the symmetry of the inner display. For custom components, ReservedRegion (SwiftUI) and UIView/ReservedRegion (UIKit) provide a way to reposition content away from reserved regions."
- "**Adapt your layout when the device folds.** Prefer a layout container that adapts automatically, like the split view in Notes that adjusts the width of each pane to stay clearly visible as the device folds. In a grid-style layout, prefer an even number of columns so content divides cleanly. Use the `ReservedRegion` API to keep important elements clear of the center if the system doesn't move them automatically."
- Notes example: fully open, "The leading pane shows a list of notes and is narrower than the trailing pane"; partially folded, "The leading pane ... is the same width as the trailing pane."
- "**Avoid extreme layout changes as people fold the device.** Move only what's necessary to keep elements visible and easy to tap. Controls that disappear or shift dramatically are harder to find and track, so favor small adjustments over rearrangement."

### Split views

- "On iPhone Duo, a split view expands on the inner display and collapses to a single pane on the outer display, the same way it adapts between regular and compact environments on other iPhone devices. When built with standard components, split views adapt to reserved regions automatically, adjusting width and margins to adapt to the fold."
- "When two apps share the inner display with Split View multitasking, each one places controls along its outer edge, so the left app has controls on the left."

### Arrangement views

- "An *arrangement view* is a layout container that holds two views inside it — a primary view and a secondary view — and dynamically organizes them based on display size, orientation, and reserved regions."
- "A *split* arrangement divides its area between its primary and secondary views. It splits horizontally when the arrangement is wider than it is tall, and splits vertically when the arrangement is taller than it is wide."
- "An *overlay* arrangement positions the primary and secondary views on top of one another. When the display is partially folded, the views move to occupy each side; otherwise the primary view moves atop the secondary view."
- "You can limit which axes a split arrangement uses, and collapse the secondary view in an overlay arrangement when you don't want it to appear."
- "**Consider an arrangement view when your layout already resembles one.** ... an HStack or VStack, translates directly to a split arrangement. A layout that layers one view over another, such as a ZStack, translates to an overlay arrangement."
- "**Keep navigation outside of arrangement views.** An arrangement view lays out content but doesn't handle navigation, so place navigation containers like navigation split views and tab views around it rather than within it."

### Vertical controls

- "Keep controls consistent across device poses... keep controls' relative positions as similar as possible so people don't have to relearn where actions live as they change between poses."
- "Keep text-based buttons to a minimum."
- "Provide both a title and a symbol for each toolbar item that isn't text-only... the system uses the title in overflow menus and expanded forms."
- "Group related toolbar items instead of spacing them manually... avoid adding fixed spacing yourself."
- "Reserve the ellipsis symbol for overflow, and give other menus a distinct symbol." "If your app has its own overflow menu, move those actions into the system menu."
- "In general, don't override the default bar placement. The position of controls on the vertical axis is one of the core patterns of iPhone Duo."
- "Consider using the full display width for interfaces where bars aren't necessary... as long as nothing conflicts with the Dynamic Island or the status bar. Calculator, for example, occupies the full width of the display." Calculator on iPhone 16 uses "four columns of five items"; on the Duo outer display "five columns of four items".

### Resources linked from the page

Apple Design Resources (#ios-apps), Screenshot specifications, Designing for iOS, Layout; developer documentation for `ReservedRegion`, `UIView/ReservedRegion`, `ArrangementView`, `UIArrangementViewController`, and the Technology Overview; videos 111466, 111462, 111463.

---

## 2. Tech Talk 111466 "Design for iPhone Duo"

[Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/) (10:45; Marcos and Vince, Apple Design). Chapters: Introduction 0:00, Design principles 0:28, Adapting your design 3:42, Positioning controls 5:07, Designing for the outer display 6:33, Designing for the inner display 7:34, Sheet behavior 8:36, Fold avoidance 9:28, Conclusion 10:01.

- Target "two size classes: compact width (outer display) and regular width (inner display)"; "Avoid fixed widths, breakpoints, and screen-specific metrics."
- "An optional special layout can suit seated, hands-free use, but it must keep the same controls and hierarchy as other poses." "Don't tie functionality to a pose."
- "Use the extra width. Split views can surface more of the app hierarchy, and layouts can switch to two columns. Keep the hierarchy consistent between the inner and outer displays."
- "Top toolbar items go to the top of that side space and bottom items go to the bottom. Tab bars stay bottom-aligned."
- "Items too wide for the side space, such as text buttons or segmented controls, stay in the nav bar."
- "Most content needs an offset so it isn't hidden behind side controls. Safe area insets handle this automatically. Immersive, non-scrolling interfaces can center on the full display if interactive elements aren't blocked. Mixing approaches is also fine, such as a full-width header with inset scrollable content."
- Sheets: vertical controls on the outer display (can be disabled for single-button sheets), horizontal bars on the inner display; "When the device is folded, sheets slide away from the fold."
- "When partially folded, the curve in the display acts as a divider, and content moves away from it."
- "System components nudge interactive elements away from the fold when the device is partially folded. Use system components to get this behavior automatically. Scrollable content doesn't need to avoid the fold."
- Split View is "a 50/50 layout started from the home gesture."
- Apple's position on aspect ratio (Group Lab wording): "Don't assume fixed ratios. Resize to fit each pose, favor changing aspect ratio over letterboxing, and add artwork to unavoidable padding."

Third-party transcript detail, not verified against Apple's page: inner-display portrait is "the only pose where we've kept horizontal bars" (5:27), and "buttons are tough to tap when they land right in the fold" (9:28) (blakecrosley.com; third-party, unverified).

---

## 3. Tech Talk 111463 "Strike a pose with adaptive layouts on iPhone Duo"

[Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/) (18:01; Maria, HI Design; Harry, UI Frameworks).

- "When partially folded like a book, the hinge divides the inner display into usable regions. Content that spans the fold becomes harder to see, much like a photo spread across a book's spine."
- Displacement "adjusts the frame of existing elements based on available space, keeping content visible, reachable, and unobstructed." Move elements "independently when they can adapt alone, and together when they work as a unit." "Avoid excessive movement."
- "Continuous scrolling content (articles, feeds, documents, lists) does not displace. It already adapts through scrolling, and moving it can interrupt continuity."
- "The fold is backed by a **division** region because it divides a larger area into smaller ones." "The fold's division region is active only when the device is folded. When flat, it is inactive with a width of zero." "Inactive regions still support high-level decisions. For example, prefer an even number of grid columns whenever a division region is present, whether or not it is currently active." "**Occlusion** regions occlude rather than divide... The FaceTime camera is represented as an occlusion region, which is active while the camera is active."
- "**Book pose** (partially folded): alerts move to the trailing side, closer to where they will appear when the device closes."
- "**Table pose** (propped up): the top region suits content viewed at a distance, such as an alert. The bottom region suits interactive controls, such as media controls, which get a more stable surface for touch."
- "search fields stay over the keyboard or the view they search, and their width and position adapt as the device folds."
- Reminders' split view "keeps both columns visible in an even 50/50 split" when folded; Fitness's grid "outer margins are preserved while spacing around the hinge increases."
- Arrangement inputs: "horizontal and vertical size classes, the view's width-to-height aspect ratio, and any active division regions"; outputs: "whether each view is shown and its frame." "If the arrangement cannot split along its primary axis, it shows only one view." "When a closed iPhone Duo is held in landscape, only the primary view is shown." "Choose **overlay** for a clear foreground/background relationship... Choose **split** for a main/detail relationship."
- Closing audit: "Audit your app's centered layouts. Consider a two-column layout or a displacement pattern." "Identify your highest-priority manually laid-out controls and adopt the reserved regions API."
- Accessibility Reader is cited as an example of the overlay arrangement "where scrollable content may be partially obscured."

---

## 4. Tech Talk 111462 "Raise the bar with iPhone Duo" (design-side rules)

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) (15:43; Anna, UI Frameworks; Maria, HI Design).

- Why bars move: on the outer display controls "share the space with the status bar and Live Activities, and overflow into a menu if space runs short." Items overflow "more often on the outer display in landscape, or when the keyboard or Picture in Picture appears."
- "Content from custom `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered."
- Shared vertical region is "like rotating 90 degrees into a vertical stack"; in split views "only the detail column participates"; inspectors get no vertical bar.
- Vertical bars have "fixed width and flexible item height"; icon items go vertical, text-only items stay horizontal. "Even if your content is an image, it's still important to provide a title."
- Flexible spacers are zero on the vertical axis. "Don't add extra spacing, whether the bar is horizontal or vertical."
- Reserve the ellipsis for overflow "rather than introducing symbols from other platforms." Use badges instead of inline counts.
- Default overflow order is bottom-to-top; toolbars compress before tab bars by default.
- The bar "remains fixed" on the same hardware side in right-to-left languages.
- "Vertical bars have no scroll-edge effect by default, but get a background when Reduce Transparency is enabled. Keep content legible either way."
- When to opt out: "Single-page, bottom-heavy layouts such as Calculator" or "Control-heavy sheets with only one item."
- "Accessory bars stay attached to the keyboard and don't move to the vertical axis."

The API names behind these rules belong to the duo-bars skill.

---

## 5. Tech Talk 111461 "Prepare your app for iPhone Duo" (design-relevant rules)

[Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/) (10:10; David Jackson, UI Frameworks).

- Size classes: "*Outer display:* Like other iPhone models. Portrait is regular vertical and compact horizontal. Landscape is compact vertical and compact horizontal. *Inner display:* Regular horizontal and regular vertical, leaving room for sidebars."
- "The inner display doesn't honor your supported interface orientations. As with Idiom, avoid checking interface orientation for layout decisions. Use size classes instead." "Landscape support is still valuable on the outer display, since people may use the device like a tent."
- "Safe areas and layout margins are often asymmetric on iPhone Duo, so avoid assuming that insets on opposite sides are equal." Bars sit outside the safe area; horizontal bars provide top/bottom insets, vertical bars provide leading/trailing insets.
- SDK tiers as the user sees them: iOS 26 SDK or earlier, "centered on the inner display with empty space around it"; iOS 27 SDK, fills most of the inner display but avoids the status bar; iOS 27.1 SDK, "your app extends to the edge of the screen. Standard navigation and toolbar buttons now lay out vertically under the status bar."
- "`NavigationSplitView`, `UISplitViewController`, `TabView`, and `UITabBarController` adapt to every pose. Closed, columns collapse to a single stack. Open, columns appear tiled and as overlays. Tabs appear on both displays and lay out vertically when appropriate. On the inner display you can opt into a sidebar."
- Device Hub: "Use the control buttons at the bottom of the screen to open, close, rotate, or fold iPhone Duo."

---

## 6. Technology Overview "Preparing your app for iPhone Duo" (design-relevant rules)

[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo).

- Pose figure caption: "closed, folded like a tent, open in a wide layout, partially folded, open in a tall layout, and folded like a laptop".
- "iPhone Duo presents navigation bars, toolbars, and tab bars together vertically on the side of the display in some poses ... This happens on the outer display when the device is closed, and for some views in the leading or trailing position on the inner display when the device is open."
- Item rules: "The system uses an icon for an item it presents vertically. / The system uses an icon or a title for an item it presents horizontally, preferring an icon. / The system uses an icon and title for an item in an overflow menu. / If your item has a title and doesn't have an icon, the system doesn't present it vertically. / If your item uses a custom view rather than a title or icon, the system doesn't present it vertically."
- Order: "Reserve the top for primary navigation controls, like Back or Close, followed by prominent actions, such as Done. If you use a navigation controller, the system adds the Back button automatically."
- Context rules: "**Inspectors.** The system presents bars in inspectors horizontally. / **Split views.** In a split view displaying multiple views, the system shows bars horizontally for the sidebar or content view, and vertically for the detail view. / **Sheets.** On the outer display, the system presents bars vertically for sheets by default. ... For sheets on the inner display, the system presents the toolbar horizontally for centered or leading placements, and vertically for trailing placements."
- Regions: "A division occurs when a folding region divides a large view into smaller views. An occlusion is an area of a view where a hardware element, such as the camera, covers your content so it isn't visible. The inner front-facing camera can block your view when it's active, and the outer front-facing camera always occludes your view." "A reserved region can be active or inactive. For example, a reserved region that represents the fold is active when iPhone Duo is partially open, but inactive when it is fully open."
- Overlay arrangement when partially open: "places the primary view in the trailing or bottom part of the display relative to the fold, and the secondary view in the leading or top part".
- Audit checklist: "Confirm your views resize well in each supported orientation and pose. / Inspect how the system presents your app's navigation bars, toolbars, and tab bars vertically on the side of the display. / Identify any views, sheets, or popovers that position awkwardly when you fold or open iPhone Duo. / Identify elements or controls in your views that appear in the fold, and are difficult to see or interact with."
- Camera apps and the outer display: "When iPhone Duo is fully open and capturing photos or video with the rear camera, it can show content on the outer display in addition to showing your app on the inner display."

From the companion page [Three steps to make your app shine on iPhone Duo](https://developer.apple.com/iphone-duo/prepare/): "On the inner display, your app should look like a natural extension of its iPad layout." "**Don't choose a layout by idiom.**" "**Don't treat 'regular width' as 'iPad.'**" "**Check full-bleed media.** Hero images and video set to `.scaleAspectFill` or `.aspectRatio(contentMode: .fill)` can lose important content on wider displays. Use the current size classes or aspect ratio to choose between fill and fit, or set a focal point." "Share app previews and screenshots that highlight your app across orientations."

From [HIG, Layout](https://developer.apple.com/design/human-interface-guidelines/layout) (updated September 9, 2026): "Determine layout based on size classes, not device type or orientation." "while an app's size classes might change when someone resizes it, its idiom — the device type it's made for — remains the same: keep the layout recognizable and familiar to the platform even when resizing." "Consider taking advantage of larger spaces to switch from a tab bar to a sidebar or expose functionality that might otherwise be grouped into an overflow menu." "Don't change your app's functionality based on the space it occupies." "Support Dynamic Type by adjusting your layout to accommodate text at larger sizes. For example, horizontally adjacent views may need to stack vertically."

---

## 7. Group Lab Q&A (Apple engineers)

[Developer Forums 847644, "A Summary of the iPhone Duo Group Lab"](https://developer.apple.com/forums/thread/847644) (DTS; counts as Apple).

- "There's no single pose API. Infer pose from hinge status, angle, orientation, and size class together." "Hinge changes are just geometry/trait changes." Hinge "Update rate and precision are system policy, so don't depend on specific values."
- "iPhone Duo is not a separate device class ... iPhone Duo does not support Stage Manager and does not have its own `UIUserInterfaceIdiom`." "Apps don't need iPad support first."
- "Portrait-only apps ... still receive compact and regular size class changes. The outer display honors supported orientations, but the inner display ignores them." "There is no sanctioned way to lock the inner display to portrait."
- "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running." "Text input, scroll position, and video playback are generally preserved automatically."
- "Custom bottom sheets need fold avoidance using reserved regions. Safe-area insets alone are not enough."
- "Scene size can't be set directly. It's driven by pose and Split View." "Free-form drag-to-resize isn't supported."
- "Scene accessories ... are the only way for non-camera apps to present on the outer display, and the system decides when." "`CameraCaptureAccessory` appears only while the app is foregrounded with an active capture session." "Non-camera apps can't draw directly on the outer display."
- "Live Activities must implement compact, minimal, expanded, and Lock Screen presentations. The camera region expands into the Dynamic Island." Widgets: "Supported families include `systemSmall`, `systemMedium`, `systemLarge`, `systemExtraLargePortrait`, `accessoryCircular`, `accessoryRectangular`, and `accessoryInline`. Inner and outer displays behave similarly to the broader iOS and iPadOS ecosystem."
- "Animations should be able to start, pause, and stop at any point. Use `TimelineView` or `CADisplayLink`."
- "Don't fake rotation by spinning UI elements. Use real size-class-driven layout." "Apps don't need to know which face is up. Use size classes."
- "Interactions that look fine in the simulator may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution."
- Idiom confirmation from an Apple Frameworks Engineer, [Developer Forums 847945](https://developer.apple.com/forums/thread/847945): "you are not required to support iPad to support the iPhone Duo as its device idiom is still `.phone`."
- Sidebars from an Apple Frameworks Engineer, [Developer Forums 847912](https://developer.apple.com/forums/thread/847912): "By default, iPhone Duo (and all other iPhones) will not show a sidebar for `UITabBarController` apps, even when its horizontal size class is regular. Sidebars are opt-in on iPhone".

---

## 8. Outer display, Lock Screen, StandBy, Live Activities

- [Apple Newsroom, September 2026](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/): "Lock Screen controls, the Dock, and app navigation move to the side." "Today View appears on the left when open, alongside two Home Screen pages." "The Dynamic Island is redesigned to fit vertically on the side of the outer and inner displays, and expands for Live Activities and alerts." "StandBy works on either display even when it's not charging." Both displays: "ProMotion, Always On, and 3000 nits of peak outdoor brightness." Outer display "90 percent of the screen area of iPhone 18 Pro"; inner display "50 percent larger than iPhone 18 Pro Max." Apple Pencil (USB-C) support "Later this year".
- [HIG, Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities) (change log October 13, 2026, "Added guidance for limited width layouts"): "Support limited width presentations. To avoid truncated text in contexts with limited width like the Dynamic Island on iPhone in landscape, adapt your compact and minimal presentations to fit inside a 28pt-diameter circle... adopt a leading view only and leave the trailing view empty; the system automatically hides the trailing view." Environment value `isDynamicIslandLimitedInWidth`. The page never names iPhone Duo; connecting it to the vertical Dynamic Island on Duo is an inference.
- [Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/): camera capture accessory conditions: "The app is full screen on the inner display. The app has an active camera session. The accessory is registered on the same view as the camera UI." "On the outer display of iPhone Duo, new windows cannot be created. That behavior is reserved for the inner display."
- [Apple Newsroom, October 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/): "Scene accessories: Apps can show content on both displays at once, such as a teleprompter on the outer display." Pose-specific examples: Prime Video, "Partially folded, video plays on the top half and X-Ray info ... appears on the bottom half"; MLB, "Live games play on the upright half while stats fill the lower half when propped on a table"; United Airlines, "Navigation on the right side of the display."
- [Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes): "StandBy is unavailable in the iPhone Duo Simulator runtime. (187708663)".

---

## 9. Games

- HIG best practice 5, quoted in full in section 1.
- [Developer Forums 847644](https://developer.apple.com/forums/thread/847644): "Make them playable in every pose, and prefer changing aspect ratio" over letterboxing; "Add artwork to unavoidable padding"; "Use `UIRequiresFullScreen` for immersive apps. The app still resizes."
- [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/): "Landscape is a good opportunity on the outer display because people may set the phone down like a tent."
- [HIG, Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games) has no Duo text; the Duo game rules live only on the Duo page.

---

## 10. Accessibility

- [Developer Forums 847644](https://developer.apple.com/forums/thread/847644): "Standard iOS accessibility practices apply." "Test Dynamic Type, contrast, VoiceOver, and resizing across poses using Xcode and Device Hub." "VoiceOver focus order is generally handled by the view hierarchy. Custom hinge-spanning layouts may need explicit containers or sort priorities." "For one-screen layouts, don't hold text at the largest standard size. Let it reflow so it stays readable." "For fixed one-screen layouts, holding text at the largest standard size can fail App Store Connect's Larger Text criteria. The thread cites scales past 200% at AX3 and over 300% at AX5."
- [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/): vertical bars "get a background when Reduce Transparency is enabled. Keep content legible either way."
- [HIG, Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo): "Move only what's necessary to keep elements visible and easy to tap." Titles on items: "the system uses the title in overflow menus and expanded forms."
- Tooling caveat, [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes): "VoiceOver, the Accessibility Inspector, and other accessibility tools cannot convey screen content on an iPhone Duo within Device Hub. (187148389)".
- There is no Duo-specific accessibility section in the HIG.

---

## 11. App Store assets and design resources

- [ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications): outer display 1398 × 2034 (portrait) / 2034 × 1398 (landscape); inner display 2007 × 2853 / 2853 × 2007; up to 10 per device size; .jpeg/.jpg/.png; no alpha. "Starting in April 2027, screenshots will be required for any app using the iOS 27.1 SDK or later." "When you submit iPhone Duo screenshots in App Store Connect, your App Store product page displays a badge indicating the app is optimized for iPhone Duo."
- [Developer News, October 5, 2026](https://developer.apple.com/news/?id=kkphp5qo): "Starting April 2027, any apps or games submitted will need to include screenshots for iPhone Duo." (Scope wording differs from the specifications page; the conflict is unresolved. See duo-ship.)
- [ASC app preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications): accepted upload resolutions 886 × 1920 (portrait) / 1920 × 886 (landscape), 15–30 seconds, up to 30 fps, up to three per device size and language.
- Badge name "Made for iPhone Duo" ([Apple Newsroom, October 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/); [developer hub](https://developer.apple.com/iphone-duo/)).
- [HIG, App Icons](https://developer.apple.com/design/human-interface-guidelines/app-icons): no iPhone Duo mention; spec remains 1024 × 1024 px; latest change "June 8, 2026 | Refined guidance for Liquid Glass."
- [Apple Design Resources](https://developer.apple.com/design/resources/) are linked from the HIG page and the hub for margins and safe areas; their Duo contents were not verified in the report.
- [Apple Tech Specs](https://www.apple.com/iphone-duo/specs/): inner "1878‑by‑2670-pixel resolution at 430 ppi", 7.6-inch; outer "1398‑by‑2034-pixel resolution at 460 ppi", 5.4-inch; both displays with Dynamic Island; Touch ID in the side button.

---

## 12. Apple's consolidated "don't" list

From the HIG Duo page: "Don't reinvent your app when it resizes." "Avoid fixed widths and display-specific dependencies." "Avoid extreme layout changes as people fold the device." "In general, don't override the default bar placement." "Group related toolbar items instead of spacing them manually." "Keep text-based buttons to a minimum." "Reserve the ellipsis symbol for overflow, and give other menus a distinct symbol." "Keep navigation outside of arrangement views." "Prefer changing the aspect ratio over letterboxing or pillarboxing."

From the Tech Talks, Technology Overview, Three steps, and HIG Layout: "Avoid fixed widths, breakpoints, and screen-specific metrics." "avoid assuming that insets on opposite sides are equal." "avoid checking interface orientation for layout decisions." "Don't choose a layout by idiom." "Don't treat 'regular width' as 'iPad.'" "Remove checks for specific device sizes." "Don't add extra spacing, whether the bar is horizontal or vertical." "Avoid excessive movement." "Don't tie functionality to a pose." "Don't change your app's functionality based on the space it occupies." "Don't fake rotation by spinning UI elements."

---

## 13. What Apple has not published

- No point dimensions for either display, no scale factor, no margin values, no fold width in points. The HIG page "contains no numeric point/pixel dimensions for either display, no margin values, and no hinge/fold width in points"; the HIG Layout page has no device table. Figures such as 466 × 678 pt and 669 × 951 pt @3x, an 84 pt vertical-bar inset, and a 40 pt fold region are third-party simulator measurements (third-party, unverified).
- No pose API and no hinge-angle thresholds separating tent, laptop, and book. Device Hub's Book = 127° and Open = 180° readings are third-party (third-party, unverified); Apple's own Device Hub documentation names the buttons Closed, Partially Open, and Open ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)).
- No Duo-specific HIG for widgets, Lock Screen, StandBy, Always On, keyboards, Apple Pencil, or Camera Control.
- No animation duration or curve for the fold transition, and no "fold transition" API.
- No statement on three-column split views on the inner display, on Dynamic Type thresholds for collapsing split views, or on VoiceOver behaviour across two displays.
- No Duo-specific app icon guidance.
- Apple's own pages disagree on who the April 2027 screenshot rule covers (section 11).
