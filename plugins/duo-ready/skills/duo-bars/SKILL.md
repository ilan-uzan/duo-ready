---
name: duo-bars
description: >-
  Make navigation bars, toolbars and tab bars behave on iPhone Duo, where the
  system moves them to a vertical column on the side of the display. Use it
  whenever a developer says their toolbar or tab bar "looks weird", "went
  sideways", "is on the right edge now", "has an empty strip next to it",
  "disappeared", "shows a ... menu I didn't add" or "jumps around" on the new
  iPhone, the foldable, the Duo simulator, or after rebuilding with Xcode 27.1;
  when Done/Back/Close buttons are missing or out of order; when a custom
  UIToolbar/UINavigationBar/UITabBar or a hand-rolled bottom bar does not go
  vertical; when they ask how to opt a screen out of the vertical bar, where
  sheets or inspectors put their buttons, how to get a sidebar on the inner
  display, how to use toolbarVerticalBehavior, axisBehavior,
  visibilityPriority, ToolbarOverflowMenu, pinnedTrailingGroup,
  preferredVerticalBarBehavior or verticalBarEdge; or when a design review
  asks whether a bar layout follows Apple's iPhone Duo guidance.
---

# duo-bars: vertical navigation, tool and tab bars on iPhone Duo

## What Apple actually says

- "iPhone Duo presents navigation bars, toolbars, and tab bars together vertically on the side of the display in some poses ... This happens on the outer display when the device is closed, and for some views in the leading or trailing position on the inner display when the device is open" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). "The exception is the inner display in portrait, which has enough vertical space to keep standard horizontal bars" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Why: "Because the outer display is wider and shorter than the display on other iPhone devices, the system moves controls to the side to preserve vertical space for content" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). The side column stacks, top to bottom, "the Dynamic Island, the status bar, the toolbar (including navigation buttons), and the tab bar" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Opt-in is the iOS 27.1 SDK plus a system container: "In SwiftUI, add the `toolbar(content:)` modifier to a `NavigationStack` or `NavigationSplitView`. In UIKit, set toolbar items on a view controller that you add to a navigation controller" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). "Content from custom `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). There is no Info.plist key.
- Items need icons: "If your item has a title and doesn't have an icon, the system doesn't present it vertically. / If your item uses a custom view rather than a title or icon, the system doesn't present it vertically" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- "In general, don't override the default bar placement. The position of controls on the vertical axis is one of the core patterns of iPhone Duo" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Everything in this skill is either an Apple statement with its page named, or marked (third-party, unverified) / (inferred). Where Apple has published nothing, say so instead of guessing; `references/api-map.md` section 7 lists those gaps.

## Workflow

### 1. Look at the real code first

Ask for, or open, the view that owns the bar: the SwiftUI `NavigationStack` / `NavigationSplitView` / `TabView` and its `.toolbar { }`, or the UIKit view controller, its `navigationItem`, and whatever container (`UINavigationController`, `UITabBarController`) it sits in. Ask which display and pose the complaint comes from (closed, open landscape, open portrait, Split View, with the keyboard up) because the system behaves differently in each. Do not advise from a description alone; most bar complaints are container or item-shape problems that only the code reveals.

When a project path is available, run the audit before reading further:

```
python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path>
```

Bar-related rules: DUO-017 (custom tab/tool bar built from plain views), DUO-018 (navigation bar hidden), DUO-016 (status bar hidden, side inset still applies), DUO-019 (project not upgraded to Xcode 27.1), DUO-022 (symmetric safe-area math). The `vertical_bars` adoption line tells you which Duo bar APIs the project already uses.

### 2. Confirm the SDK tier

