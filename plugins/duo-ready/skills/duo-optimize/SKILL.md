---
name: duo-optimize
description: >-
  Do the whole job of getting an iOS app ready for iPhone Duo (iOS 27.1): scan
  the project, fix what the scanner finds, rebuild, re-scan, capture simulator
  screenshots, and report exactly what is done and what still needs a human.
  Use it when someone says "optimize my app for iPhone Duo", "make my app work
  on the foldable iPhone", "fix everything for Duo", "run the Duo skills on my
  project", "just do it", or hands over a project path and wants changes made
  rather than advice. It drives the other duo-ready skills (duo-audit,
  duo-layout, duo-bars, duo-scenes, duo-camera, duo-test, duo-ship) and never
  claims the app is certified, because Apple publishes no pass/fail test.
---

# duo-optimize

The other skills explain. This one acts: it edits the project, verifies each
step with a command, and ends with an honest report. It does not certify
anything, because Apple documents no compliance check, only a checklist and
testing in Device Hub (Apple: [Three steps](https://developer.apple.com/iphone-duo/prepare/)).
Apple also says its own App Resizability skill "finds most issues, but not
all of them", so a clean scan is evidence, not proof.

## Before touching anything

1. Get the project root (the folder with the `.xcodeproj`, `.xcworkspace` or
   `Package.swift`; for React Native, Expo, Flutter, Capacitor or Unity also
   the folder with `package.json`, `pubspec.yaml`, `capacitor.config.*` or
   `ProjectSettings/`). Cross-platform projects: read `duo-crossplatform` first
   and fix the native shell, not the JS layer, unless that skill says otherwise.
2. Check the toolchain and report what it says, do not assume:
   `xcodebuild -version` (Apple: Xcode 27.1, build 27A9275, needs macOS Tahoe
   26.6 or later) and `xcrun simctl list devicetypes | grep -i duo`. Without
   Xcode 27.1 the app cannot get the full-display tier (the SDK you link
   against decides it, not the deployment target), so edits are still useful
   but nothing can be built or run. Do steps 1 to 4, skip steps 5 and 6, and
   list them under "Not verified" in the report.
3. Make the changes safe to undo: `git status` must be clean (otherwise ask),
   then work on a branch named `duo-optimize`. One commit per fix class so the
   user can drop any of them. When one file holds several classes, commit by
   file and list every rule id it covers in the message.

## The loop

1. **Baseline.** Run `python3 -I <duo-audit>/scripts/duo_audit.py <root> --format json`
   (`<duo-audit>` is the sibling `duo-audit` skill folder). Save the output.
   Record `summary.by_severity`. Build once with Xcode 27.1 before editing, if
   it is installed, so you can tell new build errors from old ones.
2. **Plan.** Group findings by `rule_id` and route each class to the skill that
   owns the fix: layout and size classes to `duo-layout`; bars, toolbars and
   tabs to `duo-bars`; scene lifecycle, fold, hinge and state to `duo-scenes`;
   camera to `duo-camera`. Read that skill's SKILL.md and its references before
   editing, and use its replacement, not a guess. If a finding sits in a stub
   (a bare `package.json`, `pubspec.yaml` or similar with no native shell to
   change), do not invent one: report it as not applicable. Findings flagged
   `heuristic: true` need reading the surrounding code first; some are false
   positives and should be left alone and reported.
3. **Fix in severity order, P0 then P1 then P2.** Rules for every edit:
   - Make the smallest change that removes the cause. No refactors, renames or
     style changes outside the finding.
   - If the deployment target is below 27.1, put iOS 27.1 APIs behind
     `if #available(iOS 27.1, *)` (and keep older behaviour working).
   - Some documented fixes are API names without usage detail (for example
     `backgroundExtensionEffect()`). Do not write code from a name alone: leave
     that finding and say why.
   - Use only API names that appear in `duo-layout`, `duo-bars`, `duo-scenes`
     or `duo-camera`. If a fix needs an API those skills do not document, stop
     and report it; do not invent one. Apple publishes no pose API, no Duo
     idiom, no Duo Info.plist key and no point dimensions.
   - Do not branch on device model, idiom or orientation, and do not hard-code
     point sizes from blogs (third-party, unverified).
   - Commit after each class with the rule ids in the message.
4. **Re-scan.** Run the scanner again and compare with the baseline. Every P0
   must be fixed or explained. The scanner matches lines, so it can keep
   firing on code that already follows the documented fix (a size-class
   ternary, for example); report those as "scanner still matches, fix applied"
   rather than changing the scanner or adding `--ignore` to make the number
   go down.
5. **Build and test** (needs Xcode 27.1). `xcodebuild -list` for the scheme,
   then `xcodebuild build` for an iOS Simulator destination (confirm the Duo
   destination name with `xcrun simctl list devicetypes | grep -i duo`, it is
   unconfirmed by Apple), then the project's own unit tests. On a build error,
   fix it if it came from your edit; otherwise report it. Confirm the build
   stamp: `otool -l <App.app/App> | grep -A4 LC_BUILD_VERSION` must show
   `sdk 27.1` (a third-party check; only that SDK gives the full inner display).
6. **Capture.** If the simulator runs, use `duo-test`'s
   `scripts/duo_screenshots.sh` and look at both displays yourself. Apple lists
   known simulator issues (black screenshots for a while after launch, slow first
   boot), so retake before concluding anything is wrong.
7. **Report**, in this shape, and nothing longer:
   - **Fixed** (rule ids, files, commits), with the before and after scan counts.
   - **Not fixed and why** (heuristic false positives, needs a design
     decision, third-party library, no documented API).
   - **Still needs a human**: test both displays in Device Hub across poses and
     orientations on a real project run; test on a physical iPhone Duo; add Duo
     screenshots for App Store Connect (`duo-ship`; Apple says they are needed
     from April 2027 and its two pages disagree on which apps that covers);
     review the diff.
   - **Not verified**: anything that was not built or run, and that the sample
     code was not compile-checked unless the build in step 5 actually succeeded.

## Refuse these shortcuts

- Saying "your app is optimized for iPhone Duo" or "Made for iPhone Duo". The
  badge comes from uploading Duo screenshots, not from code.
- Declaring success because the scanner is quiet; read the P0 and P1 diffs.
- Pushing, opening a pull request, or changing signing, bundle ids, version
  numbers or App Store Connect settings. Leave those to the user.
