Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Vertical bar API map: SwiftUI vs UIKit

Status labels follow the report: **[Apple]** = stated on an Apple page, in a Tech Talk, or by an Apple engineer on the Developer Forums (page named in the Source column); **[3P]** = third-party only, unverified against an Apple page; **[Inference]** = the research team's conclusion; **Gap** = Apple has not published it. Every symbol below is spelled exactly as the report records it. Availability: all vertical-bar symbols are iOS 27.1+ / iPadOS 27.1+ except where noted ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo); [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). Apple also said the new APIs are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo" and recommended "gating iOS 27.1 APIs behind availability checks" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## Contents
1. Where the system moves bars
2. The API table
3. Enum values and cases: what is confirmed
4. Context rules: inspectors, split views, sheets, keyboard, Split View, RTL
5. Spelling discrepancies in Apple's own material (flag, do not resolve)
6. Third-party observations (unverified)
7. Gaps

## 1. Where the system moves bars

| Situation | Bars | Source |
|---|---|---|
| Outer display, device closed | Vertical, on the side of the display | [Apple] "This happens on the outer display when the device is closed" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)) |
| Inner display, landscape | Vertical ("controls remain on the side in landscape") | [Apple] [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) |
| Inner display, portrait | Horizontal ("has enough vertical space to keep standard horizontal bars") | [Apple] [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) |
| Inner display, "some views in the leading or trailing position" | Vertical | [Apple] [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) |
| Split View (two apps) | Each app's controls on its outer edge: "the left app has controls on the left" | [Apple] [HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo) |
| RTL | The bar "remains fixed" on the same hardware side | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) |

The side column stacks, top to bottom, "the Dynamic Island, the status bar, the toolbar (including navigation buttons), and the tab bar", aligned with the always-visible corner camera ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Why: "Because the outer display is wider and shorter than the display on other iPhone devices, the system moves controls to the side to preserve vertical space for content" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Opt-in is SDK plus container. Only binaries built with the iOS 27.1 SDK get vertical bars: "**iOS 27.1 SDK or later:** The app uses the full display, and toolbars and tab bars move vertically below the status bar" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)). There is no Info.plist key for this ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/); report).

## 2. The API table

| Purpose | SwiftUI | UIKit | Status / source |
|---|---|---|---|
| Provide bars the system can move | `toolbar(content:)` on `NavigationStack` / `NavigationSplitView` | Items on a view controller inside `UINavigationController` / `UITabBarController` | [Apple] [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo). "Content from custom `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)) |
| Back / Close at the top | `ToolbarItem(placement: .cancellationAction)` | `navigationItem.leadingItemGroups = [UIBarButtonItemGroup(...)]`; `navigationItem.leftItemsSupplementBackButton = false` | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/). Back is added automatically by a navigation controller ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). See section 5 for the spelling flag |
| Prominent action (Done), never overflows | `ToolbarItemPlacement.topBarPinnedTrailing` | `navigationItem.pinnedTrailingGroup = UIBarButtonItemGroup(...)` | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) |
| Include / exclude an item from the vertical axis | `ToolbarContent.axisBehavior(.automatic / .horizontalOnly / .verticalPreferred)` | `UIBarButtonItem.axisBehavior = .verticalPreferred` / `.horizontalOnly` (works on `UIBarButtonItem(customView:)`) | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) |
| Overflow order | `ToolbarContent.visibilityPriority(_:)` with `ToolbarItemVisibilityPriority` (`.high`, `.low`) | `UIBarButtonItem.visibilityPriority = .high` (`UIBarButtonItemVisibilityPriority`) | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/); HIG names `ToolbarItemVisibilityPriority` and `UIBarButtonItemVisibilityPriority` ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)) |
| Items that live directly in the overflow menu | `ToolbarOverflowMenu { Button("Scan") {…}; Button("Connect") {…} }` | `navigationItem.additionalOverflowItems = UIDeferredMenuElement({ provider in provider(self.persistentOverflowItems()) })` | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) |
| Badges instead of inline counts | `.badge(7)` | `item.badge = .count(7)` | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) |
| Detect which edge holds the vertical bar | `@Environment(\.toolbarVerticalEdge)` | `UITraitCollection.verticalBarEdge: UIVerticalBarEdge` | [Apple] [UITraitCollection.verticalBarEdge](https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge): "reflects the system's preferred edge regardless of whether a vertical bar is currently visible"; returns `UIVerticalBarEdgeUnspecified` "on devices and in contexts where the system never places a vertical bar". SwiftUI type `HorizontalEdge?` (`.leading`, `.trailing`, nil) is [3P] per the research notes (classmethod) |
| Toolbar vs tab bar when space is short | `toolbarVerticalCompressionBehavior(.automatic / .prefersToolbarItems / .prefersTabBar)` | `navigationItem.verticalBarCompressionBehavior = .prefersBarItems` | [Apple] `.prefersToolbarItems` and `.prefersBarItems` appear in Apple code ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)); the research notes trace the full SwiftUI value list (`.automatic`, `.prefersTabBar`) to a third-party article (classmethod), so treat those two as [3P] until checked in the SDK |
| Opt out of vertical bars | `toolbarVerticalBehavior(.automatic / .disabled)` | `override var preferredVerticalBarBehavior: UIVerticalBarBehavior { .disabled }` | [Apple] [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/); named in [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo). Doc URL `https://developer.apple.com/documentation/swiftui/view/toolbarverticalbehavior(_:)` was reported by a third party, not fetched |
| Sheet placement on the inner display | `View.presentationPlacement(_:)` | `UISheetPresentationController.preferredPlacement` | [Apple] [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo). Argument values: Gap (see section 7) |
| Hero art under the bar | `View.backgroundExtensionEffect()` | `UIBackgroundExtensionView` | [Apple] [Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) (symbol names only; no usage text captured) |
| Sidebar on the inner display (not automatic) | `TabView { … }.defaultTabBarPlacement(.sidebar)` | `tabBarController.sidebar.preferredPlacement = .sidebar` | [Apple] [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/); [Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912). `sidebar.preferredPlacement` is an iOS 27 API per the forum answer |

