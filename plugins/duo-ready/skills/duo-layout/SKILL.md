---
name: duo-layout
description: >-
  Make an iOS app's layout adapt to iPhone Duo in SwiftUI and UIKit: derive
  layout from size classes and scene or view bounds instead of UIScreen.main,
  idiom, orientation or cached sizes; handle asymmetric safe areas; keep
  content off the fold and the cameras with reserved regions; adopt
  ArrangementView / UIArrangementViewController for two-pane layouts; keep
  state alive when the device folds; fix grids, centered layouts and games.
  Use it whenever someone mentions iPhone Duo, a foldable, the inner or outer
  display, the fold, crease or hinge, and also when they describe the symptom
  without naming the device: "layout breaks when the phone opens", "my view is
  stretched or clipped on the new iPhone", "content sits under the camera",
  "a grid column lands on the crease", "portrait lock is ignored",
  "UIScreen.main returns the wrong size", "regular size class on an iPhone",
  "stale layout after folding", "should I use ArrangementView", "two-column
  layout when unfolded", "how big is the Duo screen in points".
---

# duo-layout

Adaptive layout for iPhone Duo (iOS 27.1, Xcode 27.1 build 27A9275). Everything here is
Apple's published guidance; anything measured by third parties or inferred by this repo is
labelled as such. Ask to see the user's actual code before advising.

## What Apple actually says

