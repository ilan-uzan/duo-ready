<h1 align="center">duo-ready</h1>

<p align="center">
  Make your iOS app ready for iPhone Duo.<br>
  Eleven Claude Code skills and a code scanner, built only from what Apple has actually published.
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#the-skills">Skills</a> ·
  <a href="#why-you-can-trust-it">Why you can trust it</a> ·
  <a href="docs/known-gaps.md">What Apple has not said</a> ·
  <a href="docs/apple-sources.md">81 Apple sources</a>
</p>

---

iPhone Duo shipped on October 23, 2026. Apps built with the iOS 26 SDK run centered on the inner display with empty space around them. Apps built with the iOS 27.1 SDK fill it, and their toolbars and tab bars move to the side. Starting April 2027, App Store submissions need iPhone Duo screenshots. Apple's own guidance is spread across one Technology Overview, one HIG page, six Tech Talks, three Group Labs, a technote, release notes, and a dozen forum answers.

This repo turns that corpus into skills your coding agent can use, with every rule linked to the Apple sentence it came from.

## Start with the scanner

No install needed. It is one Python file with no dependencies.

```bash
git clone https://github.com/ilan-uzan/duo-ready
python3 duo-ready/plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py /path/to/YourApp
```

Output on the bundled fixture project (`scripts/fixtures/BadApp`), trimmed to the first finding:

```
```

```
iPhone Duo readiness audit
Path: ./BadApp
Files scanned: 15    Findings: 48 (P0: 14, P1: 19, P2: 15)

== P0 (14) ==
[P0] DUO-001 UIScreen.main used for layout — Sources/AppDelegate.swift:10
    > window = UIWindow(frame: UIScreen.main.bounds)
    Why:    Apple: UIScreen.main is "ambiguous on two-display devices and will be deprecated"; its bounds go stale when the device folds and the scene is resized mid-session.
    Fix:    Replace with view.bounds / window.bounds (SwiftUI: GeometryReader or onGeometryChange); re-read sizes in layoutSubviews, viewDidLayoutSubviews or viewWillTransition(to:with:); never store a UIScreen - reach it via view.window?.windowScene?.screen.
    Source: https://developer.apple.com/iphone-duo/prepare/ ; Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/
```

27 rules. Each one carries a severity, Apple's reasoning, a fix, and a source URL. Rules that are pattern-based heuristics say so in the output, so you know which hits to double-check. `--format markdown` pastes into a GitHub issue; `--format json` feeds CI. Exit code 1 means at least one P0.

The rules come from Apple's own "Step 2: Fix patterns" list on the [Three steps](https://developer.apple.com/iphone-duo/prepare/) page, plus TN3192, the Group Lab summary, and the Xcode 27.1 release notes. See [the rule table](plugins/duo-ready/skills/duo-audit/references/rules.md).

## Install

**Claude Code**

```
/plugin marketplace add ilan-uzan/duo-ready
/plugin install duo-ready@duo-ready
```

Then type `/duo-optimize` and say "optimize my app for iPhone Duo": the agent scans your code, fixes it, builds with Xcode 27.1, runs the iPhone Duo simulator and checks screenshots of both displays. Or type `/duo-audit` for a read-only report, or just describe the problem ("my toolbar went sideways on the new iPhone") and Claude picks the right skill.

**Any agent that reads SKILL.md** (Cursor, Codex, Copilot, Gemini CLI and others): copy the folders from [`plugins/duo-ready/skills/`](plugins/duo-ready/skills) into your agent's skills directory (`duo-optimize` reads its sibling skills and the `duo-audit` scanner, so copy them together). The skills follow the open [Agent Skills](https://agentskills.io/specification) layout.

## The skills

