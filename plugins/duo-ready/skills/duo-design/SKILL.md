---
name: duo-design
description: >-
  Review a design, mockup, Figma frame, or screenshot set against Apple's
  Human Interface Guidelines for iPhone Duo, and explain Apple's design rules
  to designers, PMs, and developers in Apple's own words. Use it whenever
  someone asks "does this design work on the new foldable iPhone", "how
  should this screen look when the phone is open", "what poses do we design
  for", "what are the screen sizes in points for Figma", "should the tab bar
  be on the side", "do we need a special layout when it is propped on a
  table", "is letterboxing OK for our game", "does the fold matter for our
  grid", "the toolbar looks strange on the new iPhone", or wants a design
  review, a design spec, or a design-system update for iOS 27.1. Also use it
  when a PM asks for a per-pose spec, a "tent mode" or "flex mode" layout, or
  Duo margins and dimensions, because Apple has published none of those and
  the honest answer needs Apple's sentences. Not for implementing the
  layout code (duo-layout, duo-bars) or capturing store assets (duo-ship).
---

# duo-design: review designs against Apple's iPhone Duo guidelines

## What Apple actually says

- Supporting poses "doesn't mean designing a custom layout for each one: instead, use size classes ... A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose. Don't reinvent your app when it resizes" ([HIG, Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Five bolded best practices: build your app to resize; create a consistent experience across displays; maintain the same functionality across device poses; follow the system's vertical layout for toolbars, tab bars, and navigation controls; make your game playable in every device pose (same page).
- "There's no single pose API" and hinge update rate and precision "are system policy, so don't depend on specific values" ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)); Apple publishes no angle thresholds and no point dimensions, margins, or fold width for either display.
- The fold is a *reserved region* (a division, active only when partially folded), the cameras are occlusions; alerts, menus, sheets, and split views avoid the fold automatically, scrolling content does not displace, and grids should use an even number of columns ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo); [Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)).
- "In general, don't override the default bar placement. The position of controls on the vertical axis is one of the core patterns of iPhone Duo" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

## Workflow

### Step 1: Get the actual material before you judge anything

Ask for, or open, what exists: Figma or Sketch frames, exported PNGs, simulator screenshots, a design spec, or the SwiftUI/UIKit source. A review needs three views of each screen: compact width (closed), regular width (open, both rotations), and a note or frame for the partially folded state. If any is missing, score those criteria "Unclear" and say which frame you need; do not infer behaviour across poses from one screenshot.

If a project path is available, run the audit tool so the design review is grounded in what the code does:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

Its findings (custom bars, fixed sizes, idiom checks, portrait locks) map directly onto rubric sections A and D below. Read `references/review-rubric.md` for the criteria and `references/hig-verbatim.md` when you need Apple's exact sentence.

### Step 2: Translate the stakeholder's vocabulary into Apple's

People say "tent mode", "flex mode", "half-open", "laptop mode". Apple's words are: "closed, folded like a tent, open in a wide layout, partially folded, open in a tall layout, and folded like a laptop" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)); "partially folded like a book, placed down on a surface, or standing on its edges" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)); "Book pose (partially folded)" and "Table pose (propped up)" ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)). Use those terms in the review, and say once that Apple does not use "tent mode" or "flex mode". `references/poses.md` has the full table.

Then restate every pose in terms the system actually exposes: outer display is compact width (regular height in portrait, compact in landscape); inner display is regular width and regular height in either rotation ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)); the fold's division region is active only when partially folded and has "a width of zero" when flat (Tech Talk 111463). If a design calls for "layout B at 90°", explain that no angle threshold exists and that the implementable condition is "the folding region is active".

### Step 3: Check the two base layouts first

Before any pose detail, confirm the design is two layouts, not six:

