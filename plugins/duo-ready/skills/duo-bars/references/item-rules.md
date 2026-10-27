Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Apple's bar-item rules, verbatim

Every quotation below is Apple's wording as recorded in the report, with the page it came from. Tech Talk quotations come from transcript summaries; API names and numbers are preserved, prose wording should be re-checked against the video page before quoting it as verbatim (report labelling conventions). Nothing here is third-party.

## 1. Which items can go vertical at all

[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

> "The system uses an icon for an item it presents vertically. / The system uses an icon or a title for an item it presents horizontally, preferring an icon. / The system uses an icon and title for an item in an overflow menu. / If your item has a title and doesn't have an icon, the system doesn't present it vertically. / If your item uses a custom view rather than a title or icon, the system doesn't present it vertically."

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/): icon items go vertical, text-only stay horizontal; custom-view items are not shown vertically unless opted in with `.verticalPreferred`.

[Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/):

> "Items too wide for the side space, such as text buttons or segmented controls, stay in the nav bar."

Consequence (Apple's rules combined; the combination is the report's reading, not a quote): an item needs an SF Symbol to ride the vertical bar, and a title to be legible in the overflow menu. Give every item both.

## 2. Always provide a title too

[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo) / [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/):

> "Even if your content is an image, it's still important to provide a title"

[HIG Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo):

> "Provide both a title and a symbol for each toolbar item that isn't text-only... the system uses the title in overflow menus and expanded forms."

> "Keep text-based buttons to a minimum"

## 3. Order of items in the vertical bar

[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

> "Reserve the top for primary navigation controls, like Back or Close, followed by prominent actions, such as Done. If you use a navigation controller, the system adds the Back button automatically"

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/): order is `.cancellationAction` (back/close) at the top, then `.topBarPinnedTrailing` / `pinnedTrailingGroup` (Done) next; the shared vertical region is "like rotating 90 degrees into a vertical stack"; toolbars compress before tab bars by default; items overflow bottom-to-top; `visibilityPriority` applies to groups first, then items.

[Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/):

> "Top toolbar items go to the top of that side space and bottom items go to the bottom. Tab bars stay bottom-aligned"

## 4. Spacing and grouping

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/): flexible spacers are zero on the vertical axis, and

> "Don't add extra spacing, whether the bar is horizontal or vertical"

[HIG Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo):

> "Group related toolbar items instead of spacing them manually... avoid adding fixed spacing yourself."

## 5. Overflow menu and badges

[HIG Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo):

> "If your app has its own overflow menu, move those actions into the system menu"

> "Reserve the ellipsis symbol for overflow, and give other menus a distinct symbol."

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/): reserve the ellipsis for overflow "rather than introducing symbols from other platforms"; use badges (`.badge(7)`, `item.badge = .count(7)`) instead of inline counts; items overflow more "on the outer display in landscape, or when the keyboard or Picture in Picture appears".

[HIG Layout](https://developer.apple.com/design/human-interface-guidelines/layout) (general, updated Sept 9, 2026):

> "Consider taking advantage of larger spaces to switch from a tab bar to a sidebar or expose functionality that might otherwise be grouped into an overflow menu."

## 6. Do not override the pattern without a reason

[HIG Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo):

> "Follow the system's vertical layout for toolbars, tab bars, and navigation controls. Because the outer display is wider and shorter than the display on other iPhone devices, the system moves controls to the side to preserve vertical space for content and reflect the asymmetry of the display. On the inner display, controls remain on the side in landscape to preserve a continuous experience at the same vertical height. If you use standard system components, you receive this layout automatically, but you may want to refine it based on the needs of your app."

> "In general, don't override the default bar placement. The position of controls on the vertical axis is one of the core patterns of iPhone Duo."

> "Keep controls consistent across device poses... keep controls' relative positions as similar as possible so people don't have to relearn where actions live as they change between poses."

> "Maintain the same functionality across device poses. Controls may overflow and content may move or change size as the interface adapts to the available area. Provide access to the same controls and content regardless of how someone holds or views the device."

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/), the sanctioned opt-out cases: "Single-page, bottom-heavy layouts such as Calculator" or "Control-heavy sheets with only one item". Apple's code: `NavigationStack { ContentView().toolbarVerticalBehavior(.disabled) }`.