| Command | What it does | You leave with |
|---|---|---|
| [`/duo-optimize`](plugins/duo-ready/skills/duo-optimize/SKILL.md) | Does the whole job: scans, fixes the code on a git branch, builds with Xcode 27.1, runs the Duo simulator, opens screenshots of both displays, fixes what it sees, repeats | A branch of small commits, before and after scan counts, screenshot evidence, and an honest list of what was not verified |
| [`/duo-audit`](plugins/duo-ready/skills/duo-audit/SKILL.md) | Runs the scanner, works out which SDK tier your build is on, triages P0 to P2 | A fix list ordered by what Apple says breaks first, and the skill to open for each |
| [`/duo-layout`](plugins/duo-ready/skills/duo-layout/SKILL.md) | Size classes, scene geometry, reserved regions, `ArrangementView` / `UIArrangementViewController`, fold continuity | Layout code that uses the fold as a division region instead of guessing a pose |
| [`/duo-bars`](plugins/duo-ready/skills/duo-bars/SKILL.md) | Vertical navigation, tool and tab bars: who owns the bar, icon and title rules, order, overflow, opt-out | Bars that actually go vertical, with no empty rail |
| [`/duo-scenes`](plugins/duo-ready/skills/duo-scenes/SKILL.md) | The fold as a trait change, `UIRequiresFullScreen` under TN3192, Split View, multiple windows, scene accessories, hinge API | State that survives opening and closing the phone |
| [`/duo-camera`](plugins/duo-ready/skills/duo-camera/SKILL.md) | Two front cameras, `AVCaptureDeviceDirectionCoordinator`, mirroring, `CameraCaptureAccessory` | A camera that faces the person holding the phone |
| [`/duo-test`](plugins/duo-ready/skills/duo-test/SKILL.md) | Device Hub, the Duo simulator, per-display screenshots, what cannot be automated, a CI matrix | A manual pass and a screenshot script at App Store Connect sizes |
| [`/duo-ship`](plugins/duo-ready/skills/duo-ship/SKILL.md) | Screenshot and preview specs, the April 2027 rule, the badge, launch screen, release checklist | A submission that earns "Made for iPhone Duo" |
| [`/duo-design`](plugins/duo-ready/skills/duo-design/SKILL.md) | The HIG page as a 48-point review rubric, Apple's pose vocabulary, what not to do | A design review tied to Apple's sentences, not opinions |
| [`/duo-backend`](plugins/duo-ready/skills/duo-backend/SKILL.md) | Device detection limits, analytics properties, CDN sizing, server-driven UI, WKWebView, widgets | A backend that stops asking "is this a Duo" |
| [`/duo-crossplatform`](plugins/duo-ready/skills/duo-crossplatform/SKILL.md) | React Native, Flutter, Capacitor, Unity: known issues, fixes, bridges | The native fix first, and what each framework still lacks |

## Why you can trust it

**Every claim is labelled.** Facts from Apple's documentation, Tech Talks, release notes, Newsroom, or an Apple engineer on the Developer Forums are stated plainly with an inline link. Anything from a blog, a GitHub repo, or a simulator measurement is marked *third-party, unverified*. Anything we concluded ourselves is marked *inferred*. The labels are in the skills, not just the README.

**It says what Apple has not said.** Apple has not published point dimensions for either display, hinge angle thresholds, a pose API, a `simctl` fold command, or a sample project. [docs/known-gaps.md](docs/known-gaps.md) lists 22 such gaps, including two places where Apple's own pages disagree with each other. The skills tell your agent to say "Apple has not published this" rather than make something up.

**Sources are one click away.** [docs/apple-sources.md](docs/apple-sources.md) lists all 81 Apple URLs behind the repo, grouped and described. [docs/device-facts.md](docs/device-facts.md) has every number with its status. [docs/api-quick-reference.md](docs/api-quick-reference.md) has every symbol with its minimum OS.

**What we do not claim yet.** Code samples are composed from Apple-documented APIs and carry a header saying they have not been compile-checked against the iOS 27.1 SDK; Apple's own verbatim examples are marked as such. Nothing has been verified on a physical iPhone Duo. The scanner's 31 tests run in CI; the SwiftUI and UIKit samples do not yet. Pull requests that change either of those are the most useful ones you can send.

## Apple ships its own skill. Why this one?

Xcode 27.1 includes an "App Resizability" skill, and Apple makes running it Step 1 of its checklist. Apple also says it "finds most issues, but not all of them." It covers the Step 2 anti-patterns. duo-ready covers those too, and adds vertical bars, the hinge and scene APIs, the camera, testing, App Store screenshots and the April 2027 deadline, backend and web, cross-platform frameworks, and design review. [docs/beyond-apples-skill.md](docs/beyond-apples-skill.md) has the side-by-side.

## The facts Apple has published

| | Inner display | Outer display |
|---|---|---|
| Size | 7.6-inch | 5.4-inch |
| Pixels | 1878 × 2670 at 430 ppi | 1398 × 2034 at 460 ppi |
| App Store screenshot | 2007 × 2853 | 1398 × 2034 |
| Size classes | regular × regular | compact × regular (portrait), compact × compact (landscape) |

Points per display: not published by Apple. Pose API: none. Duo idiom: none, it stays `.phone`. Duo Info.plist key: none. Source links for every row are in [docs/device-facts.md](docs/device-facts.md).

## Contributing

Found an Apple page that changed, a symbol that does not compile, or a behavior that differs on hardware? Open an issue with the URL or a PR with the diff. [CONTRIBUTING.md](CONTRIBUTING.md) is short and is also the house style every skill follows.

## License

[MIT](LICENSE). Not affiliated with or endorsed by Apple. iPhone, iPhone Duo, Xcode, SwiftUI and related marks are trademarks of Apple Inc.