Vertical bars exist only for binaries built with the iOS 27.1 SDK: "**iOS 27.1 SDK or later:** The app uses the full display, and toolbars and tab bars move vertically below the status bar. Before shipping with this SDK, confirm your content adapts to the vertical bars" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). Xcode 27.1 is build 27A9275 ([Apple Software Releases](https://developer.apple.com/news/releases?id=10152026a)). If the app is built with Xcode 27.0 or 26, the bars will not go vertical and nothing below applies yet; send the user to duo-audit for the SDK tiers. The behavior depends on the linked SDK, not the deployment target. The new APIs are "Available on any iPhone or iPad running iOS 27.1+" and Apple recommends "gating iOS 27.1 APIs behind availability checks" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

### 3. Check who owns the bar

The system only moves bars it owns. Decide which case the code is in:

| What you find | Verdict |
|---|---|
| `.toolbar { }` on a view inside `NavigationStack` / `NavigationSplitView`; `TabView` | System-owned; continue to step 4 |
| `UIBarButtonItem`s on `navigationItem` / `toolbarItems` of a VC inside `UINavigationController` / `UITabBarController` | System-owned; continue |
| A `UIToolbar`, `UINavigationBar` or `UITabBar` created by the app and added as a subview; `.navigationBarHidden(true)` or `setNavigationBarHidden(true)` with a hand-built header; an `HStack` of buttons pinned to the bottom | Not considered. The fix is to move the items into the container's bar, not to rotate the custom bar yourself |
| Keyboard accessory bar (`inputAccessoryView`, SwiftUI `.keyboard` toolbar placement) | Stays horizontal by design: "Accessory bars stay attached to the keyboard and don't move to the vertical axis" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). Not a bug |
| Inspector | Horizontal by design ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)) |
| Split view sidebar or content column | Horizontal by design; only the detail column goes vertical ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)) |

Explain the why when you move a custom bar: the system needs to merge navigation buttons, toolbar items and tabs into one column with the status bar and Dynamic Island, and it can only do that with items it knows about.

### 4. Audit every item against the icon/title rules

For each `ToolbarItem` / `UIBarButtonItem`, check: does it have an SF Symbol? Does it have a title? Is it a custom view? Is it a text button or segmented control? Apple's rules, verbatim, are in `references/item-rules.md` section 1. Apply them as follows:

- Title-only items (`Button("Done") { }`, `UIBarButtonItem(title:)`) are not presented vertically. Give them a symbol and keep the title; the title is what the overflow menu shows ("The system uses an icon and title for an item in an overflow menu"). This is the single most common Duo bar defect; a field report describes a text-only Done that "reserved the side rail and left it empty" (third-party, unverified: blakecrosley.com).
- Custom-view items are not presented vertically unless you opt them in with `.axisBehavior(.verticalPreferred)` / `UIBarButtonItem.axisBehavior = .verticalPreferred`; a third-party report says this only works when the view fits the bar (unverified). Prefer converting them to icon+title items.
- Text buttons and segmented controls "stay in the nav bar" ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)); mark them `.axisBehavior(.horizontalOnly)` so the choice is explicit, or move the choice into a menu. Segmented controls are "not a good candidate" for the vertical bar (Apple UIKit Q&A as summarized by a third party).
- "Keep text-based buttons to a minimum" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

### 5. Fix the order

"Reserve the top for primary navigation controls, like Back or Close, followed by prominent actions, such as Done. If you use a navigation controller, the system adds the Back button automatically" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).

- Close / Cancel: `ToolbarItem(placement: .cancellationAction)`; UIKit `navigationItem.leadingItemGroups = [UIBarButtonItemGroup(...)]` with `navigationItem.leftItemsSupplementBackButton = false` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Done or the one prominent action: `ToolbarItemPlacement.topBarPinnedTrailing`; UIKit `navigationItem.pinnedTrailingGroup = UIBarButtonItemGroup(...)`. Pinned items never overflow.
- Flag, do not resolve: Apple's own material spells the UIKit property two ways. The 111462 slide shows `leftItemsSupplementBackButton`; the narration says `leftItemSupplementsBackButton` (report Appendix C: "Verify in headers"). Write the slide spelling and tell the user to confirm it in the SDK header. The report's second Apple-page discrepancy, `UIView.ReservedRegion` vs `UIViewReservedRegion`, is duo-layout territory but has the same status; mention it if the user is adopting reserved regions in the same pass.
- Tab bars "stay bottom-aligned"; "Top toolbar items go to the top of that side space and bottom items go to the bottom" ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)). Do not try to reorder tabs relative to toolbar items.
- A user who says the order "is completely different between both modes" (third-party sentiment, mjtsai.com) is seeing the stack rule above; explain it rather than fighting it.