Audit coverage: `duo_audit.py` rules DUO-017 (custom tab/tool bar built from plain views), DUO-018 (navigation bar hidden), DUO-016 (status bar hidden, side inset still applies), DUO-019 (project not upgraded to Xcode 27.1) and DUO-022 (symmetric safe-area math) are the ones that touch bars; the `vertical_bars` adoption check lists which of the symbols above a project already uses.

## 3. Enum values and cases: what is confirmed

| Type | Cases confirmed in Apple code or prose | Not confirmed |
|---|---|---|
| SwiftUI `axisBehavior` argument | `.automatic`, `.horizontalOnly`, `.verticalPreferred` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)) | none recorded |
| `UIBarButtonItem.axisBehavior` | `.verticalPreferred`, `.horizontalOnly` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)) | an `.automatic` case: not recorded |
| `ToolbarItemVisibilityPriority` | `.high`, `.low` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/); report) | `.automatic` ordering `.low < .automatic < .high` and `.init(higherThan: .high)` are [3P] (iPhone-Duo-by-Examples) |
| `UIBarButtonItemVisibilityPriority` | `.high` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)) | other cases: not recorded |
| `toolbarVerticalBehavior` argument | `.automatic`, `.disabled` (report API map, [Apple]) | `UIVerticalBarBehavior` cases beyond `.disabled`: Gap (Appendix C) |
| `UIVerticalBarEdge` | only `UIVerticalBarEdgeUnspecified` is named, in Objective-C form ([UITraitCollection.verticalBarEdge](https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge)) | Swift case names (leading/trailing): Gap (Appendix C) |
| `toolbarVerticalCompressionBehavior` argument | `.prefersToolbarItems` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)) | `.automatic`, `.prefersTabBar`: [3P] value list |
| `verticalBarCompressionBehavior` | `.prefersBarItems` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)) | others: not recorded |
| `presentationPlacement(_:)` / `preferredPlacement` values | none named; Apple describes "centered or leading placements" and "trailing placements" in prose only ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)) | all case names: Gap |

## 4. Context rules: inspectors, split views, sheets, keyboard, Split View, RTL

Verbatim from the Technology Overview ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):

- "**Inspectors.** The system presents bars in inspectors horizontally."
- "**Split views.** In a split view displaying multiple views, the system shows bars horizontally for the sidebar or content view, and vertically for the detail view." Tech Talk 111462 says the same: in split views "only the detail column participates".
- "**Sheets.** On the outer display, the system presents bars vertically for sheets by default. Use `View.toolbarVerticalBehavior(_:)` in SwiftUI or `UIViewController.preferredVerticalBarBehavior` in UIKit to disable vertical presentation for your bars. For sheets on the inner display, the system presents the toolbar horizontally for centered or leading placements, and vertically for trailing placements. Set `View.presentationPlacement(_:)` in SwiftUI or `UISheetPresentationController.preferredPlacement` in UIKit to indicate where you want the system to place the sheet."

