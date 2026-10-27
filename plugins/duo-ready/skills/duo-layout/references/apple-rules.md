Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# Apple's layout rules for iPhone Duo, verbatim

Quotations are Apple's words as captured in the report. Documentation and HIG text was fetched
from Apple's Markdown endpoints; Tech Talk text comes from transcript summaries, so API names
and numbers are exact but prose should be re-checked against the video page before being
quoted as verbatim. Forum quotes are from Apple DTS or Apple Frameworks Engineers.

Contents

1. The core principle
2. Size classes, idiom, orientation
3. Screen, scene and container bounds
4. Safe areas and layout margins
5. Reserved regions
6. Arrangement views
7. Displacement, grids and centered layouts
8. Fold continuity
9. Games and aspect ratio
10. Testing checklist
11. Statements about what Apple has not published

Sources

- Preparing: [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)
- Three steps: [Three steps to make your app shine on iPhone Duo](https://developer.apple.com/iphone-duo/prepare/)
- HIG: [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- HIG Layout: [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- TT 111461: [Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/)
- TT 111463: [Strike a pose with adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/)
- TT 111464: [Leverage multiple displays and scenes on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111464/)
- TT 111466: [Design for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111466/)
- Forums 847644: [A Summary of the iPhone Duo Group Lab](https://developer.apple.com/forums/thread/847644)
- Forums 847945: [idiom stays .phone](https://developer.apple.com/forums/thread/847945)
- Forums 847887: [DTS on compatibility behaviour](https://developer.apple.com/forums/thread/847887)
- TN3192: [Migrating your app from the deprecated UIRequiresFullScreen key](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)
- Reference pages: [ArrangementView](https://developer.apple.com/documentation/swiftui/arrangementview), [GeometryProxy.reservedRegions](https://developer.apple.com/documentation/swiftui/geometryproxy/reservedregions(kind:options:layoutdirectionbehavior:)), [ReservedRegion](https://developer.apple.com/documentation/swiftui/reservedregion), [UIView.reservedRegions](https://developer.apple.com/documentation/uikit/uiview/reservedregions(kind:options:)), [UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion), [UIArrangementViewController](https://developer.apple.com/documentation/uikit/uiarrangementviewcontroller)
- Device Hub: [Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)
- Specs: [iPhone Duo Tech Specs](https://www.apple.com/iphone-duo/specs/)

## 1. The core principle

- "Resizing is a key feature for your app on iPhone Duo. If your app already works on iPad and Mac or you've prepared your app to resize in iPhone Mirroring, you're well on your way to supporting iPhone Duo. If not, adopt standard layout controls and containers, and use size classes and scene geometry to improve your app's resizing. Then, handle reserved regions such as the fold to resize your app and handle folded layouts. Evaluate whether an arrangement view can assist your app's layout to handle the fold." (Preparing)
- "Prefer system-provided layouts and containers, such as split views, tab bars, arrangement views, and navigation stacks. These handle resizing, automatically adjusting for the outer display, fully open or folded inner display, and camera occlusions. / Size your views relative to their container rather than to fixed iPhone dimensions. / Make layout calculations based on your scene or containing view's bounds rather than screen dimensions. / Adopt Auto Layout in UIKit to make your views resizable. / Use automatic trait tracking to observe `UITraitCollection.horizontalSizeClass` and `UITraitCollection.verticalSizeClass` changes to adapt your interface to different sizes. Don't use `UIDevice.userInterfaceIdiom` or `UIInterfaceOrientation` for layout decisions in your UIKit app." (Preparing)
- "Build your app to resize" ... "Avoid fixed widths and display-specific dependencies". (HIG, first of five bolded best practices)
- "Supporting the device's various poses doesn't mean designing a custom layout for each one: instead, use size classes so your app adapts naturally as it changes size. A compact width layout for the outer display and a regular width layout for the inner display give you the fundamentals for every pose. Don't reinvent your app when it resizes; allow the existing layout to expand based on the available space instead." (HIG)
- "Determine layout based on size classes, not device type or orientation." "iOS and iPadOS apps can exist in every combination of size classes." "Don't change your app's functionality based on the space it occupies." (HIG Layout)

## 2. Size classes, idiom, orientation

- Size classes: outer display "regular vertical and compact horizontal size class in portrait; compact vertical and horizontal in landscape, like other iPhone models. Inner display: regular horizontal and vertical size classes, leaving room for sidebars." (TT 111461)
- "you are not required to support iPad to support the iPhone Duo as its device idiom is still `.phone`. In iOS 27, iPhone apps on both the iPhone Duo and iPhone Mirroring (in macOS 27) will see iPhone apps have regular size classes when resized" (Forums 847945, Apple Frameworks Engineer)
- "iPhone Duo is not a separate device class ... iPhone Duo does not support Stage Manager and does not have its own `UIUserInterfaceIdiom`"; "apps can't require iPhone Duo-specific capabilities"; "Apps don't need iPad support first". (Forums 847644)
- "With iPhone Duo and resizable iPhone Mirroring, iPhone apps can have any combination of size classes"; "Don't choose a layout by idiom"; "Don't treat 'regular width' as 'iPad.'"; "Remove checks for specific device sizes". (Three steps)
- "The inner display doesn't honor supported interface orientations, so use size classes rather than orientation for layout decisions. Landscape support is still valuable on the outer display, since people may use the device like a tent." (TT 111461)
- To "Is there a sanctioned way to lock the inner display to portrait only?": "No. The inner display doesn't honor your supported interface orientations — avoid checking orientation for layout decisions and use size classes instead." (Forums 847644). The same thread, in a compatibility-mode answer, also says "Yes, iPhone Duo still honors UISupportedInterfaceOrientations, but the expected behavior for this device differs from previous iPhone devices in certain hinge states and orientations. Instead, use size classes..." The first wording matches TT 111461 and is the operative guidance; do not rely on either as a layout mechanism.
- "Portrait-only apps ... still receive compact and regular size class changes. The outer display honors supported orientations, but the inner display ignores them." Overriding `horizontalSizeClass` "would likely interfere with system updates". (Forums 847644)
- "the system still determines your scene's supported interface orientations by comparing the orientations your app declares — through `supportedInterfaceOrientations`, your `Info.plist`, or `application(_:supportedInterfaceOrientationsFor:)` — against the orientations the device itself supports." Orientation lock requests via `prefersInterfaceOrientationLocked` plus `setNeedsUpdateOfPrefersInterfaceOrientationLocked()` are not guaranteed to be honored. (TN3192)
- "Don't fake rotation by spinning UI elements. Use real size-class-driven layout." (Forums 847644)
- "Apps don't need to know which face is up. Use size classes." (Forums 847644)

## 3. Screen, scene and container bounds

- Step 2, "Stop sizing from the main screen": replace `UIScreen.main` with `view.bounds`, `window.bounds`, `GeometryReader`, or `onGeometryChange`; re-read size in `layoutSubviews`, `viewDidLayoutSubviews`, or `viewWillTransition(to:with:)` "because a fold can resize your app in the middle of a session"; get scale from `traitCollection.displayScale` or `@Environment(\.displayScale)`; create windows with `UIWindow(windowScene:)`; "Don't store a `UIScreen`", access it via `view.window?.windowScene?.screen`. (Three steps)
- Step 2, "Don't use orientation for layout": remove logic based on `UIDevice.current.orientation`, `statusBarOrientation`, `interfaceOrientation`, or `windowScene.effectiveGeometry.interfaceOrientation`; compare available width vs height instead. (Three steps)
- Step 2, "Check full-bleed media ... choose fill or fit based on size class or aspect ratio, or set a focal point"; fill "can lose important content on wider displays". (Three steps)
- `UIScreen.main` is "ambiguous on two-display devices and will be deprecated in a future release". "Avoid referencing the main screen on two-display devices. Use the environment, trait collection, or scene bounds, and access the screen dynamically from the window scene." (TT 111461)
- "Scene size can't be set directly. It's driven by pose and Split View"; "Free-form drag-to-resize isn't supported". (TT 111466)
- "With a discrete resize, the scene doesn't change size while people drag the window. When they finish, the `coordinateSpace.bounds` of the scene's `effectiveGeometry` changes, and the scene moves to a `UIScreen` of exactly the same size." (TN3192)

## 4. Safe areas and layout margins

- Bars sit outside the safe area; horizontal bars provide top/bottom insets, vertical bars provide leading/trailing insets; "Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently." (TT 111461)
- "Keep interactive content inside the safe area and let background artwork extend past it." (TT 111461)
- Code forms: `foreground.frame = view.bounds.inset(by: view.safeAreaInsets)` with `backgroundView.frame = view.bounds`; replace `view.bounds.width - view.safeAreaInsets.left * 2` with `view.bounds.inset(by: view.safeAreaInsets).width`. (TT 111461)
- "Custom bottom sheets need fold avoidance using reserved regions. Safe-area insets alone are not enough." Custom UI overlapping the camera region without the API has touch "suppressed or may not register as expected". (Forums 847644)
- "Interactions that look fine in the simulator may feel awkward on hardware due to reachability, asymmetric safe areas, and weight distribution". (Forums 847644)

## 5. Reserved regions

- "your custom views need a flexible approach to identify *divisions* and *occlusions*. iOS represents these as *reserved regions*. A division occurs when a folding region divides a large view into smaller views. An occlusion is an area of a view where a hardware element, such as the camera, covers your content so it isn't visible. The inner front-facing camera can block your view when it's active, and the outer front-facing camera always occludes your view." (Preparing)
- "In SwiftUI, use a `GeometryReader` to get a `GeometryProxy`, then get an array of `ReservedRegion` instances from `GeometryProxy.reservedRegions(kind:options:layoutDirectionBehavior:)`. In UIKit, get an array of `UIView.ReservedRegion` instances from `UIView.reservedRegions(kind:options:)`. Inspect the frames of the reserved regions, and adjust your views accordingly." (Preparing)
- "Note: A reserved region can be active or inactive. For example, a reserved region that represents the fold is active when iPhone Duo is partially open, but inactive when it is fully open." (Preparing)
- "**The outer front-facing camera.** This region is always present, and expands into the Dynamic Island for Live Activities ... **The inner front-facing camera.** This region is only present when the camera is active ... **The folding region.** This region is conditional ... When the device is partially open, the folding region divides the inner display into multiple usable regions". (HIG)
- "Use the `ReservedRegion` API to keep important elements clear of the center if the system doesn't move them automatically". (HIG)
- Returns "the reserved regions that overlap the view, with frames in the view's coordinate space"; each region "describes a frame, margins, active state, and an identifier". `ReservedRegion.Kind.occlusion`: "An area that covers your content, such as the Dynamic Island, a camera, or window controls". `ReservedRegion.Kind.division`: "An area where content splits into separate regions, such as the fold of a hinge". Custom `Layout` caveat: `bounds` in `placeSubviews` don't always start at (0,0); compute from (0,0) and add `bounds.origin`. (GeometryProxy.reservedRegions reference)
- `ReservedRegion.frame`: "Coordinates are relative to the view, with `(0, 0)` at the top-leading corner, and the frame already includes `margins`." `margins`: "Extra space around the reserved area that keeps interactive content clear of it." `isActive`: "Indicates whether the region currently affects the view." (ReservedRegion reference, verified 2026-10-26)
- "UIKit tracks the regions you read in `updateConstraints()` and runs it again when the regions change." (UIView.reservedRegions reference)
- "The fold's division region is active only when the device is folded. When flat, it is inactive with a width of zero"; "Inactive regions still support high-level decisions. For example, prefer an even number of grid columns whenever a division region is present, whether or not it is currently active". (TT 111463)
- "not every app needs to use Arrangement Views or the reserved regions API". (Forums 847887, DTS)

## 6. Arrangement views

- "`ArrangementView` in SwiftUI and `UIArrangementViewController` in UIKit represent an *arrangement view*, which is a layout container for a primary view and a secondary view that you can use to adjust to the different device poses. Arrangement views offer two styles of preferred arrangements: split and overlay." (Preparing)
- Split "presents the primary and secondary views side by side when the containing view is wider than it is tall; or it places the primary view on top and the secondary view below it when the containing view is taller than it is wide. The arrangement view adjusts the placement of the primary and secondary views to adapt to reserved regions, such as the folding region." Use where you would use `HStack`/`VStack`. (Preparing)
- Overlay "positions the primary view on top of the secondary view when there aren't any active reserved regions that are divisions. This is true when iPhone Duo is closed or fully open. When iPhone Duo is partially open, the overlay arrangement places the primary view in the trailing or bottom part of the display relative to the fold, and the secondary view in the leading or top part of the display relative to the fold." Use where you would use `ZStack`. (Preparing)
- Inputs are "horizontal and vertical size classes, the view's width-to-height aspect ratio, and any active division regions"; outputs are "whether each view is shown and its frame"; "If the arrangement cannot split along its primary axis, it shows only one view"; "When a closed iPhone Duo is held in landscape, only the primary view is shown"; "Choose **overlay** for a clear foreground/background relationship ... Choose **split** for a main/detail relationship". (TT 111463; ArrangementView reference)
- "Avoid placing an arrangement view inside a navigation split view, list, scroll view, or other container that might cause part of your view to become inaccessible." (Preparing)
- "Keep navigation outside of arrangement views. An arrangement view lays out content but doesn't handle navigation, so place navigation containers like navigation split views and tab views around it rather than within it." (HIG)
- "Avoid putting it inside another layout container, such as a scroll view, navigation split view, grid ... Also avoid placing container views such as a navigation split view or tab view inside it." (ArrangementView reference)
- "Consider an arrangement view when your layout already resembles one". (HIG)
- `overlayArrangementZIndex`: "Use this value to read the z-ordering of a view when it is placed in an overlay arrangement. Views with a higher z-index are rendered on top of views with a lower z-index." (reference, verified 2026-10-26)
- `splitArrangementAxis`: "Use this value to read the axis that a split arrangement is using to place its views. Views can adapt their layout or appearance based on whether the split is horizontal or vertical. The value is `nil` when the view is not contained within a split arrangement view." (reference, verified 2026-10-26)
- `ArrangementView` and `UIArrangementViewController` are "Available on any iPhone or iPad running iOS 27.1+, not exclusive to iPhone Duo"; Apple recommends "gating iOS 27.1 APIs behind availability checks". (Forums 847644)

## 7. Displacement, grids and centered layouts

- "Continuous scrolling content (articles, feeds, documents, lists) does not displace. It already adapts through scrolling"; move elements "independently when they can adapt alone, and together when they work as a unit"; "Avoid excessive movement". (TT 111463)
- Reminders' split view "keeps both columns visible in an even 50/50 split" when folded; Fitness's grid "outer margins are preserved while spacing around the hinge increases"; search fields "stay over the keyboard or the view they search, and their width and position adapt as the device folds". (TT 111463)
- Book pose (partially folded): "alerts move to the trailing side, closer to where they will appear when the device closes". Table pose (propped up): "the top region suits content viewed at a distance, such as an alert. The bottom region suits interactive controls, such as media controls". (TT 111463)
- "Audit your app's centered layouts. Consider a two-column layout or a displacement pattern. Identify your highest-priority manually laid-out controls and adopt the reserved regions API." (TT 111463)
- "Adapt your layout when the device folds. Prefer a layout container that adapts automatically ... In a grid-style layout, prefer an even number of columns so content divides cleanly." (HIG)
- "Avoid extreme layout changes as people fold the device. Move only what's necessary ... favor small adjustments over rearrangement." (HIG)
- "Because the outer display is wider and shorter than the display on other iPhone devices, the system moves controls to the side to preserve vertical space for content and reflect the asymmetry of the display." Calculator: iPhone 16 uses "four columns of five items", the Duo outer display "five columns of four items". (HIG)
- "An optional special layout ... for seated, hands-free use, but it must keep the same controls and hierarchy as other poses. Don't tie functionality to a pose". (TT 111466)
- "Consider using the full display width for interfaces where bars aren't necessary ... as long as nothing conflicts with the Dynamic Island or the status bar." (HIG) "Mixing approaches is also fine, such as a full-width header with inset scrollable content". (TT 111466)

## 8. Fold continuity

- "Opening or closing the device, or switching displays, is treated as a size-class and trait change, not a scene disconnect or app termination. The process keeps running"; "Text input, scroll position, and video playback are generally preserved automatically. Apps usually don't need `scrollPosition(id:)` for LazyVGrid column changes"; "An active editing session survives the hinge transition without getting a new scene"; "For state that must survive a true scene disconnect/reconnect, implement `stateRestorationActivity(for:)` and save an `NSUserActivity`"; animations "should be able to start, pause, and stop at any time. Use `TimelineView` or `CADisplayLink` for custom timing"; "Hinge changes are just geometry/trait changes". (Forums 847644)
- "Create a consistent experience across displays. Keep functionality and the state of elements the same between displays. Maintain your app's information hierarchy, but show an additional level of hierarchy on the larger inner display if it makes sense ... Mail, for example, shows either a list of emails (primary) or an email (secondary) when the device is closed. When it's open, it shows both side by side." "Maintain the same functionality across device poses". (HIG)
- Split views "expand on the inner display and collapse to a single pane on the outer display". (HIG)
- "The app continues to honor `UIRequiresFullScreen`, but still resizes when the device opens or closes." (TT 111461) "Starting in iOS 27 and iPadOS 27, `UIRequiresFullScreen` no longer opts your app out of resizing on either platform. Instead, the system resizes your app's scene discretely." (TN3192)
- "if your app is in full-screen using the entire open flat inner display, the scene is unaffected by the hinge state change". (Forums 847838, DTS)

## 9. Games and aspect ratio

- "Make your game playable in every device pose." "You can choose to lock to either portrait or landscape orientation, but be sure to fill the screen as the device pose changes ... Prefer changing the aspect ratio over letterboxing or pillarboxing in games; if you can't avoid letterboxing or pillarboxing, add artwork to the padding area." (HIG)
- "Don't assume fixed ratios. Resize to fit each pose, favor changing aspect ratio over letterboxing, and add artwork to unavoidable padding"; "Apple recommends changing aspect ratio over letterboxing, especially for games." (Forums 847644)
- Split View and PiP "mean apps may run at varying aspect ratios, so they should be freely resizable". (TT 111466)
- TN3192's asset-swap hook: compare `coordinateSpace.bounds.size` in `windowScene(_:didUpdateEffectiveGeometry:)` and update assets (its example calls `gameAssetManager.updateAssets(sceneSize:)`) when `!geometry.isInteractivelyResizing`. (TN3192)

## 10. Testing checklist

- "Confirm your views resize well in each supported orientation and pose. / Inspect how the system presents your app's navigation bars, toolbars, and tab bars vertically on the side of the display. / Identify any views, sheets, or popovers that position awkwardly when you fold or open iPhone Duo. / Identify elements or controls in your views that appear in the fold, and are difficult to see or interact with." (Preparing)
- "Check how your app appears on both displays, when closed, open, or partially folded. Rotate iPhone Duo in each pose to see how your app's layout reacts." (Preparing)
- "To close the iPhone Duo, click the Closed button on the right of the Rotate Right button. / To partially open the iPhone Duo, click the Partially Open button in the middle of the three device pose buttons. / To fully open the iPhone Duo, click the Open button on the far right. — To fold the device to any angle, hold the Option key while dragging the slider that appears below the bezel." (Device Hub)
- Test Split View by dragging "the app by the home indicator to either side of the screen, and check vertically laid-out content on both sides". (TT 111461)
- "Device Hub's Resizable iPhone / iPhone Mirroring behavior is an approximation, but iPhone Duo-specific behaviors need dedicated testing." (Forums 847644)
- "Test Dynamic Type, contrast, VoiceOver, and resizing across poses using Xcode and Device Hub"; "Custom hinge-spanning layouts may need explicit containers or sort priorities"; "don't hold text at the largest standard size. Let it reflow". (Forums 847644)

## 11. Statements about what Apple has not published

- "There's no single pose API. Infer pose from hinge status, angle, orientation, and size class together." (Forums 847644)
- Hinge "Update rate and precision are system policy, so don't depend on specific values." (Forums 847644) No angle thresholds for tent, laptop or book appear in any Apple source.
- Apple's spec page gives pixel resolutions only: inner "1878‑by‑2670-pixel resolution at 430 ppi", outer "1398‑by‑2034-pixel resolution at 460 ppi". (Specs) No Apple page states point dimensions, scale factor, margin values or fold width in points.
- No `simctl` or `XCUIDevice` API changes the pose; the forum request has no Apple reply (Forums 847883).
- No Apple sample project exists; the only runnable Apple artifact is the App Resizability skill in Xcode 27.1 (Three steps; TT 111461).