[HIG Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo), the full-width exception:

> "Consider using the full display width for interfaces where bars aren't necessary ... as long as nothing conflicts with the Dynamic Island or the status bar. Calculator, for example, occupies the full width"

Calculator's layout change is quantified: iPhone 16 uses "four columns of five items", the Duo outer display "five columns of four items" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).

Apple UIKit Q&A, as summarized by a third party (Gubarenko Q8, Q18): `preferredVerticalBarBehavior` should be "a stable choice, not toggled per navigation state"; segmented controls are "not a good candidate" for the vertical bar.

## 7. Which bars count

[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

> "If the system doesn't present your bars vertically, check that you're using the bar support that navigation containers, such as a tab view or navigation stack, provide. In SwiftUI, add the `toolbar(content:)` modifier to a `NavigationStack` or `NavigationSplitView`. In UIKit, set toolbar items on a view controller that you add to a navigation controller, instead of creating a custom bar for your view based on `UIToolbar`, `UINavigationBar`, or `UITabBar`."

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/):

> "Content from custom `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered"

> "Accessory bars stay attached to the keyboard and don't move to the vertical axis"

[Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912), Apple Frameworks Engineer:

> "By default, iPhone Duo (and all other iPhones) will not show a sidebar for `UITabBarController` apps, even when its horizontal size class is regular. Sidebars are opt-in on iPhone via the iOS 27 API: `tabBarController.sidebar.preferredPlacement = .sidebar`. Otherwise, by default, tab bar apps will have either a vertical or horizontal tab bar on the inner display"

SwiftUI equivalent: `TabView { … }.defaultTabBarPlacement(.sidebar)` ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

## 8. Audit checklist Apple gives for testing bars

[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo):

> "Inspect how the system presents your app's navigation bars, toolbars, and tab bars vertically on the side of the display."

> "Identify any views, sheets, or popovers that position awkwardly when you fold or open iPhone Duo."

[Three steps](https://developer.apple.com/iphone-duo/prepare/): "Before shipping with this SDK, confirm your content adapts to the vertical bars".

[Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/): vertical bars "have no scroll-edge effect by default, but get a background when Reduce Transparency is enabled. Keep content legible either way."

## 9. Rule-to-API mapping (the report's reading, not Apple's wording)

| Apple rule | What to change |
|---|---|
| Title-only items are not presented vertically | Give the item a symbol: SwiftUI `Button("Done", systemImage: "checkmark")`-style labels, UIKit `UIBarButtonItem` with an `image` plus a `title` |
| Custom-view items are not presented vertically | Prefer icon+title items; if the custom view must stay, `.axisBehavior(.verticalPreferred)` / `UIBarButtonItem.axisBehavior = .verticalPreferred` and accept that it only works if it fits (fit limit is third-party, unverified) |
| Text buttons and segmented controls stay in the nav bar | Mark them `.axisBehavior(.horizontalOnly)` so the layout is explicit, or move the choice into a menu |
| Back/Close top, Done next | `.cancellationAction` / `leadingItemGroups`; `.topBarPinnedTrailing` / `pinnedTrailingGroup` |
| Own overflow menu | Replace with `ToolbarOverflowMenu` / `additionalOverflowItems`; keep the ellipsis for it |
| Inline counts | `.badge(7)` / `item.badge = .count(7)` |
| Manual spacing | Remove fixed spacers; group related items (`UIBarButtonItemGroup`) |
| Toolbar vs tab bar fight for the column | `toolbarVerticalCompressionBehavior(.prefersToolbarItems)` / `verticalBarCompressionBehavior = .prefersBarItems`, per tab |
| Calculator-like single screen or one-item sheet | `toolbarVerticalBehavior(.disabled)` / `preferredVerticalBarBehavior` returning `.disabled`, applied consistently |