### 6. Overflow, priority, badges, spacing

- Overflow is bottom-to-top, and happens more "on the outer display in landscape, or when the keyboard or Picture in Picture appears" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). Control it with `.visibilityPriority(.high)` / `.low` (`ToolbarItemVisibilityPriority`) and `UIBarButtonItem.visibilityPriority = .high`; set priorities on groups first, then items.
- Items that should always live in the menu: `ToolbarOverflowMenu { Button("Scan") {…}; Button("Connect") {…} }` and UIKit `navigationItem.additionalOverflowItems = UIDeferredMenuElement({ provider in provider(self.persistentOverflowItems()) })`. "If your app has its own overflow menu, move those actions into the system menu" and reserve the ellipsis for it ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Replace inline counts with badges: `.badge(7)` / `item.badge = .count(7)`.
- Remove manual spacing: flexible spacers are zero on the vertical axis and "Don't add extra spacing, whether the bar is horizontal or vertical" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)); "Group related toolbar items instead of spacing them manually" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

### 7. Toolbar vs tab bar in a short column

Toolbars compress before tab bars by default. If a tab's actions matter more than the tab strip when space is short, use Apple's form `Tab("Recents", systemImage: "clock") { ContentView().toolbarVerticalCompressionBehavior(.prefersToolbarItems) }` or UIKit `navigationItem.verticalBarCompressionBehavior = .prefersBarItems` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). The SwiftUI values `.automatic` and `.prefersTabBar` are listed in the report's API map but the research notes trace that list to a third-party article; say so if you name them.

### 8. Decide whether a screen may opt out

Apple's two sanctioned cases: "Single-page, bottom-heavy layouts such as Calculator" and "Control-heavy sheets with only one item" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). Code: `NavigationStack { ContentView().toolbarVerticalBehavior(.disabled) }`; UIKit `override var preferredVerticalBarBehavior: UIVerticalBarBehavior { .disabled }`. Rules for using it:

- Make it a stable, per-screen-type choice. Apple's UIKit Q&A (third-party summary) calls it "a stable choice, not toggled per navigation state", and a field report warns that mixing behaviours across screens "makes buttons jump around" (third-party, unverified: skarol.dev). If one sheet opts out, every sheet of that kind should.
- Opting out does not remove the status bar's side inset or the Dynamic Island; a full-width design must keep interactive content clear of them ("as long as nothing conflicts with the Dynamic Island or the status bar", [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Audit rule DUO-016 covers the related `prefersStatusBarHidden` mistake.
- `UIVerticalBarBehavior` cases other than `.disabled` are not enumerated in the report; do not invent them.
- A third-party report says `toolbarVerticalBehavior(.disabled)` inside a sheet affects only that sheet, and that in a window the behavior comes from the topmost view in a `NavigationStack`, the selected tab, or the trailing-most column (unverified: nilcoalescing.com). Useful for debugging; do not present it as Apple's rule.

### 9. Sheets, inspectors, split views, hero art, sidebar

- Sheets: "On the outer display, the system presents bars vertically for sheets by default ... For sheets on the inner display, the system presents the toolbar horizontally for centered or leading placements, and vertically for trailing placements. Set `View.presentationPlacement(_:)` in SwiftUI or `UISheetPresentationController.preferredPlacement` in UIKit" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). The argument values are not in the report; tell the user to read the parameter type in Xcode rather than guessing a case name.
- Inspectors: always horizontal. Split views: sidebar and content horizontal, detail vertical. Nothing to configure.
- Hero art that should run under the bar: `View.backgroundExtensionEffect()` / `UIBackgroundExtensionView` ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)); only the names are documented in the report. Keep interactive content inside the safe area; vertical bars provide leading/trailing insets and "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Sidebar on the inner display is opt-in, not automatic: `TabView { … }.defaultTabBarPlacement(.sidebar)` ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)); `tabBarController.sidebar.preferredPlacement = .sidebar` ([Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912)). Without it, "tab bar apps will have either a vertical or horizontal tab bar on the inner display".
- Detecting the edge for content refinements: `@Environment(\.toolbarVerticalEdge)` / `UITraitCollection.verticalBarEdge`, which "reflects the system's preferred edge regardless of whether a vertical bar is currently visible" ([UITraitCollection.verticalBarEdge](https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge)). Use it to nudge content, not to choose a layout; layout comes from size classes.

