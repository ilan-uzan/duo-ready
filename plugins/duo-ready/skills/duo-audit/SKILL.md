---
name: duo-audit
description: >-
  Entry point for "is my app ready for iPhone Duo?". Runs the bundled scanner
  (scripts/duo_audit.py, 27 rules built from Apple's own grep list), explains
  which SDK tier the build is on, triages findings P0 -> P1 -> P2, separates
  heuristic hits from cited ones, and hands each finding class to the right
  duo-ready skill. Use it whenever someone asks to audit, check, scan, review
  or "prepare" an iOS project for the foldable iPhone, says "the new iPhone",
  "the folding one", "iOS 27.1", "my app looks letterboxed / centered with
  black bars on the new phone", "layout breaks when the phone opens", "the
  toolbar moved to the side", "App Store wants new screenshots", or asks
  "am I done?" after recompiling. Also use it before any other duo-ready skill
  when a project path is available, so advice starts from the real code.
---

# duo-audit

Scan first, read the code second, advise third. This skill wraps a
deterministic scanner and tells you how to interpret what it prints. It does
not certify anything.

## What Apple actually says

- Build with Xcode 27.1 (iOS 27.1 SDK). What the app gets on the inner display
  "depends on which SDK the binary links against, not its deployment target":
  iOS 26 SDK or earlier runs centered with empty space; iOS 27 SDK fills most
  of the inner display but avoids the status bar; iOS 27.1 SDK or later uses
  the full display with toolbars and tab bars moving vertically
  ([Three steps](https://developer.apple.com/iphone-duo/prepare/);
  [Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
- Apple's own checklist is three steps: run the App Resizability skill in
  Xcode 27.1 ("get my app ready for iPhone Duo", or `xcrun agent skills export`
  for other agents), fix a grep list of patterns (`UIScreen.main`, orientation,
  idiom, hard-coded sizes, fill media), then test in the Resizable simulator,
  iPhone Mirroring and the iPhone Duo simulator. Apple says the skill "finds
  most issues, but not all of them" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Layout comes from size classes and scene geometry, never from device, idiom
  or orientation: "an iPhone app can have any combination of size classes",
  and the inner display "doesn't honor supported interface orientations"
  ([Three steps](https://developer.apple.com/iphone-duo/prepare/);
  Tech Talk 111461, [Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/)).
- Bars go vertical only when the system owns them: "Content from custom
  `UIToolbar`, `UINavigationBar`, or `UITabBar` instances isn't considered"
  (Tech Talk 111462, [Raise the bar with iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111462/)).
- Safe areas "are often asymmetric on iPhone Duo. Handle each side
  independently" (Tech Talk 111461).

## Workflow

### 1. Locate the project and run the scanner

Ask for the project path if none was given. Scan the directory that holds the
`.xcodeproj`/`.xcworkspace` or `Package.swift` (and, for cross-platform apps,
the directory holding `package.json`, `pubspec.yaml`, `capacitor.config.*` or
`ProjectSettings/`), so the project-level rules see the Info.plist and
pbxproj. The script lives next to this file at `scripts/duo_audit.py`; from the
repo root that is `plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py`.

```
python3 -I <skill-dir>/scripts/duo_audit.py <project-root> --format markdown
python3 -I <skill-dir>/scripts/duo_audit.py <project-root> --format json     # when triaging programmatically
python3 -I <skill-dir>/scripts/duo_audit.py --list-rules                      # the 27 rules with sources
```

Flags: `--min-severity P0|P1|P2` hides less severe findings (the JSON summary
reports how many under `hidden_by_min_severity`), `--ignore GLOB` skips paths
or basenames (repeatable), `--no-color` for the text format. Python 3.9+
standard library only; no install step. Test directories (`*Tests`,
`*UITests`), `*Tests.swift`/`*Spec.swift`, `Pods`, `node_modules`,
`DerivedData`, `.build` and `*.xcassets` are skipped; commented-out code and
`#if DEBUG` / `targetEnvironment(simulator)` blocks are not reported.

Exit codes: `0` = no P0 findings, `1` = at least one P0 finding, `2` = usage
error (no path, or not a directory). `--min-severity` changes what is shown
and therefore the exit code, so run it without the flag in CI.

Inline suppression, for confirmed false positives only: append
`// duo-audit: ignore` (all rules) or `// duo-audit: ignore DUO-003`
(one or more ids, comma or space separated) to the offending line, or put the
comment on its own line immediately above it. Objective-C files use the same
comment text. Tell the user to add a reason next to it.

The markdown report has four parts: a summary line (files scanned, counts per
severity), the findings grouped P0/P1/P2 as checkboxes with snippet, Why, Fix
and Source, an "Already adopted" list, and Apple's three steps as "Next
steps". The JSON has `summary`, `findings[]` (with `rule_id`, `severity`,
`file`, `line`, `snippet`, `why`, `fix`, `source`, `heuristic`) and
`adopted[]`.

### 2. State the SDK tier before discussing any finding

The tier decides whether the user is looking at a letterbox problem or a
layout problem, so settle it first:

- Ask which Xcode produced the build. Apple's tiers, from the Three steps
  page: iOS 26 SDK or earlier runs "centered on the inner display with empty
  space around it"; iOS 27 SDK "fills most of the inner display but still
  avoids the status bar"; iOS 27.1 SDK or later "uses the full display, and
  toolbars and tab bars move vertically below the status bar"
  ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- The tier follows the SDK the binary links against, not the deployment
  target, and there is no Info.plist key to request the older mode (third-party
  summary of Apple's UIKit Q&A, Q23). Xcode 27.1 final is build 27A9275
  ([Xcode 27.1 release](https://developer.apple.com/news/releases?id=10152026a)),
  requires macOS Tahoe 26.6 or later ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes)).
  Xcode 27.2 beta did not include Duo support despite the higher number
  (third-party, unverified).
- Rule DUO-019 (`LastUpgradeCheck < 2710`) is a heuristic proxy for the
  Xcode version that last touched the project, not proof of the build SDK. To
  check a built binary, a third-party tip (unverified) is
  `otool -l <binary> | grep -A4 LC_BUILD_VERSION`, which should read
  `sdk 27.1`; one developer's `swiftc -sdk` build was stamped 27.0 by mistake.
- If the app is on the iOS 27.1 tier, the question becomes "does the content
  adapt to the vertical bars?", which is Apple's own caveat for that tier.

Details and verbatim text: `references/sdk-tiers-and-three-steps.md`.

### 3. Triage P0, then P1, then P2, using Apple's Step 2 list as the frame

Work through the report in the order the scanner prints it; it is already
sorted by severity, then rule id, then file. For each finding:

- Open the file at the reported line and read the surrounding function before
  you comment. The snippet is one line of context.
- Separate the two kinds of rule. Rules tagged `[heuristic]` (text) or
  `_(heuristic)_` (markdown), `"heuristic": true` in JSON, are
  pattern-matching approximations: DUO-011, 012, 013, 014, 016, 017, 018, 019,
  023. The Apple guidance they cite is real; the detection may not apply to
  this line (a `height > 600` check inside a chart renderer, a `16/9` that
  really is a video's intrinsic ratio, a `struct ToolbarTitle: View` that is
  not a bar). Confirm by reading, and either fix or suppress with a reason.
  DUO-023 says in its own source field that no Apple statement covers the
  exact pattern. The other 18 rules are cited directly to Apple text; still
  read the code, because the fix depends on what the value is used for.
- Map each finding to Apple's Step 2 row it violates (screen bounds, scale,
  window creation, stored `UIScreen`, orientation, idiom, regular-width-means-
  iPad, device-size checks, fill media). That tells the user which Apple
  sentence they are fixing and keeps the advice to what Apple said.
- Group by file, not by rule, when writing the fix list: one view controller
  with five findings is one refactor.
- P0 is "the app is wrong or will not ship" (lifecycle, launch screen,
  `UIScreen.main`, idiom, orientation, hard-coded dimensions, symmetric
  safe-area math). P1 is "visibly broken on one of the displays". P2 is
  "degraded or needs a manual check". These priorities are the repo's, built
  from Apple's statements and the field reports; they are not Apple's.

Per-rule fixes with the exact Apple replacement and the skill to open:
`references/triage-playbook.md`. The full rule table: `references/rules.md`.

### 4. Hand off each finding class

| Finding class | Rules | Open |
|---|---|---|
| Screen/scale/window geometry, idiom, orientation, device sniffing, hard-coded sizes, safe areas, fill media, aspect ratio | DUO-001, 002, 004, 005, 006, 007, 011, 012, 013, 014, 015, 016, 022, 023 | `duo-layout` |
| Hand-built bars, hidden navigation bar, text-only items, sheets | DUO-017, 018 (and DUO-016 when the hidden status bar was meant to free the side column) | `duo-bars` |
| Scene lifecycle, window creation, `UIRequiresFullScreen`, discrete resize, multi-window | DUO-003, 008, 009 | `duo-scenes` |
| Launch screen, SDK tier, screenshots, badge, release checklist | DUO-010, 019 | `duo-ship` |
| Front camera, capture accessory, mirroring, rotation | no rule; see below | `duo-camera` |
| React Native, Flutter, Capacitor/Ionic, Unity, WKWebView | DUO-021, 030, 031, 032, 033 | `duo-crossplatform` (web and WKWebView host geometry also in `duo-backend`) |
| iOS 27.1-only API in a Mac Catalyst target | DUO-020 | the skill that owns the API; the guard is `#if !targetEnvironment(macCatalyst)` ([Xcode 27.1 Release Notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes), 185924957) |

The scanner has no camera rule. If the project contains `AVCaptureSession`,
`AVCaptureDevice` or a selfie/video-call feature, send the user to
`duo-camera` even when the scan is clean: "a front camera is not always
looking at you" and `AVCaptureDevice.position` is insufficient
([Choosing a camera by the direction it faces](https://developer.apple.com/documentation/avkit/choosing-a-camera-by-the-direction-it-faces)).

### 5. Remind the user of Apple's three steps

Repeat them in this order and say why each matters, because the scanner only
approximates Step 2:

1. Step 1, run Apple's App Resizability skill in Xcode 27.1 (ask the coding
   assistant to "get my app ready for iPhone Duo"; other agents run
   `xcrun agent skills export`). It was introduced at WWDC26 as "Modernize your
   UIKit app" and renamed App Resizability in 27.1, covering SwiftUI and
   iPhone Duo (Tech Talk 111461). Apple: "The skill finds most issues, but not
   all of them." Run it as well as this scanner; they overlap but neither is
   complete.
2. Step 2, fix the common patterns. The scanner's rule table is that list plus
   lifecycle, bars, safe areas and cross-platform checks.
3. Step 3, test resizing: the iOS Resizable simulator in Device Hub, iPhone
   Mirroring on macOS 27 "resized to extreme sizes in both directions", and the
   iPhone Duo simulator in Xcode 27.1, "the best way to test the full native
   experience" ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).

### 6. Point to verification and shipping

- `duo-test` for the manual pass: Device Hub's Closed / Partially Open / Open
  buttons and the Option-drag hinge slider
  ([Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)),
  Split View, sheets, keyboard, and what cannot be automated (there is no
  `simctl` fold command; the forum request has no Apple reply).
- `duo-ship` for App Store Connect: Duo screenshots are optional now, earn
  the "Made for iPhone Duo" badge, and become required from April 2027; Apple's
  two pages differ on scope (news post: "any apps or games submitted";
  specifications page: "any app using the iOS 27.1 SDK or later"), so plan for
  the broader reading ([Developer News, Oct 5 2026](https://developer.apple.com/news/?id=kkphp5qo);
  [Screenshot specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
  A launch screen is required for iOS 27 SDK submissions
  ([TN3192](https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key)).

## Why a clean scan is not a pass

Say this explicitly whenever the report shows zero findings, and never phrase
the result as "ready" or "certified":

- Apple's Step 2 is itself a grep list. The scanner regex-matches Swift,
  Objective-C, Info.plist, pbxproj and framework config files. It cannot see
  what a view looks like, how a grid lands on the fold, or whether a toolbar
  item has an icon.
- Apple's own tool carries the same caveat: "The skill finds most issues, but
  not all of them."
- Field reports collected in the research: SwiftUI apps built on `TabView` and
  `NavigationStack` needed near-zero Duo code and still shipped visible
  defects. A sheet whose only item was a text "Done" button "reserved the side
  rail and left it empty" (third-party report); a six-column grid centered on
  the content area put a column across the fold (third-party report). Neither
  is detectable by text search, and both violate Apple rules: "If your item
  has a title and doesn't have an icon, the system doesn't present it
  vertically" ([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo));
  "In a grid-style layout, prefer an even number of columns so content divides
  cleanly" ([HIG, Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)).
- The "Already adopted" section is positive keyword detection
  (`horizontalSizeClass`, `ArrangementView`, `reservedRegions(`, ...). It
  means the symbol appears, not that it is used correctly, and not that the
  API is available on the build SDK.

After a clean scan, hand the user Apple's audit checklist from the Technology
Overview and ask them to run it in the Duo simulator: "Confirm your views
resize well in each supported orientation and pose. / Inspect how the system
presents your app's navigation bars, toolbars, and tab bars vertically on the
side of the display. / Identify any views, sheets, or popovers that position
awkwardly when you fold or open iPhone Duo. / Identify elements or controls in
your views that appear in the fold, and are difficult to see or interact with"
([Preparing your app](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)).
Then open `duo-test`.

## Common mistakes

- Treating exit code 0 as "ready". It means no P0 pattern matched. (Repo
  guidance.)
- Deciding the fix from the snippet without opening the file. Half the
  heuristic rules need context; the user loses trust after one false "fix".
- Reporting a heuristic hit in the same voice as a cited one. Always carry the
  tag through to the user.
- Confusing deployment target with build SDK. An app targeting iOS 16 built
  with Xcode 27.1 is on the 27.1 tier; an app targeting iOS 27 built with
  Xcode 27.0 is not ([Three steps](https://developer.apple.com/iphone-duo/prepare/)).
- Suggesting a device check to "detect iPhone Duo". There is no Duo idiom and
  no Duo Info.plist key; Apple: "Design from size, traits, and reserved
  regions, not hardware names or screen dimensions" (third-party summary of
  Apple's UIKit Q&A; [Group Lab summary](https://developer.apple.com/forums/thread/847644)).
  CONTRIBUTING forbids it in every skill.
- Quoting point sizes as Apple's. Apple publishes pixels only (inner
  1878x2670 at 430 ppi, outer 1398x2034 at 460 ppi,
  [Tech Specs](https://www.apple.com/iphone-duo/specs/)); 466x678 pt and
  669x951 pt are third-party simulator measurements.
- Skipping the camera because the scan was clean. There is no camera rule.
- Running the scanner on a subfolder (for example `Sources/`) so the Info.plist
  and pbxproj rules (DUO-007 to DUO-010, DUO-019, DUO-020) never fire.

## When to read the references

- `references/rules.md`: the 27 rules with id, severity, kind, title, Apple
  source, and the verbatim why/fix text. Read it when a user asks "what does
  DUO-0xx mean" or wants the full list. Do not add rules there; rules live in
  the script's `RULES` table (see CONTRIBUTING.md).
- `references/sdk-tiers-and-three-steps.md`: Apple's tier text and three steps
  with URLs, the toolchain facts, and the third-party SDK-stamp tip. Read it
  when the user's build setup is unclear or they ask why the app is
  letterboxed.
- `references/triage-playbook.md`: for every rule class, what to look at in
  the code, the Apple-stated fix, and which skill to open. Read it while
  writing the fix list.

## Related skills

`duo-layout` (size classes, geometry, reserved regions, arrangement views,
grids), `duo-bars` (vertical bars, item rules, overflow, sheets, opt-out),
`duo-scenes` (fold as trait change, state, multi-window, scene accessories,
hinge), `duo-camera` (two front cameras, direction coordinator, mirroring),
`duo-test` (Device Hub, simulator, manual pass, CI), `duo-ship` (screenshots,
April 2027 rule, badge, launch screen, TN3192), `duo-design` (HIG rubric),
`duo-backend` (analytics, CDN sizing, web views, widgets), `duo-crossplatform`
(React Native, Flutter, Capacitor, Unity).
