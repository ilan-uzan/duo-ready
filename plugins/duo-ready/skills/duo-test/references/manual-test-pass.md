Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# The manual test pass

Contents
1. Apple's audit checklist (verbatim)
2. What to expect in each pose before you start
3. The pass, step by step
4. Hardware-only checks
5. Recording a finding

Labelling: Apple statements carry an Apple link. "(third-party, unverified)" marks developer write-ups and simulator measurements. "(inferred)" marks this repo's reasoning. The order of the pass itself comes from a third-party write-up (SwiftLee, unverified) extended with Apple's Split View instruction and one field report; the checks at each step are Apple's rules.

## 1. Apple's audit checklist (verbatim)

From the Technology Overview ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):

> Confirm your views resize well in each supported orientation and pose.
> Inspect how the system presents your app's navigation bars, toolbars, and tab bars vertically on the side of the display.
> Identify any views, sheets, or popovers that position awkwardly when you fold or open iPhone Duo.
> Identify elements or controls in your views that appear in the fold, and are difficult to see or interact with.

Tech Talk 111463 adds a closing audit for layouts: "Audit your app's centered layouts. Consider a two-column layout or a displacement pattern. Identify your highest-priority manually laid-out controls and adopt the reserved regions API" ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)).

## 2. What to expect in each pose before you start

Size classes by display ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)):

| Display / pose | Horizontal size class | Vertical size class |
|---|---|---|
| Outer display, portrait | compact | regular ("like other iPhone models") |
| Outer display, landscape | compact | compact |
| Inner display, either rotation | regular | regular ("leaving room for sidebars") |

Behaviour Apple documents, so you know what is a bug and what is the system:

- The device idiom stays `.phone`; "iPhone Duo does not support Stage Manager and does not have its own `UIUserInterfaceIdiom`" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644); [Apple Developer Forums 847945](https://developer.apple.com/forums/thread/847945)).
- "The inner display doesn't honor supported interface orientations"; "The outer display honors supported orientations, but the inner display ignores them" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/); [Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). A portrait-only app in a wide inner layout is expected; a broken layout there is the bug.
- Bars go vertical "on the outer display when the device is closed, and for some views in the leading or trailing position on the inner display when the device is open"; "The exception is the inner display in portrait, which has enough vertical space to keep standard horizontal bars" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo); [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- Only system containers move bars: "Content from custom `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)). "If your item has a title and doesn't have an icon, the system doesn't present it vertically. / If your item uses a custom view rather than a title or icon, the system doesn't present it vertically" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- Sidebars are opt-in: "By default, iPhone Duo (and all other iPhones) will not show a sidebar for `UITabBarController` apps, even when its horizontal size class is regular" ([Apple Developer Forums 847912](https://developer.apple.com/forums/thread/847912)).
- A fold is a trait change: "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running"; "Text input, scroll position, and video playback are generally preserved automatically" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Sheets: "On the outer display, the system presents bars vertically for sheets by default ... For sheets on the inner display, the system presents the toolbar horizontally for centered or leading placements, and vertically for trailing placements" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)). Partially folded sheets "slide over to avoid resting in the fold"; fold avoidance is built into sheets, alerts, menus and toolbar buttons; scrollable content need not avoid it ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)).
- Book pose: "alerts move to the trailing side, closer to where they will appear when the device closes"; table pose: "the top region suits content viewed at a distance, such as an alert. The bottom region suits interactive controls, such as media controls" ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)).
- The fold is not in `safeAreaInsets`: "Custom bottom sheets need fold avoidance using reserved regions. Safe-area insets alone are not enough" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- "Accessory bars stay attached to the keyboard and don't move to the vertical axis"; items overflow more "on the outer display in landscape, or when the keyboard or Picture in Picture appears" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).

## 3. The pass, step by step

Do the whole pass with an iOS 27.1 SDK build (confirm the stamp first; see `device-hub-and-simulator.md` section 4). Use Device Hub's Closed, Partially Open and Open buttons, the Option-drag slider, and Rotate Right ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)). Wait a few minutes after boot before trusting screenshots (187146039, [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)).

