# Poses: Apple's vocabulary, and what a pose means for layout

Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

Poses are a design vocabulary, not an API. Apple describes them in prose and illustrations, never as an enum, and states that layout must come from size classes and reserved regions rather than from a pose. This file collects every pose word Apple has used, the one API-visible consequence of each pose, and the two pose-specific placement rules Apple has published.

## 1. Every pose word Apple has used

| Apple's words | Where | Notes |
|---|---|---|
| "closed, folded like a tent, open in a wide layout, partially folded, open in a tall layout, and folded like a laptop" | Pose figure caption, [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) | Six poses in one sentence. "Open in a wide layout" and "open in a tall layout" are the fully open inner display in its two rotations. |
| "partially folded like a book, placed down on a surface, or standing on its edges" | Device poses, [HIG, Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo); illustration alt text "An illustration of six device poses." | The HIG does not name the six individually. |
| "**Book pose** (partially folded)" and "**Table pose** (propped up)" | [Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/) | The only two poses Apple gives placement rules for (section 4). |
| "people may use the device like a tent" / "people may set the phone down like a tent" | [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/) | Given as the reason landscape support still matters on the outer display. |
| "Partially folded, video plays on the top half and X-Ray info ... appears on the bottom half" (Prime Video); "Live games play on the upright half while stats fill the lower half when propped on a table" (MLB) | [Apple Newsroom, October 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/) | Apple's own worked examples of a table-pose layout. |
| Device Hub buttons: "Closed", "Partially Open", "Open"; "To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel" | [Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub) | Apple's testing vocabulary has three states plus a free angle. |

Whether "folded like a laptop" (Technology Overview) and "Table pose (propped up)" (Tech Talk 111463) are the same physical arrangement is not stated by Apple; treating them as one pose is an inference. Apple does not use the terms "tent mode" or "flex mode" anywhere in the sources; if a stakeholder uses them, translate to Apple's words above.

A third-party reading of the Xcode 27.1 simulator labels Device Hub's middle button "Book" at 127° and "Open" at 180° (blakecrosley.com; third-party, unverified). Prefer Apple's button names.

## 2. There is no pose API and there are no angle thresholds

- "There's no single pose API. Infer pose from hinge status, angle, orientation, and size class together." "Hinge changes are just geometry/trait changes." ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644))
- Hinge "Update rate and precision are system policy, so don't depend on specific values." (same thread)
- The hinge APIs report "the high-level hinge status (closed, partially open, fully open) and continuous hinge angle updates ... Hinge data is ideal for driving interactions and effects. For layout decisions, use the arrangement and region APIs." ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/))
- No Apple source gives an angle at which tent, laptop, or book begins or ends, or at which the hinge status flips between partially open and fully open.

Design consequence: a design spec cannot say "at 90° show layout B". It can say "when the folding region is active, keep interactive elements out of the center; when the width is regular, show two columns". Those are the conditions the system actually exposes. If a PM asks for a per-pose spec, offer the two size-class layouts plus a folded variant and explain why a tighter spec cannot be implemented.

## 3. What each pose looks like to the app

The only pose-dependent signals Apple names are the size classes, the active state of the fold's division region, and the hinge status. Size classes from [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/):

| Display / pose | Horizontal size class | Vertical size class |
|---|---|---|
| Outer display, portrait (closed) | compact | regular ("like other iPhone models") |
| Outer display, landscape (closed, including "like a tent") | compact | compact |
| Inner display, either rotation (open) | regular | regular ("leaving room for sidebars") |

Combining Apple's statements:

| Pose (Apple's word) | Display in use | Size classes | Fold division region | Bars |
|---|---|---|---|---|
| Closed | Outer | compact × regular (portrait) or compact × compact (landscape) | Not applicable; the fold is a feature of the inner display | Vertical, on the side, stacked under the Dynamic Island and status bar ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)) |
| Open in a tall layout / open in a wide layout | Inner | regular × regular | Inactive, "a width of zero" ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)) | Horizontal in portrait; vertical in landscape (HIG best practice 4) |
| Partially folded like a book | Inner | regular × regular | Active; "divides the inner display into multiple usable regions" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)) | As for the open inner display |
| Table pose / folded like a laptop | Inner | regular × regular | Active | As for the open inner display |
| Folded like a tent / standing on its edges | Outer (the tent reading in Tech Talk 111461 is about outer-display landscape) | compact × compact | Not applicable | Vertical |

The rows for the inner display partially folded are inferred from Apple's statement that the inner display is regular × regular in "either rotation" and that the fold region is active when partially open; Apple does not publish a per-pose table.

Other pose-dependent behaviours Apple states:

- The inner display "doesn't honor supported interface orientations" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)); "There is no sanctioned way to lock the inner display to portrait" ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). A portrait-only design will be shown wide and short when the device is open in a wide layout.
- "When a closed iPhone Duo is held in landscape, only the primary view is shown" by an arrangement view ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)).
- New windows cannot be created on the outer display ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)).
- Opening or closing is a resize, not a relaunch: "treated as a size-class and trait change, not a scene disconnect or app termination" ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). Scroll position, text input, and video playback are generally preserved.

## 4. The two pose-specific placement rules

From [Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/):

- **Book pose** (partially folded, held like a book): "alerts move to the trailing side, closer to where they will appear when the device closes."
- **Table pose** (propped up): "the top region suits content viewed at a distance, such as an alert. The bottom region suits interactive controls, such as media controls, which get a more stable surface for touch."

Supporting rules from the same talk and the HIG:

- "Continuous scrolling content (articles, feeds, documents, lists) does not displace. It already adapts through scrolling, and moving it can interrupt continuity."
- Move elements "independently when they can adapt alone, and together when they work as a unit." "Avoid excessive movement."
- "In a grid-style layout, prefer an even number of columns so content divides cleanly." ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)); "prefer an even number of grid columns whenever a division region is present, whether or not it is currently active" (Tech Talk 111463).
- Reminders' split view "keeps both columns visible in an even 50/50 split" when folded; Fitness's grid "outer margins are preserved while spacing around the hinge increases."
- The system's overlay arrangement, when partially open, "places the primary view in the trailing or bottom part of the display relative to the fold, and the secondary view in the leading or top part" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). This is Apple's own implementation of the table-pose rule: foreground controls go to the bottom half, background content to the top half.
- Sheets "slide away from the fold" when the device is folded ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)).

## 5. The rule that overrides all pose thinking

"Supporting the device's various poses doesn't mean designing a custom layout for each one: instead, use size classes so your app adapts naturally as it changes size. A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose. Don't reinvent your app when it resizes; allow the existing layout to expand based on the available space instead." ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo))

"An optional special layout can suit seated, hands-free use, but it must keep the same controls and hierarchy as other poses." "Don't tie functionality to a pose." ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/))

So a design package for Duo is: one compact-width layout, one regular-width layout, a note on what moves when the folding region is active, and optionally a seated-use variant that keeps every control. Six separate pose mockups are not what Apple asks for and cannot be implemented as drawn.

## 6. How to review poses without a device

Device Hub in Xcode 27.1 offers Closed, Partially Open, and Open, plus Option-drag for any angle ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)). Apple warns that simulator results are an approximation for reach and feel: "Interactions that look fine in the simulator may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution" ([Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). StandBy and most app extensions are unavailable in the Duo simulator runtime ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)). There is no supported command-line way to set a pose; see duo-test.