### 10. Verify

Device Hub drives the pose: "To close the iPhone Duo, click the Closed button ... To partially open the iPhone Duo, click the Partially Open button ... To fully open the iPhone Duo, click the Open button" ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)). Walk this list and ask the user to report what they see:

1. Closed (outer display): bars vertical; Close/Back at the top, Done next; no empty rail; every item either in the column or in the ellipsis menu with a readable title.
2. Open, landscape (inner display): bars vertical, same order as closed, nothing jumps.
3. Open, portrait: bars horizontal; this is expected, not a regression.
4. Split View: drag "the app by the home indicator to either side of the screen, and check vertically laid-out content on both sides" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)); each app's bar sits on its outer edge.
5. Keyboard up and Picture in Picture: more items overflow; confirm the pinned Done stays.
6. Reduce Transparency on: vertical bars gain a background; "Keep content legible either way" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).

No `simctl` or XCUITest command changes the pose (report; [Apple Developer Forums 847883](https://developer.apple.com/forums/thread/847883) unanswered). Screenshot display names (`--display=primary` / `primary-1`) are third-party; duo-test covers them.

## Common mistakes

- Text-only Done on a sheet leaves an empty rail (third-party field report; the cause is Apple's title-only rule). Fix: add a symbol, or opt the one-item sheet out, consistently.
- Expecting a keyboard accessory bar to go vertical. It never does ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Mixing opt-outs per screen so buttons jump between the top bar and the side column (third-party, unverified: skarol.dev).
- A custom `UIToolbar` / `UITabBar` / bottom `HStack` that stays horizontal and now collides with the side column ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). Audit rule DUO-017.
- Hiding the navigation bar to draw your own header; the system then has nothing to move. Audit rule DUO-018.
- Expecting a sidebar on the inner display without opting in ([Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912)).
- Fixed spacers or manual padding between items; zero on the vertical axis ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Your own "more" menu next to the system ellipsis ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Pinning a close button top-trailing with `.ignoresSafeArea()` so it lands under the clock in the side column (third-party field report: skarol.dev; Apple's rule is to keep interactive content inside the safe area, [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)). Audit rule DUO-022.
- Reading an 84 pt side inset as a constant. That figure is a third-party simulator measurement; Apple publishes no point value.

## When to read the references

- `references/api-map.md`: the SwiftUI vs UIKit table with status labels, which enum cases are confirmed, context rules for sheets/inspectors/split views, the two Apple-page spelling discrepancies, third-party observations, and the gap list. Read it before naming any value or case.
- `references/item-rules.md`: Apple's icon/title/order/spacing/overflow rules verbatim with URLs, and a rule-to-API table. Read it when reviewing items or when the user wants the Apple wording.
- `references/samples.md`: Apple's verbatim snippets, a composed SwiftUI toolbar, the text-only Done before/after, a composed UIKit `navigationItem` setup, opt-out and edge detection, and what cannot be composed yet. Read it before writing code.

## Related skills

- duo-audit: run the scanner and triage DUO-016/017/018/019/022; SDK tiers.
- duo-layout: safe-area asymmetry, size classes, reserved regions (and the `UIView.ReservedRegion` spelling flag), grids around the fold.
- duo-design: HIG rules for designers and the review rubric that scores bar placement.
- duo-scenes: Split View and multi-window, which change where the bar sits.
- duo-test: Device Hub poses, simulator screenshots, what cannot be automated.
- duo-ship: App Store screenshots that must show the vertical bars correctly.