### Step 1. Launch closed, on the outer display

Check (Apple's audit items 1 and 2):
- The app fills the display to the vertical bar, not a letterboxed strip. A centered app with empty space means an older SDK ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Navigation bar, toolbar and tab bar items are stacked on the side, "the Dynamic Island, the status bar, the toolbar (including navigation buttons), and the tab bar" ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Back or Close is at the top, prominent actions like Done next ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- An empty side rail with the buttons still horizontal means title-only or custom-view items (Apple rule above); a field report saw exactly this with a text "Done" button (third-party, unverified). Route to duo-bars.
- Content pinned top-trailing is not hidden under the status column. A field report lost a close button under the clock and found cards about 42 pt off-centre because insets were mirrored (third-party, unverified); Apple's rule is "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)). Route to duo-layout.
- Full-bleed media does not run under the outer camera; "the outer front-facing camera always occludes your view" ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).

### Step 2. Open the device fully while the app is running

Check (audit items 1 and 3):
- Same screen, same content, same scroll position and selection; Apple says these are "generally preserved automatically" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). A reset to the top of a list or a lost text field means the app rebuilt its hierarchy on the trait change. Route to duo-scenes.
- The layout is a regular-width version of the same hierarchy, not a different app: "Don't reinvent your app when it resizes; allow the existing layout to expand based on the available space instead" ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Mail's example: list or message when closed, both side by side when open.
- A detail screen pushed while compact should not stay stretched across the whole inner display after opening; a field report fixed this by popping and switching to a split when width became regular (third-party, unverified). Route to duo-layout.
- In portrait the bars are horizontal (Apple's exception above); in landscape they are on the side.

### Step 3. Partially open, then pause at several angles with the Option-drag slider

Check (audit items 3 and 4):
- Nothing interactive sits across the fold. Apple: "Identify elements or controls in your views that appear in the fold." Grids should have an even number of columns ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)); a six-column grid centered on the content area put its fourth column on the fold in one field report (third-party, unverified).
- Continuous scrolling content is allowed to cross the fold: "Continuous scrolling content (articles, feeds, documents, lists) does not displace" ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)). Do not file that as a bug.
- System sheets, alerts and menus avoid the fold on their own ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)); custom bottom sheets do not unless they use reserved regions ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Arrangement views, if the app uses them: `.split` shows primary and secondary side by side when wider than tall, stacked when taller; `.overlay` moves the primary view "in the trailing or bottom part of the display relative to the fold" when partially open ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- Movement is small: "Avoid extreme layout changes as people fold the device. Move only what's necessary" ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)). Use Device Hub's Slow Motion Animation (27.2 RC) to watch the transition if it looks jumpy.
- Hinge-driven effects, if any, respond to the slider and stop cleanly when the status leaves `.partiallyOpen` ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)); exact angles are not a pass criterion because they are system policy.

### Step 4. Rotate in both states

Check:
- Outer display landscape is compact / compact: the layout should still be usable, and more items will move to the overflow menu, which is expected ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Inner display rotated stays regular / regular; a portrait-only app lands here regardless of its orientation mask. A tall narrow layout that becomes "wide and short" is a field-reported failure (third-party, unverified) and a duo-layout issue.
- Nothing fakes rotation: "Don't fake rotation by spinning UI elements. Use real size-class-driven layout" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

### Step 5. Split View on the inner display

