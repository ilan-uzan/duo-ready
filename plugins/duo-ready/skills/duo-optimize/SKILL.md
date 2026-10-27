---
name: duo-optimize
description: >-
  Make an iOS app actually work on iPhone Duo (iOS 27.1), end to end, then
  prove it by running the app in the Duo simulator and looking at screenshots.
  Use this whenever someone says "optimize my app for iPhone Duo", "make my app
  Duo ready", "make it work on the foldable iPhone", "fix my app for the new
  iPhone", "run the Duo skills on my project", "just do it", or hands over a
  project and wants changes made, not advice. Scans the code, fixes what the
  scanner finds on a git branch, rebuilds with Xcode 27.1, boots the iPhone Duo
  simulator, captures both displays, reads the screenshots against Apple's
  checklist, fixes what it sees, and repeats. Drives duo-audit, duo-layout,
  duo-bars, duo-scenes, duo-camera and duo-test. Never claims certification,
  because Apple publishes no pass/fail test.
---

# duo-optimize

The goal: leave the user's project in a state where it builds against the iOS
27.1 SDK, launches on the iPhone Duo simulator, and looks right on both
displays when the agent looks at it. The other duo-ready skills explain; this
one edits, runs and checks. App Store screenshots and uploads are out of
scope.

It does not certify anything. Apple documents no compliance check, only a
checklist and testing in Device Hub ([Three steps](https://developer.apple.com/iphone-duo/prepare/)),
and says its own App Resizability skill "finds most issues, but not all of
them". A clean scan plus clean screenshots is evidence, not proof: Apple's
forum guidance warns that "Interactions that look fine in the simulator may
feel awkward on hardware" ([Apple Developer Forums 847644](https://developer.apple.com/forums/thread/847644)).

## Phase 0: prerequisites

1. Get the project root (the folder with the `.xcodeproj`, `.xcworkspace` or
   `Package.swift`; for React Native, Expo, Flutter, Capacitor or Unity also
   the folder with `package.json`, `pubspec.yaml`, `capacitor.config.*` or
   `ProjectSettings/`). For cross-platform apps read `duo-crossplatform` first
   and fix the native shell.
2. Check the toolchain and report what the commands say: `xcodebuild -version`
   (Apple: Xcode 27.1, build 27A9275, needs macOS Tahoe 26.6 or later) and
   `xcrun simctl list devicetypes | grep -i duo`. Without Xcode 27.1 the app
   cannot reach the full-display tier, because the SDK you link against decides
   it, not the deployment target. In that case do Phases 1 to 3 (code fixes
   only), skip Phases 4 and 5, and list them as "Not verified". Tell the user
   what to install; do not install Xcode yourself.
3. `git status` must be clean (otherwise ask). Work on a branch named
   `duo-optimize`. Commit by fix class, or by file when one file holds several
   classes, with the rule ids in the message.
4. Ask nothing else if the path is clear; start.

## Phase 1: baseline

1. `python3 -I <duo-audit>/scripts/duo_audit.py <root> --format json`
   (`<duo-audit>` is the sibling duo-audit skill folder). Keep the output and
   `summary.by_severity`.
2. Build once before editing, if Xcode 27.1 is present, so old build errors
   are not blamed on your edits.
3. Find the app's key screens by reading the code (root navigation, tabs, the
   main list and detail, forms, sheets, settings). Write the list down; the
   visual loop walks it.

## Phase 2: fix the code

Group findings by `rule_id` and route each class to the skill that owns it:
layout and size classes to `duo-layout`; bars, toolbars and tabs to
`duo-bars`; scene lifecycle, fold, hinge and state to `duo-scenes`; camera to
`duo-camera`. Read that skill and its references before editing and use its
replacement. Fix P0, then P1, then P2. Rules for every edit:

- Smallest change that removes the cause. No refactors or style changes.
- A regular-width recomposition (for example an inspector beside the canvas)
  has no sample code in `duo-layout`; compose it from the size-class guidance,
  keep the compact layout identical, and check a compact-width iPhone simulator
  afterwards. Panels whose content is wider than their slot can spill under the
  vertical bar; fix the content to fit rather than clipping the panel.
- If the deployment target is below 27.1, put iOS 27.1 APIs behind
  `if #available(iOS 27.1, *)` and keep the older behaviour working.
- Use only API names those skills document. Some are documented by name only
  (for example `backgroundExtensionEffect()`); do not write code from a name
  alone, leave that finding and say why. Apple publishes no pose API, no Duo
  idiom, no Duo Info.plist key and no point dimensions.
- Do not branch on device model, idiom or orientation, and do not hard-code
  point sizes from blogs (third-party, unverified).
- A finding in a stub (a bare `package.json` with no native shell) is not
  applicable; report it. `heuristic: true` findings need the surrounding code
  read first; some are false positives.

## Phase 3: static verification

Re-run the scanner and compare with the baseline. Every P0 is fixed or
explained. The scanner matches lines, so it can keep firing on code that
already follows the documented fix; report those as "scanner still matches,
fix applied" and never edit the scanner or add `--ignore` to lower the count.

## Phase 4: build and run on the Duo simulator

1. `xcodebuild -list` for the scheme, then build for an iOS Simulator
   destination using the Duo simulator's id from `xcrun simctl list devices`
   (the destination name is unconfirmed by Apple). Fix build errors your edits
   caused; report the rest.
2. Confirm the SDK stamp: `otool -l <App.app/App> | grep -A4 LC_BUILD_VERSION`
   must show `sdk 27.1` (third-party check; only that SDK gives the full inner
   display with vertical bars).
3. Boot the simulator (Apple's release note 187708500 says a first launch "can
   take several minutes"; on one Xcode 27.1 test machine it did not, so check
   `xcrun simctl list devices` rather than waiting blindly), then
   `xcrun simctl install <udid> <App.app>` and
   `xcrun simctl launch <udid> <bundle-id>`. `bootstatus` may print "Data
   Migration Failed" on every boot while the device stays usable (observed on
   Xcode 27.1; not documented by Apple). Keep the device booted for the whole
   run: opening and quitting Device Hub mid-run shut it down in that test
   ("Unable to lookup in current state: Shutdown"), so re-check it is Booted
   before every capture.
   To reach other screens, in this order: `xcrun simctl openurl` if the app has
   a URL scheme; DEBUG launch arguments or UI-test hooks you find by grepping
   the code (`grep -rn "CommandLine.arguments\|launchArguments" --include='*.swift' .`,
   quote the glob under zsh), passing them with `xcrun simctl launch <udid>
   <bundle-id> <args>`; or driving the simulator window if you have desktop
   control. If none works, say which screens were unreachable.