From Tech Talk 111462 ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)):

- "Accessory bars stay attached to the keyboard and don't move to the vertical axis."
- Items overflow more "on the outer display in landscape, or when the keyboard or Picture in Picture appears".
- Vertical bars "have no scroll-edge effect by default, but get a background when Reduce Transparency is enabled".
- Vertical bars have "fixed width and flexible item height"; flexible spacers are zero on the vertical axis.
- Toolbars compress before tab bars by default; items overflow bottom-to-top.
- Sheets on the inner display: `preferredPlacement` left = no vertical bar, right = vertical bar (talk summary wording).

From Tech Talk 111466 ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)): "Top toolbar items go to the top of that side space and bottom items go to the bottom. Tab bars stay bottom-aligned"; "Items too wide for the side space, such as text buttons or segmented controls, stay in the nav bar"; sheets "slide away from the fold" when folded.

From the HIG ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)): "Consider using the full display width for interfaces where bars aren't necessary ... as long as nothing conflicts with the Dynamic Island or the status bar. Calculator, for example, occupies the full width". Tech Talk 111466 adds "Mixing approaches is also fine, such as a full-width header with inset scrollable content".

Safe areas: bars sit outside the safe area; horizontal bars provide top/bottom insets, vertical bars provide leading/trailing insets; "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

## 5. Spelling discrepancies in Apple's own material (flag, do not resolve)

The report's Appendix C records two spelling conflicts inside Apple's own Duo material. Tell the user about them; do not pick a spelling on their behalf without checking the SDK headers.

1. `leftItemsSupplementBackButton` vs `leftItemSupplementsBackButton`. The Tech Talk 111462 slide shows `navigationItem.leftItemsSupplementBackButton = false`; the narration says `leftItemSupplementsBackButton` ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). Appendix C status: "Verify in headers". This skill writes the slide spelling because that is what Apple's code shows, and says so.
2. `UIView.ReservedRegion` vs `UIViewReservedRegion`. The docs and HIG use the nested spelling; the Tech Talk 111461 summary uses the flat one ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/); [UIView.reservedRegions(kind:options:)](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:))). Appendix C status: "Use `UIView.ReservedRegion`" (the doc spelling is authoritative). This belongs to duo-layout, but it is flagged here because both discrepancies share the same cause: Tech Talk transcripts were summarized by a fetch tool, and "prose wording should be re-checked against the video page before quoting it as verbatim" (report labelling conventions).

The research notes add a third, lesser one: spoken "reservedRegion" vs code `reservedRegions(kind:)`; the code form is the one on the reference page.

## 6. Third-party observations (unverified)

Useful when debugging, never to be stated as Apple's behavior:

- `toolbarVerticalEdge` is nil when no vertical bar is in use; `.verticalPreferred` only works when the custom label fits the bar; `toolbarVerticalBehavior(.disabled)` inside a sheet affects only that sheet; in a window the behavior comes from the topmost view in a `NavigationStack`, the selected tab, or the trailing-most column (third-party, unverified: nilcoalescing.com).
- `.visibilityPriority(.init(higherThan: .high))` exists and `.low < .automatic < .high` (third-party, unverified: iPhone-Duo-by-Examples).
- The vertical bar adds an 84 pt trailing safe-area inset with zero leading on the outer display (third-party simulator measurement: iPhone-Duo-by-Examples; skarol.dev). Apple publishes no point value.
- `prefersStatusBarHidden = true` hides the icons but not the side inset (third-party: skarol.dev). Audit rule DUO-016 flags it.
- `preferredVerticalBarBehavior` should be "a stable choice, not toggled per navigation state", and segmented controls are "not a good candidate" for the vertical bar (Apple UIKit Q&A as summarized by a third party, Gubarenko Q8/Q18).

## 7. Gaps

Say "Apple has not published this" rather than filling these in:

- `UIVerticalBarEdge` Swift case names and `UIVerticalBarBehavior` cases beyond `.disabled` (Appendix C).
- Argument values for `presentationPlacement(_:)` and `UISheetPresentationController.preferredPlacement`; Apple describes leading/centered/trailing outcomes in prose only.
- Point width of the vertical bar and its inset (only the 84 pt third-party figure exists).
- Any Info.plist key for vertical bars (none exists; opt-in is by SDK and container).
- How `backgroundExtensionEffect()` / `UIBackgroundExtensionView` are configured; only the symbol names were captured.
- Whether `toolbarVerticalBehavior(_:)` has a reference page at the third-party-reported URL; the report did not fetch it.