Drag "the app by the home indicator to either side of the screen, and check vertically laid-out content on both sides" ([Tech Talk 111461](https://developer.apple.com/videos/play/tech-talks/111461/)). Check:
- Each side places controls along its outer edge: "the left app has controls on the left" ([Apple HIG](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- The app works at a half-width scene; "Scene size can't be set directly. It's driven by pose and Split View" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)), so this is the only way to see this width.
- If the app supports multiple windows, a second instance opens only here: "On the outer display of iPhone Duo, new windows cannot be created" ([Tech Talk 111464](https://developer.apple.com/videos/play/tech-talks/111464/)). Close the device with two instances open and confirm the most recently active one stays active while "the secondary window scene would transition to an inactive state, then backgrounded" ([Apple Developer Forums 847838](https://developer.apple.com/forums/thread/847838)).
- A visible app in Split View can be `inactive` (third-party, unverified); media that pauses on resign-active will look frozen. Route to duo-scenes.

### Step 6. Sheets, alerts, menus, popovers and the keyboard, in every pose

Check:
- Sheets on the outer display get vertical bars by default; a sheet with one text-only button leaves an empty rail (Apple rule plus a field report). Apple's own opt-out example is `toolbarVerticalBehavior(.disabled)` for "Control-heavy sheets with only one item" ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Partially open: alerts land on the trailing side in book pose and the top region in table pose ([Tech Talk 111463](https://developer.apple.com/videos/play/tech-talks/111463/)); sheets slide off the fold ([Tech Talk 111466](https://developer.apple.com/videos/play/tech-talks/111466/)).
- Keyboard: the edited field stays visible; Apple expects apps to use `keyboardWillShowNotification`, `keyboardWillHideNotification`, `keyboardWillChangeFrameNotification` ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)). One field report had the keyboard cover the bottom tab rail and a UI test tap the wrong key (third-party, unverified).
- Keyboard accessory bars stay with the keyboard, horizontal ([Tech Talk 111462](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Close the device mid-edit: "the editing session and keyboard survive. The app transitions to the outer display without getting a new scene" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

### Step 7. Verify state survives: scroll, selection, text, playback

Repeat a fold, an open and a rotation with each of: a scrolled list, a selected row, a half-typed field, a playing video. Apple says all four are preserved automatically ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)); any loss is app code tearing down on a trait change (inferred). Bottom sheets are not dismissed on fold, and carousel position is generally preserved (Apple UIKit Q&A as summarised by a third party; unverified wording).

### Step 8. Background, change pose, return

Send the app to the background, change the pose, then return. One Flutter app showed a distorted App Switcher preview only in this sequence (third-party, unverified; [flutter issue #193078](https://github.com/flutter/flutter/issues/193078)). Also check that whatever the app does on `sceneWillResignActive` (privacy blur, pausing) is per-scene when two instances are open (inferred from Split View).

## 4. Hardware-only checks

Plan a device session for anything below; the simulator cannot show it.

- Cameras: "Simulator has no camera, so test on a device before shipping" ([Registering a camera capture accessory on iPhone Duo](https://developer.apple.com/documentation/avfoundation/registering-a-camera-capture-accessory-on-iphone-duo)). Front camera direction changes, Virtual Front Camera switching, mirroring, `CameraCaptureAccessory` on the outer display with an active session.
- Reach and weight: "validate button targets, vertical bars and navigation on physical devices" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Hinge rate and precision (system policy) and any angle-driven effect ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- StandBy (187708663) and most app extensions (187708767) ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)); use a regular iOS 27.1 simulator for extensions in the meantime.
- Accessibility: Apple says to "Test Dynamic Type, contrast, VoiceOver, and resizing across poses using Xcode and Device Hub", but VoiceOver and Accessibility Inspector "cannot convey screen content on an iPhone Duo within Device Hub" (187148389), so VoiceOver verification needs hardware for now ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644); [Xcode 27.2 RC Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)). App Store Connect's "Larger Text" criteria apply, and "For fixed one-screen layouts, holding text at the largest standard size can fail" them ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).
- Performance, memory, thermals and haptics (third-party, unverified list).

## 5. Recording a finding

For each defect write one line with: screen, pose (Closed / Partially Open at roughly what slider position / Open), display, rotation, size classes, what Apple expects (quote the rule), what happened, and the skill that owns the fix. Example:

```
Settings sheet | Closed | outer | portrait | compact/regular
Expected: bar items with an icon present vertically (Preparing your app for iPhone Duo)
Seen: "Done" text-only item; empty side rail
Fix owner: duo-bars (give the item a symbol or toolbarVerticalBehavior(.disabled))
```

Attach the per-display screenshots from `scripts/duo_screenshots.sh` when the defect is visual.
