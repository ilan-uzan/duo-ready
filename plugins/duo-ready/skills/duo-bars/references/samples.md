Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Samples: vertical bars in SwiftUI and UIKit

Two kinds of code appear here. **Apple's code** is reproduced exactly as the report quotes it from an Apple page or Tech Talk, with the source named. **Composed samples** are assembled from those confirmed symbols and carry the header `// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.` Nothing here was compiled; this skill cannot run Xcode 27.1. Long-standing pre-iOS 27 APIs used as scaffolding (`UIBarButtonItem(image:style:target:action:)`, `UIBarButtonItemGroup(barButtonItems:representativeItem:)`, `UIMenu`, `UIAction`, `navigationItem.trailingItemGroups`, SwiftUI `Button(_:systemImage:action:)` and `ToolbarItemPlacement.confirmationAction`) are outside the report's scope and are used as-is. All iOS 27.1-only symbols need `if #available(iOS 27.1, *)` when the deployment target is lower ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)); Mac Catalyst targets need `#if !targetEnvironment(macCatalyst)` around them ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).

## Contents
1. Apple's code, verbatim
2. SwiftUI: a toolbar that survives the vertical bar (composed)
3. SwiftUI: the text-only Done fix, before and after (composed)
4. SwiftUI: opt out for a Calculator-like screen (Apple's code)
5. SwiftUI: toolbar vs tab bar compression per tab (Apple's code)
6. UIKit: navigation item configured for the vertical bar (composed)
7. UIKit: opting a single screen out (composed)
8. Detecting the bar edge (composed, with gaps)
9. Sidebar opt-in on the inner display (Apple's code)
10. Sheets, inspectors and hero art: what cannot be composed yet

## 1. Apple's code, verbatim

From [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/) as recorded in the report and research notes:

```swift
// Opt out (Apple: "Single-page, bottom-heavy layouts such as Calculator" or
// "Control-heavy sheets with only one item")
NavigationStack { ContentView().toolbarVerticalBehavior(.disabled) }

// Prefer toolbar items over the tab bar when the column is short
Tab("Recents", systemImage: "clock") { ContentView().toolbarVerticalCompressionBehavior(.prefersToolbarItems) }

// Axis behavior for custom-view and text items
ToolbarItem { ProfileView() }.axisBehavior(.verticalPreferred)
ToolbarItem { SelectOrDoneButton() }.axisBehavior(.horizontalOnly)

// Items that live in the system overflow menu
ToolbarOverflowMenu { Button("Scan") {…}; Button("Connect") {…} }

// Badges
.badge(7)
item.badge = .count(7)
```

```swift
// UIKit, same talk
navigationItem.leadingItemGroups = [UIBarButtonItemGroup(...)]
navigationItem.leftItemsSupplementBackButton = false   // slide spelling; narration says leftItemSupplementsBackButton. Verify in headers.
navigationItem.pinnedTrailingGroup = UIBarButtonItemGroup(...)
navigationItem.additionalOverflowItems = UIDeferredMenuElement({ provider in provider(self.persistentOverflowItems()) })
navigationItem.verticalBarCompressionBehavior = .prefersBarItems
item.axisBehavior = .verticalPreferred      // also .horizontalOnly; works on UIBarButtonItem(customView:)
item.visibilityPriority = .high
override var preferredVerticalBarBehavior: UIVerticalBarBehavior { .disabled }
```

Apple's slides elide the `UIBarButtonItemGroup(...)` arguments and `persistentOverflowItems()` is Apple's placeholder for a method returning the menu elements.

From [Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/) and [Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912):

```swift
TabView { … }.defaultTabBarPlacement(.sidebar)
tabBarController.sidebar.preferredPlacement = .sidebar
```

## 2. SwiftUI: a toolbar that survives the vertical bar (composed)

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

struct NoteEditor: View {
    @Binding var note: Note
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            NoteCanvas(note: $note)
                .navigationTitle(note.title)
                .toolbar {
                    // Top of the vertical bar: primary navigation (Apple: "Reserve the top for
                    // primary navigation controls, like Back or Close").
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Close", systemImage: "xmark") { dismiss() }
                    }
                    // Next: the prominent action. topBarPinnedTrailing never overflows.
                    ToolbarItem(placement: .topBarPinnedTrailing) {
                        Button("Done", systemImage: "checkmark") { save() }
                    }
                    // Every item has a symbol (vertical bar) and a title (overflow menu).
                    ToolbarItem {
                        Button("Share", systemImage: "square.and.arrow.up") { share() }
                    }
                    .visibilityPriority(.high)
                    ToolbarItem {
                        Button("Comments", systemImage: "bubble.left") { showComments() }
                    }
                    .badge(note.unreadComments)
                    ToolbarItem {
                        Button("Tag", systemImage: "tag") { tag() }
                    }
                    .visibilityPriority(.low)
                    // Rarely used actions go straight to the system overflow menu.
                    ToolbarOverflowMenu {
                        Button("Export", systemImage: "arrow.up.doc") { export() }
                        Button("Move to Folder", systemImage: "folder") { move() }
                    }
                }
        }
    }
}
```

What this relies on: `toolbar(content:)` on a `NavigationStack` is the container Apple names ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)); `.cancellationAction`, `.topBarPinnedTrailing`, `.visibilityPriority(_:)`, `ToolbarOverflowMenu`, `.badge(_:)` are from [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/). Where `.badge` attaches (ToolbarItem vs the Button) is not shown in Apple's snippet; the report records only `.badge(7)`.

## 3. SwiftUI: the text-only Done fix, before and after (composed)

Field report (third-party, unverified: blakecrosley.com worked example): a sheet whose only bar item was a text "Done" button "reserved the side rail and left it empty", because "If your item has a title and doesn't have an icon, the system doesn't present it vertically" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). Two Apple-consistent fixes: give the item a symbol, or opt the sheet out ("Control-heavy sheets with only one item", [Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

// Before: title-only item. Not presented vertically; the rail can be reserved but empty.
struct FilterSheetBefore: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            FilterList()
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Done") { dismiss() }
                    }
                }
        }
    }
}

// After, option A: symbol plus title, so the item rides the vertical bar on the outer
// display and still reads as "Done" in an overflow menu.
struct FilterSheetAfterA: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            FilterList()
                .toolbar {
                    ToolbarItem(placement: .topBarPinnedTrailing) {
                        Button("Done", systemImage: "checkmark") { dismiss() }
                    }
                }
        }
    }
}

// After, option B: a one-item sheet is one of Apple's two sanctioned opt-out cases.
struct FilterSheetAfterB: View {
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            FilterList()
                .toolbarVerticalBehavior(.disabled)
                .toolbar {
                    ToolbarItem(placement: .confirmationAction) {
                        Button("Done") { dismiss() }
                    }
                }
        }
    }
}
```