4. Folding: Apple documents no script or API for the pose. Use Device Hub's
   Closed, Partially Open and Open buttons and the Rotate button (Apple:
   [Interacting with your app in Device Hub](https://developer.apple.com/documentation/xcode/interacting-with-your-app-in-device-hub)).
   If you have desktop control, click them yourself. If you do not,
   test the pose the simulator is in and list the other poses as "Not
   verified"; do not wait for the user in an unattended run, and say in the
   report that a human can set the pose and rerun Phase 5.

   The pose can silently revert. On the test machine the device went from Open
   back to closed during a long agent run while the simulator stayed Booted, and
   nothing reported it (the cause was not identified; in another run a plain
   install and launch left the pose Open). Read the pose from the captures: `--display=primary-1`
   returning 2853x2007 with content means open (landscape); 2007x2853 and black
   means closed; `--display=primary` swaps the other way (the display names follow
   the active display, observed on one machine). `simctl io enumerate` printed no
   pixel sizes there. So check the pixel size of the first capture in every round,
   and if the pose is not the one you need, stop capturing, report which captures
   are invalid, and ask for the pose to be restored (or list those screens as
   "Not verified" in an unattended run). Never label a capture "inner" or "outer"
   from the file name; label it from its pixel size and content.

## Phase 5: look at it

For each key screen, in each state you can reach (outer display closed, inner
display open, rotated if the app supports it, and after a pose change):

1. Capture with `scripts/duo_screenshots.sh --out <dir>` from `duo-test`, or
   `xcrun simctl io <udid> screenshot --display=<id>` after reading
   `xcrun simctl io <udid> enumerate` (the display ids conflict between
   third-party reports, so trust the printed list and the pixel sizes). Ignore
   the App Store file names. If the image is black or empty, wait and retake:
   Apple lists black screenshots for a few minutes after boot (187146039). The
   script checks only pixel size and can exit 0 on a black capture, so open every
   image, and treat identical file sizes across different screens as a blank
   capture. A display you only ever saw black is "Not verified", never a pass.
   On the test machine the inner display stayed black while the device was in
   its default pose; opening the device in Device Hub first is Apple's documented
   way to make the inner display active.
2. Downscale large PNGs for viewing, for example
   `sips -Z 1400 in.png --out view.png`, then open the image and actually look
   at it. Do not infer from file size or from the code.
3. Judge it against Apple's own list ([Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)):
   - views resize well for the display and pose; the inner display fills the
     screen, not a centered column with empty space (that means an older SDK
     tier);
   - navigation bars, toolbars and tab bars appear vertically on the side where
     the system owns them (custom bars do not move);
   - nothing sits in the fold or under the camera cutouts;
   - sheets and popovers are not positioned awkwardly after folding or opening;
   - no clipping, overlap, stretched or oddly cropped media, truncated text,
     or empty space the layout could use.
   Compare with the Phase 1 capture so you can say what changed.
4. If something is wrong, find the cause in the code, route it to the owning
   skill, fix, rebuild, recapture. Give each screen at most three rounds; after
   that report it with the screenshot path and your best diagnosis.
5. After any change to bars, safe areas or shared layout code, recapture the
   screens you did not touch too. In the Kesef test, moving controls into the
   system navigation bar covered part of an untouched welcome screen, and only a
   recapture showed it.

The scanner does not flag title-only toolbar buttons, which `duo-bars` names
as the most common defect: grep the code for `Button("` or `Text(` inside
`.toolbar`/`ToolbarItem` and `UIBarButtonItem(title:` yourself and give each an
SF Symbol with its title, per `duo-bars`.

Never describe a screenshot you did not open, and never report a screen as
checked if it was only built.

## Final report

Keep it short:

- **Fixed**: rule ids, files, commits, scan counts before and after.
- **Seen and verified**: screens and states checked on which display, with the
  screenshot paths.
- **Not fixed and why**: false positives, findings declined by design (say so
  in those words, with the reason), third-party libraries, no documented API.
  Scanner findings that code cannot clear (for example a project-upgrade marker
  when the binary is already stamped sdk 27.1) go here, not in "Fixed".
- **Not verified**: poses or screens not reached, anything not built or run, a
  missing Xcode 27.1, and that the sample code was not compile-checked unless
  the build in Phase 4 succeeded.
- **Still needs a human**: a pass on a physical iPhone Duo (cameras, haptics,
  reachability and performance are not testable in the simulator) and review
  of the diff.

## Refuse these shortcuts

- Saying "your app is optimized for iPhone Duo" or "certified". Say what was
  checked and how.
- Declaring success because the scanner is quiet or the build passed.
- Pushing, opening a pull request, or changing signing, bundle ids, version
  numbers or App Store Connect settings.