1. Compact width (outer display): a complete iPhone UI with content offset from the side column. Apple's order for that column, top to bottom, is "the Dynamic Island, the status bar, the toolbar (including navigation buttons), and the tab bar" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). The outer display is "wider and shorter than the display on other iPhone devices", which is why Calculator shows "five columns of four items" there instead of iPhone 16's "four columns of five items".
2. Regular width (inner display): the compact layout expanded, showing "an additional level of hierarchy ... if it makes sense" (Mail: list or message closed, both side by side open). Apple also says it "should look like a natural extension of its iPad layout" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)) while the idiom stays `.phone` ([Developer Forums 847945](https://developer.apple.com/forums/thread/847945)). Sidebars for tab apps are opt-in, not default ([Developer Forums 847912](https://developer.apple.com/forums/thread/847912)).

Fail the review early if the inner layout is a different product (different navigation, different features), if any layout has fixed widths or display-specific metrics, or if the spec assumes the inner display can be locked to portrait: "The inner display doesn't honor your supported interface orientations" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

### Step 4: Walk the rubric

Open `references/review-rubric.md` and score each applicable criterion Pass, Fail, Unclear, or N/A. Lead with failing Blockers (Apple's explicit "don't"s and bolded best practices), then Refinements. Quote the Apple sentence beside each Fail so the designer can verify it. The sections, with the question each answers:

- **A. Resizing fundamentals.** Two layouts, no fixed widths, size classes not devices or orientation, per-edge insets, full-bleed media with fill/fit or a focal point.
- **B. Consistency across displays and poses.** Same functionality and state on both displays; nothing exists in only one pose; a seated or hands-free variant "must keep the same controls and hierarchy as other poses" ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)); controls keep their relative positions.
- **C. Fold transitions and reserved regions.** Adapting containers, even column counts, nothing interactive across the centre when folded, "favor small adjustments over rearrangement", scrolling content stays put, book pose puts alerts trailing, table pose puts viewing content on top and controls on the bottom, custom bottom sheets need fold avoidance beyond safe areas ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- **D. Vertical bars.** System bars, symbol plus title on every item, "Keep text-based buttons to a minimum", grouped items with no manual spacing, system overflow with the ellipsis reserved for it, default placement not overridden except Calculator-style full-width layouts or single-item sheets, full-width layouts that avoid the Dynamic Island and status bar.
- **E. Outer display and system surfaces.** Compact UI not a glance surface; no app content on the outer display while open except a camera capture accessory during an active capture session ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)); Live Activities fit the 28pt limited-width circle (HIG Live Activities, which does not name Duo; the link is inferred); landscape on the outer display is designed because people stand the closed device like a tent.
- **F. Games.** Lock allowed but "be sure to fill the screen as the device pose changes"; prefer changing aspect ratio over letterboxing; artwork in unavoidable padding; consistent text and control sizes.
- **G. Accessibility.** "Standard iOS accessibility practices apply"; test across poses; hinge-spanning layouts may need containers or sort priorities; let text reflow (pinned text "can fail App Store Connect's Larger Text criteria"); legible with Reduce Transparency.
- **H. App Store assets.** Pixel sizes for Duo screenshots; no Duo icon work (the App Icons HIG has no Duo guidance).

### Step 5: Write the review

Use the report template at the end of `references/review-rubric.md`: material reviewed, what was not shown, blockers with Apple's sentence and a one-line fix, refinements, passes worth keeping, and a "not scorable from Apple's guidance" list. The last list matters as much as the blockers: when a reviewer asked for margins, point sizes, fold width, or angle thresholds, say Apple has not published them rather than supplying a number. If a number is needed to proceed, offer the third-party simulator figures with the label "(third-party, unverified)" and point to Apple Design Resources, which the HIG links for margins and safe areas but whose Duo contents the report did not verify.

### Step 6: Hand off

For each failing criterion name the skill that implements the fix: duo-layout for size classes, reserved regions, arrangement views, and grids; duo-bars for bar items, overflow, and opt-out; duo-scenes for state across the fold; duo-ship for screenshots. For verification, say which Device Hub poses to check (Closed, Partially Open, Open, plus Option-drag for any angle, per [Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)) and note Apple's warning that reach and weight can only be judged on hardware ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## Decisions you will be asked to make

**"Can we design a special layout for when it is propped on a table?"** Yes, as an option, and only if it keeps every control and the same hierarchy: "An optional special layout can suit seated, hands-free use, but it must keep the same controls and hierarchy as other poses. Don't tie functionality to a pose" ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)). Apple's own examples are Prime Video (video top half, X-Ray bottom half) and MLB (game on the upright half, stats on the lower half) ([Apple Newsroom, October 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/)). The trigger a developer can implement is an active division region plus size classes, not an angle.

**"Should we move the tab bar to the side ourselves?"** No. The system does it when the app uses system navigation containers; custom bars are not moved and the HIG asks you not to override the default placement. The design should show the side column and assume text-only and segmented items stay horizontal ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)).