- Build with Xcode 27.1, "use size classes and scene geometry to improve your app's resizing",
  prefer "system-provided layouts and containers, such as split views, tab bars, arrangement
  views, and navigation stacks", and "Make layout calculations based on your scene or
  containing view's bounds rather than screen dimensions" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- Size classes: outer display portrait = compact width / regular height, outer landscape =
  compact / compact, inner display = regular / regular in either rotation (Tech Talk 111461,
  "Prepare your app for iPhone Duo"). The idiom stays `.phone` ([Forums 847945](https://developer.apple.com/forums/thread/847945)).
- "There's no single pose API. Infer pose from hinge status, angle, orientation, and size
  class together" ([Forums 847644](https://developer.apple.com/forums/thread/847644)). The fold is
  a *division* reserved region that is "active when iPhone Duo is partially open, but inactive
  when it is fully open" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- "Hinge data is ideal for driving interactions and effects. For layout decisions, use the
  arrangement and region APIs" (Tech Talk 111464).
- "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side
  independently" (Tech Talk 111461).
- Apple publishes pixel sizes only (inner 1878×2670, outer 1398×2034). There is no Apple
  statement of point dimensions; any point figure you see is a third-party simulator
  measurement ([Tech Specs](https://www.apple.com/iphone-duo/specs/)).

## Workflow

### 0. Look at the code first

Ask for the view or view controller that misbehaves, plus any layout helper it calls. When a
project path is available, run the scanner and triage its findings before you suggest changes:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

It flags Apple's Step 2 anti-patterns (`UIScreen.main`, idiom, orientation, hard-coded sizes,
symmetric safe-area math, portrait-only locks). Fix those before adopting any iOS 27.1 API,
because Apple's own ordering is hygiene first, new API second
([Three steps](https://developer.apple.com/iphone-duo/prepare/)).

### 1. Classify the layout by size class, not by device

Use this matrix (Tech Talk 111461) and nothing else to decide which layout a view shows:

| Display / pose | Horizontal | Vertical |
|---|---|---|
| Outer display, portrait | compact | regular ("like other iPhone models") |
| Outer display, landscape | compact | compact |
| Inner display, either rotation | regular | regular ("leaving room for sidebars") |

Why this is enough: "A compact width layout for the outer display and a regular width layout
for the inner display give you the fundamentals for every pose. Don't reinvent your app when
it resizes; allow the existing layout to expand based on the available space instead"
([HIG: Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Rules that follow from the matrix:

- Check both size classes where it matters. "Don't treat 'regular width' as 'iPad'", because
  "an iPhone app can have any combination of size classes" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
  A developer who chose a regular layout by width alone broke on a 6.9-inch iPhone in
  landscape (third-party, unverified: blakecrosley.com).
- Never gate a feature on `userInterfaceIdiom == .pad`; the inner display is regular/regular
  with idiom `.phone`, so iPad-only branches silently stay off ([Forums 847945](https://developer.apple.com/forums/thread/847945)).
- Do not override `horizontalSizeClass`; Apple says that "would likely interfere with system
  updates" ([Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Orientation is not a layout input. Apple's operative guidance, matching Tech Talk 111461:
  "The inner display doesn't honor supported interface orientations, so use size classes
  rather than orientation for layout decisions. Landscape support is still valuable on the
  outer display, since people may use the device like a tent." DTS confirmed "There is no
  sanctioned way to lock the inner display to portrait" ([Forums 847644](https://developer.apple.com/forums/thread/847644)).
  The same thread, answering a compatibility-mode question, also says "iPhone Duo still
  honors UISupportedInterfaceOrientations, but the expected behavior for this device differs
  from previous iPhone devices in certain hinge states and orientations. Instead, use size
  classes"; treat neither wording as a layout mechanism and do not try to resolve the
  difference in the user's code.
- If the user asks "how many points wide is it", answer that Apple has not published point
  dimensions. The circulating 466×678 pt (outer) and 669×951 pt (inner) @3x figures are
  third-party simulator measurements (blakecrosley.com); the arithmetic matches the App Store
  Connect screenshot sizes (inferred), but a layout must never depend on them.

### 2. Replace screen, idiom and orientation assumptions

Apple's Step 2 list is grep-able. Each row is Apple's own replacement
([Three steps](https://developer.apple.com/iphone-duo/prepare/); Tech Talk 111461):

| Find | Replace with | Why |
|---|---|---|
| `UIScreen.main.bounds` | `view.bounds`, `window.bounds`; SwiftUI `GeometryReader` or `onGeometryChange` | `UIScreen.main` is "ambiguous on two-display devices and will be deprecated in a future release" |
| Size read once at launch or in `viewIsAppearing` | Re-read in `layoutSubviews` / `viewDidLayoutSubviews`; use `viewWillTransition(to:with:)` for work that must run on resize | "a fold can resize your app in the middle of a session" |
| `UIScreen.main.scale` | `traitCollection.displayScale`; `@Environment(\.displayScale)` | two displays, two scales to consider |
| `UIWindow(frame: UIScreen.main.bounds)` | `UIWindow(windowScene:)` | windows belong to scenes |
| A stored `UIScreen` | `view.window?.windowScene?.screen` at the moment of use | "Don't store a `UIScreen`" |
| `UIDevice.current.orientation`, `statusBarOrientation`, `interfaceOrientation`, `windowScene.effectiveGeometry.interfaceOrientation` | Compare available width vs height; use size classes | inner display ignores orientation |
| `userInterfaceIdiom == .phone/.pad` | size classes | "Don't choose a layout by idiom" |
| `bounds.height == 844`-style checks | remove | "Remove checks for specific device sizes" |
| `.scaleAspectFill` / `.aspectRatio(contentMode: .fill)` on hero media | choose fill or fit by size class or aspect ratio, or set a focal point | fill "can lose important content on wider displays" |

In SwiftUI, do not copy a size into `@State` in `onAppear`; read it with
`onGeometryChange(for:of:action:)` so it updates after a fold (the modifier is named by Apple's
Step 2; the stale-`onAppear` failure is a third-party report, skarol.dev). In UIKit, observe
size-class changes with `registerForTraitChanges(_:handler:)` or
`registerForTraitChanges(_:target:action:)` ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)),
and observe scene size with `windowScene(_:didUpdateEffectiveGeometry:)` comparing
`coordinateSpace.bounds` (same technote).

### 3. Handle each safe-area edge independently

Bars sit outside the safe area: "horizontal bars provide top/bottom insets, vertical bars
provide leading/trailing insets" (Tech Talk 111461). On the outer display and in inner-display
landscape the system bar column is on one side only, so insets are one-sided. Apple's code
form: `foreground.frame = view.bounds.inset(by: view.safeAreaInsets)` with
`backgroundView.frame = view.bounds`; replace `view.bounds.width - view.safeAreaInsets.left * 2`
with `view.bounds.inset(by: view.safeAreaInsets).width` (Tech Talk 111461). In SwiftUI use
`ignoresSafeArea()` only for background artwork and keep interactive content inside the safe
area (same talk).

Two things the safe area does *not* give you:

- The fold. "Custom bottom sheets need fold avoidance using reserved regions. Safe-area
  insets alone are not enough" ([Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Touch over the camera. Custom UI overlapping the camera region without the reserved-region
  API has touch "suppressed or may not register as expected" (same thread).

Third-party, unverified field reports to look for in code: the side column adds about an
84 pt inset on one edge only; a close button pinned top-trailing disappeared under the clock;
`prefersStatusBarHidden = true` hides the icons but not the inset; nested scroll views
report 0 side safe area (skarol.dev, iPhone-Duo-by-Examples). Fix by constraining to the safe
area and removing `.ignoresSafeArea()` from anything that is not a background.

### 4. Keep content off the fold and the cameras: reserved regions

Concepts ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):
"A division occurs when a folding region divides a large view into smaller views. An
occlusion is an area of a view where a hardware element, such as the camera, covers your
content so it isn't visible. The inner front-facing camera can block your view when it's
active, and the outer front-facing camera always occludes your view." The HIG lists three
regions: the outer camera (always present), the inner camera (only while active), and the
folding region (conditional) ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Read them where the frameworks track them:

- SwiftUI: `proxy.reservedRegions(kind: .division)` (or `.occlusion`), add
  `options: .includeInactive` to see the fold while flat; frames are "in the view's
  coordinate space", `(0, 0)` at the top-leading corner
  ([GeometryProxy.reservedRegions](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:))).
  Each `ReservedRegion` has `id`, `kind`, `frame: CGRect` (which "already includes
  `margins`"), `margins: EdgeInsets` and `isActive: Bool`
  ([ReservedRegion](https://developer.apple.com/documentation/swiftui/reservedregion), verified 2026-10-26).
- UIKit: `view.reservedRegions(kind: .division)` inside `updateConstraints()`, because "UIKit
  tracks the regions you read in `updateConstraints()` and runs it again when the regions
  change" ([UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))).
  `UIView.ReservedRegion` exposes `frame`, `isActive`, `kind`, `margins: UIEdgeInsets`
  ([UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion), verified 2026-10-26).
  Consuming regions in `viewDidLayoutSubviews()` instead is not what Apple documents (inferred).
- Custom SwiftUI `Layout`: Apple warns that `bounds` in `placeSubviews` does not always start
  at (0,0); compute positions from (0,0) and add `bounds.origin` (same `reservedRegions` page).
- "The fold's division region is active only when the device is folded. When flat, it is
  inactive with a width of zero"; "Inactive regions still support high-level decisions. For
  example, prefer an even number of grid columns whenever a division region is present,
  whether or not it is currently active" (Tech Talk 111463).

Do not over-apply it. DTS: "not every app needs to use Arrangement Views or the reserved
regions API" ([Forums 847887](https://developer.apple.com/forums/thread/847887)); the HIG says to
use it "to keep important elements clear of the center if the system doesn't move them
automatically". Apple's own `UIView.ReservedRegion` page points to `UIArrangementViewController`
as the preferred tool when the job is arranging two related views around the fold. Third-party
observations (unverified): regions arrive after the first layout pass, so do not cache them;
inactive regions can return zero-size frames, so check `isActive` first.

### 5. Decide whether an arrangement view fits

`ArrangementView` (SwiftUI) and `UIArrangementViewController` (UIKit) are "a layout container
for a primary view and a secondary view" with two styles ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):

- **Split** (default): side by side when the container is wider than tall, primary on top
  otherwise, adjusted for reserved regions. Use where you would use `HStack`/`VStack`.
  "When a closed iPhone Duo is held in landscape, only the primary view is shown"; "If the
  arrangement cannot split along its primary axis, it shows only one view" (Tech Talk 111463;
  [ArrangementView](https://developer.apple.com/documentation/swiftui/arrangementview)).
- **Overlay**: primary over secondary when no division is active; when partially open,
  primary goes to the trailing/bottom part relative to the fold, secondary to leading/top.
  Use where you would use `ZStack`.
- Choose "overlay for a clear foreground/background relationship" and "split for a main/detail
  relationship"; "Consider an arrangement view when your layout already resembles one"
  (Tech Talk 111463; [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Container rules Apple states three times, which you should enforce in review:
"Keep navigation outside of arrangement views ... place navigation containers like navigation
split views and tab views around it rather than within it" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo));
"Avoid placing an arrangement view inside a navigation split view, list, scroll view, or other
container that might cause part of your view to become inaccessible" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo));
"Avoid putting it inside another layout container, such as a scroll view, navigation split
view, grid ... Also avoid placing container views such as a navigation split view or tab view
inside it" ([ArrangementView](https://developer.apple.com/documentation/swiftui/arrangementview)).
The resulting order, navigation container outside, arrangement view in the middle, `List` or
`ScrollView` inside each pane, is this repo's inference from those rules.

Tuning: `.arrangementViewStyle(.split.axes(.horizontal))`, `overlayArrangementEdge(_:)`,
`splitArrangementLayoutRatio`, `splitArrangementLayoutSize`, `splitArrangementFixedLayoutSize`.
Read `@Environment(\.overlayArrangementZIndex)` (an `Int`; "zIndex > 0 ? .collapsed : .expanded"
in Apple's example) to collapse a pane that is floating over the other, and
`@Environment(\.splitArrangementAxis)` (`Axis?`, nil outside a split arrangement) to adapt a
pane's inner layout. UIKit: `setViewController(_:for:)`, `updateArrangement(.split.axes(.vertical))`,
`state(for: .primary)?.zIndex`; wrap in `UINavigationController(rootViewController:)`
(Tech Talk 111463; [UIArrangementViewController](https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller)).
Third-party, unverified: in book pose `.split` puts its divider on the fold even when a ratio
is set; `splitArrangementFixedLayoutSize` overrides the fold; the root view reads
`overlayArrangementZIndex == 0`, so read it from a subview (iPhone-Duo-by-Examples).

### 6. Decide what moves when the device folds

Tech Talk 111463's displacement rules: "Continuous scrolling content (articles, feeds,
documents, lists) does not displace. It already adapts through scrolling"; move elements
"independently when they can adapt alone, and together when they work as a unit"; "Avoid
excessive movement". Its examples: Reminders keeps "an even 50/50 split", Fitness keeps outer
margins "while spacing around the hinge increases", search fields "stay over the keyboard or
the view they search". The HIG adds: "In a grid-style layout, prefer an even number of
columns so content divides cleanly" and "Avoid extreme layout changes as people fold the
device. Move only what's necessary ... favor small adjustments over rearrangement"
([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Pose-specific destinations Apple names: in book pose "alerts move to the trailing side, closer
to where they will appear when the device closes"; in table pose "the top region suits content
viewed at a distance, such as an alert. The bottom region suits interactive controls, such as
media controls" (Tech Talk 111463). An optional hands-free layout "must keep the same controls
and hierarchy as other poses. Don't tie functionality to a pose" (Tech Talk 111466).

Apply the talk's closing audit to the user's screens: "Audit your app's centered layouts.
Consider a two-column layout or a displacement pattern. Identify your highest-priority
manually laid-out controls and adopt the reserved regions API." Compositional collection
layouts do not avoid the fold automatically (third-party summary of Apple's UIKit Q&A,
Gubarenko Q6). A six-column grid centered on the content area put its fourth column across the
fold (third-party, blakecrosley.com); even counts put the fold in a gutter.

### 7. Keep state alive across a fold

"Opening or closing the device, or switching displays, is treated as a size-class and trait
change, not a scene disconnect or app termination. The process keeps running"; "Text input,
scroll position, and video playback are generally preserved automatically. Apps usually don't
need `scrollPosition(id:)` for LazyVGrid column changes"; `stateRestorationActivity(for:)` is
only for a true scene disconnect ([Forums 847644](https://developer.apple.com/forums/thread/847644)).
The HIG asks you to "Keep functionality and the state of elements the same between displays".

Consequence (inferred from those statements): do not tear down and rebuild the view tree on a
size-class change. In SwiftUI, switch layouts with `AnyLayout` or size-class-aware containers
rather than `if` branches that give the panes new identity; in UIKit, keep the same view
instances and let Auto Layout relayout. A card pushed in the compact layout that stayed
"stretched to full width" after unfolding (third-party, blakecrosley.com) is the symptom of
navigation state that was not re-evaluated when width became regular; `NavigationSplitView`
and `UISplitViewController` handle that collapse/expand automatically ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
Animations "should be able to start, pause, and stop at any time. Use `TimelineView` or
`CADisplayLink`" (Forums 847644). `UIRequiresFullScreen` is honored on Duo "but still resizes
when the device opens or closes" (Tech Talk 111461); under the iOS 27 SDK it only yields a
discrete resize ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
Fold-as-trait-change details (multi-window, scene phase) are in `duo-scenes`.

### 8. Games

"You can choose to lock to either portrait or landscape orientation, but be sure to fill the
screen as the device pose changes ... Prefer changing the aspect ratio over letterboxing or
pillarboxing in games; if you can't avoid letterboxing or pillarboxing, add artwork to the
padding area" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
Split View and PiP "mean apps may run at varying aspect ratios, so they should be freely
resizable" (Tech Talk 111466). Orientation lock requests via `prefersInterfaceOrientationLocked`
plus `setNeedsUpdateOfPrefersInterfaceOrientationLocked()` "are not guaranteed to be honored"
([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).
TN3192's hook for swapping assets: compare `coordinateSpace.bounds.size` in
`windowScene(_:didUpdateEffectiveGeometry:)` and update when `!geometry.isInteractivelyResizing`.
Apple publishes no Duo-specific Metal or frame-pacing guidance (gap).

### 9. Verify

Apple's test loop is Device Hub: the Closed, Partially Open and Open buttons under the bezel,
Option-drag on the slider for any angle, Rotate in each pose
([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)).
Test Split View by dragging "the app by the home indicator to either side of the screen"
(Tech Talk 111461). Previews have a "Display group for previewing content on a device's
alternative display" ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
Walk Apple's checklist: views resize in each pose; bars present correctly; sheets and popovers
position well when folding; nothing sits in the fold ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
There is no `simctl` or XCUITest fold command; see `duo-test` before promising automation.

Availability: every symbol in steps 4 and 5 is iOS 27.1+, "Available on any iPhone or iPad
running iOS 27.1+", and Apple recommends "gating iOS 27.1 APIs behind availability checks"
([Forums 847644](https://developer.apple.com/forums/thread/847644)); guard Mac Catalyst targets
with `#if !targetEnvironment(macCatalyst)` ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

## Common mistakes

- `UIScreen.main.bounds.width > 900` to enable a two-page mode, so it never appears on the
  inner display (third-party: quran-ios #1224). Apple: use container bounds.
- Sizes saved at launch, "Stale layout after folding" (third-party: skarol.dev). Apple: re-read
  in layout callbacks, `viewWillTransition(to:with:)`, trait registration.
- Portrait-only app whose "Tall, narrow layouts appear wide and short on the inner display"
  (third-party: skarol.dev). Apple: the inner display ignores supported orientations.
- A feature gated on `.pad` that never shows on the inner display (third-party: skarol.dev).
- Regular layout chosen by width only (third-party: blakecrosley.com). Apple: check both
  size classes.
- Symmetric safe-area math; a close button lost under the clock (third-party: skarol.dev).
  Apple: handle each side independently.
- A grid column across the fold; a fold-unaware compositional layout (third-party reports;
  Apple: even columns, reserved regions).
- `ArrangementView` inside a `List`, `ScrollView` or `NavigationSplitView`, or a `TabView`
  inside it (violates Apple's stated container rules).
- Hero media on `.fill` losing its subject on the wider display (Apple: Three steps).
- Reading hinge angle to pick a layout (Apple: hinge is for effects; layout uses arrangement
  and region APIs).
- Overriding `horizontalSizeClass` to force a phone layout (Apple: interferes with system updates).
- Promising a point size or an angle threshold. Apple publishes neither.

## When to read the references

- `references/api-reference.md`: every layout symbol with signature, minimum OS and status
  label; the gaps table. Read before writing any iOS 27.1 call.
- `references/samples.md`: Apple's verbatim examples plus minimal composed before/after
  samples (size classes, `onGeometryChange`, trait registration, `updateConstraints` with
  reserved regions, even-column grid, arrangement views in the right container order, the
  TN3192 scene-geometry hook). Read when producing code.
- `references/apple-rules.md`: Apple's rules verbatim with URLs. Read when the user asks
  "where does Apple say that" or when a review needs the exact wording.

## Related skills

- `duo-audit`: run the scanner first and triage findings.
- `duo-bars`: vertical navigation, tool and tab bars, sheets, opt-out.
- `duo-scenes`: fold as a trait change, multi-window and Split View, scene accessories, hinge API.
- `duo-design`: HIG rules, poses vocabulary, review rubric.
- `duo-test`: Device Hub, simulator, what cannot be automated.
- `duo-camera`, `duo-ship`, `duo-backend`, `duo-crossplatform` for everything outside layout.