Pick A when the sheet has, or will grow, more than one action. Pick B only for a genuinely one-button sheet, and apply the same choice to every similar sheet in the app; a third-party report says mixing behaviours across screens "makes buttons jump around" (skarol.dev, unverified) and Apple's own Q&A (third-party summary) calls the UIKit equivalent "a stable choice, not toggled per navigation state".

## 4. SwiftUI: opt out for a Calculator-like screen (Apple's code)

```swift
// Apple's code, Tech Talk 111462. Opt-out is for "Single-page, bottom-heavy layouts such as Calculator".
NavigationStack { ContentView().toolbarVerticalBehavior(.disabled) }
```

The HIG's matching design permission: "Consider using the full display width for interfaces where bars aren't necessary ... as long as nothing conflicts with the Dynamic Island or the status bar" ([HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Opting out does not remove the status bar's side inset; keep interactive content inside the safe area.

## 5. SwiftUI: toolbar vs tab bar compression per tab (Apple's code)

```swift
// Apple's code, Tech Talk 111462.
Tab("Recents", systemImage: "clock") { ContentView().toolbarVerticalCompressionBehavior(.prefersToolbarItems) }
```

Default: toolbars compress before tab bars. Use this on a tab whose toolbar actions matter more than the tab strip when the column is short (outer display landscape, keyboard, Picture in Picture).

## 6. UIKit: navigation item configured for the vertical bar (composed)

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