**"Three columns look better on the open display."** Apple asks for an even number so the fold lands in a gutter when partially folded ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Apple has made no statement on three-column split views on the inner display; treat that as a gap, not a permission.

**"Our game is landscape-only. Can we letterbox when the phone opens?"** The lock is allowed, letterboxing is discouraged: "Prefer changing the aspect ratio over letterboxing or pillarboxing in games; if you can't avoid letterboxing or pillarboxing, add artwork to the padding area" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Remind the team the inner display ignores orientation locks.

**"Can we show a scoreboard, lyrics, or a message on the outer display while the phone is open?"** Only camera apps during an active capture session, via a camera capture accessory: "Non-camera apps can't draw directly on the outer display" ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

**"What are the point sizes and margins for our Figma frames?"** Apple has published pixels only: inner "1878‑by‑2670-pixel resolution at 430 ppi", outer "1398‑by‑2034-pixel resolution at 460 ppi" ([Apple Tech Specs](https://www.apple.com/iphone-duo/specs/)); App Store Connect screenshot sizes are outer 1398 × 2034 and inner 2007 × 2853 ([ASC screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). The 466 × 678 pt and 669 × 951 pt @3x figures are third-party simulator measurements (third-party, unverified). Advise designing with size classes, layout margins, and safe area insets, and framing to the ASC pixel sizes for screenshots.

## Common mistakes

Field reports converge on a short list. Items marked [Apple] are Apple statements; items marked [3P] are developer anecdotes from the report and are unverified.

- [Apple] Hero media set to fill "can lose important content on wider displays" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). Design the fill/fit decision or a focal point.
- [Apple] Functionality that exists in one pose only, or a seated layout that drops controls, violates best practice 3 and Tech Talk 111466.
- [3P] A sheet whose only action was a text "Done" button reserved the side rail and left it empty, because text-only items are not presented vertically. Fix in design: give the item a symbol, or opt the sheet out of vertical bars (blakecrosley.com).
- [3P] A six-column grid centred on the content area put its fourth column across the fold (blakecrosley.com); another developer picked even counts "on purpose" so the fold falls in a gutter (bleepingswift.com). Apple's even-column rule is the reason.
- [3P] A close button pinned top-trailing disappeared under the clock because the design assumed symmetric insets; the vertical bar adds a one-sided inset (skarol.dev). Apple's rule: handle each side independently ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- [3P] "Tall, narrow layouts appear wide and short on the inner display" when a design relies on a portrait lock (skarol.dev). Apple: the inner display ignores supported orientations.
- [3P] A card pushed in the compact layout stayed "stretched to full width" after unfolding instead of becoming a split (blakecrosley.com). Design the regular-width counterpart of every compact screen.
- [3P] Day-one press described un-updated apps as centred with empty space and one mail app as resizing "but has a poor widescreen layout" (Macworld). Compiling is not a design review.
- [Apple] Mixing bar opt-outs across screens makes controls jump; Apple's opt-out cases are narrow (Calculator-style single pages, single-item sheets) and the HIG says not to override placement in general.

## When to read the references

- `references/review-rubric.md`: every time you score a design. Criteria A1 to H3, each tied to an Apple sentence, plus the report template and the list of things Apple has not ruled on.
- `references/hig-verbatim.md`: when you need Apple's exact wording or URL for a review comment, a design spec, or a disagreement with a stakeholder. Includes the five best practices, both fold-transition rules, the reserved regions text, the vertical controls section, Tech Talk design rules, and the consolidated "don't" list.
- `references/poses.md`: when someone asks what the poses are, whether there is a pose API, what each pose means for size classes and the fold region, or wants a per-pose spec.

## Related skills

- duo-audit: run the scanner and triage code-level findings behind a design problem.
- duo-layout: implement size-class layouts, reserved regions, arrangement views, and even-column grids.
- duo-bars: implement vertical bar items, symbols and titles, overflow, and the Calculator-style opt-out.
- duo-scenes: keep state across the fold; multi-window and Split View behaviour.
- duo-camera: camera capture accessories, the only route to the outer display while open.
- duo-test: Device Hub poses, simulator screenshots, what cannot be automated.
- duo-ship: App Store screenshots at Duo sizes, the April 2027 rule and its ambiguity, the badge.
- duo-backend: image sizing and server-driven layout hints keyed on size class, not device.
- duo-crossplatform: the same design rules applied through React Native, Flutter, Capacitor, and Unity.