final class NoteEditorViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        // This view controller must be inside a UINavigationController (or a
        // UITabBarController) for the system to own and move its bars.

        let close = UIBarButtonItem(image: UIImage(systemName: "xmark"), style: .plain,
                                    target: self, action: #selector(closeTapped))
        close.title = "Close"   // title is used in overflow menus and expanded forms

        let done = UIBarButtonItem(image: UIImage(systemName: "checkmark"), style: .done,
                                   target: self, action: #selector(doneTapped))
        done.title = "Done"

        let share = UIBarButtonItem(image: UIImage(systemName: "square.and.arrow.up"), style: .plain,
                                    target: self, action: #selector(shareTapped))
        share.title = "Share"
        share.visibilityPriority = .high

        let comments = UIBarButtonItem(image: UIImage(systemName: "bubble.left"), style: .plain,
                                       target: self, action: #selector(commentsTapped))
        comments.title = "Comments"
        comments.badge = .count(7)

        // Top of the vertical bar: Close. Apple shows leadingItemGroups together with
        // leftItemsSupplementBackButton = false (slide spelling; narration differs).
        navigationItem.leadingItemGroups = [
            UIBarButtonItemGroup(barButtonItems: [close], representativeItem: nil)
        ]
        navigationItem.leftItemsSupplementBackButton = false

        // Prominent action that never overflows.
        navigationItem.pinnedTrailingGroup =
            UIBarButtonItemGroup(barButtonItems: [done], representativeItem: nil)

        navigationItem.trailingItemGroups = [
            UIBarButtonItemGroup(barButtonItems: [share, comments], representativeItem: nil)
        ]

        // Rare actions straight into the system overflow menu.
        navigationItem.additionalOverflowItems = UIDeferredMenuElement({ provider in
            provider(self.persistentOverflowItems())
        })

        // Keep toolbar items over the tab bar when the column is short.
        navigationItem.verticalBarCompressionBehavior = .prefersBarItems
    }

    private func persistentOverflowItems() -> [UIMenuElement] {
        [
            UIAction(title: "Export", image: UIImage(systemName: "arrow.up.doc")) { _ in },
            UIAction(title: "Move to Folder", image: UIImage(systemName: "folder")) { _ in },
        ]
    }

    @objc private func closeTapped() {}
    @objc private func doneTapped() {}
    @objc private func shareTapped() {}
    @objc private func commentsTapped() {}
}
```

Note: `navigationItem.trailingItemGroups` is a pre-existing UIKit property used here as the natural counterpart of `leadingItemGroups`; the report records only `leadingItemGroups` and `pinnedTrailingGroup` from Apple's Duo material.

A custom view that must stay in the bar:

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
let avatarItem = UIBarButtonItem(customView: avatarView)
avatarItem.axisBehavior = .verticalPreferred   // otherwise custom views are not presented vertically

let scopeControl = UIBarButtonItem(customView: segmentedControl)
scopeControl.axisBehavior = .horizontalOnly    // segmented controls stay in the nav bar
```

## 7. UIKit: opting a single screen out (composed)

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

final class CalculatorViewController: UIViewController {
    // Apple's form (Tech Talk 111462). Make this a stable choice for the screen,
    // not something toggled as navigation state changes.
    override var preferredVerticalBarBehavior: UIVerticalBarBehavior { .disabled }
}
```

`UIVerticalBarBehavior` cases other than `.disabled` are not enumerated in the report (Appendix C gap); do not invent an `.automatic` or `.enabled` name without checking the header.

## 8. Detecting the bar edge (composed, with gaps)

Use the edge to refine content (for example, which side a floating control hugs), never to decide the overall layout; layout comes from size classes ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import SwiftUI

struct PlaybackScrubber: View {
    @Environment(\.toolbarVerticalEdge) private var barEdge
    var body: some View {
        // barEdge is nil when no vertical bar is in use (third-party, unverified);
        // the HorizontalEdge? type is reported by a third party, not read from an Apple page.
        ScrubberBody()
            .padding(barEdge == .trailing ? .leading : .trailing, 16)
    }
}
```

```swift
// Composed from Apple-documented APIs; not yet compile-checked against the iOS 27.1 SDK.
import UIKit

final class PlayerViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        // Apple: verticalBarEdge "reflects the system's preferred edge regardless of whether a
        // vertical bar is currently visible" and returns UIVerticalBarEdgeUnspecified where the
        // system never places one. The Swift case names are not in the report; read the header
        // before comparing against a case.
        let edge = traitCollection.verticalBarEdge
        _ = edge
    }
}
```

Source: [UITraitCollection.verticalBarEdge](https://developer.apple.com/documentation/uikit/uitraitcollection/verticalbaredge).

## 9. Sidebar opt-in on the inner display (Apple's code)

```swift
// Apple's code, Tech Talk 111461.
TabView { … }.defaultTabBarPlacement(.sidebar)
```

```swift
// Apple's code, Apple Developer Forums 847912 (Apple Frameworks Engineer).
tabBarController.sidebar.preferredPlacement = .sidebar
```

Without this, "tab bar apps will have either a vertical or horizontal tab bar on the inner display" ([Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912)). The inner display is regular width in both rotations ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)), which is what makes a sidebar viable there.

## 10. Sheets, inspectors and hero art: what cannot be composed yet

- **Sheet placement.** Apple names `View.presentationPlacement(_:)` and `UISheetPresentationController.preferredPlacement` and says the inner display shows the toolbar "horizontally for centered or leading placements, and vertically for trailing placements" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). The argument values are not in the report, so no sample is given. Tell the user to read the parameter type in Xcode's documentation viewer and choose a trailing placement if they want the vertical bar on an inner-display sheet.
- **Inspectors** always get horizontal bars ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)); nothing to configure.
- **Split views**: sidebar and content columns horizontal, detail vertical ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)); nothing to configure beyond using `NavigationSplitView` / `UISplitViewController`.
- **Hero art under the bar.** `View.backgroundExtensionEffect()` and `UIBackgroundExtensionView` are named for this ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)); the report captured no usage text, so only the names are given here. Keep interactive content inside the safe area and let only background artwork extend past it ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)).
