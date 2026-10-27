# Contributing to duo-ready

Thanks for helping iOS apps unfold properly. This file is also the house style every skill in this repo follows, so a reader can move between skills without relearning the format.

## What a duo-ready skill is

A skill is a folder under `plugins/duo-ready/skills/<name>/` that follows the open Agent Skills layout:

```
<name>/
├── SKILL.md          # required: frontmatter + instructions (under 500 lines)
├── references/       # Apple-grounded detail the model reads when it needs it
├── scripts/          # deterministic helpers (Python 3 stdlib only, or shell)
└── evals/            # test prompts and graders (claude plugin eval layout)
```

`SKILL.md` frontmatter has exactly two required keys:

```yaml
---
name: duo-layout
description: >-
  What it does, then when to use it. Be specific and a little pushy: list the
  phrases and situations that should trigger it, including ones where the user
  never says "iPhone Duo".
---
```

## Ground rules (why each one exists)

1. **Every rule cites Apple.** Each recommendation links to the Apple page or Tech Talk it came from, inline, like `[Preparing your app for iPhone Duo](https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo)` or `(Tech Talk 111463, "Strike a pose with adaptive layouts")`. Readers trust the repo because they can check it, and Claude gives better advice when it knows which guidance is Apple's and which is ours.
2. **Label the unverified.** Apple has not published everything (point sizes, hinge thresholds, some enum cases). Anything inferred from the simulator, a third party, or our own testing is marked `(inferred)` or `(third-party, unverified)`. Never upgrade a guess to a fact.
3. **Exact names, exact signatures.** API names are copied from Apple's documentation, never paraphrased or "cleaned up". Availability is stated (`iOS 27.1+`). A wrong symbol name costs a developer an hour.
4. **Explain the why, skip the shouting.** Prefer "do X because the inner display ignores supported orientations" over "ALWAYS do X". Models and humans both follow reasoning better than commands.
5. **Size classes, not devices.** No skill may suggest detecting iPhone Duo by model identifier, idiom, or orientation for layout decisions. That is Apple's central instruction and the most common bug.
6. **Code samples are complete and buildable.** SwiftUI and UIKit samples compile against the iOS 27.1 SDK. Include imports. Mark the Xcode version they were checked with. If you could not compile it, say so in a comment at the top of the sample.
7. **Short SKILL.md, deep references.** Keep `SKILL.md` to the workflow, the decision points, and pointers. Put long API tables, full samples, and Apple quotes in `references/` and say when to read each file.
8. **No marketing in skills.** Skills help developers ship. The README does the selling.

## Writing a sample

```swift
// Checked with Xcode 27.1 (27A9275), iOS 27.1 SDK.
import SwiftUI

struct Example: View { ... }
```

Prefer one focused sample per concept over one giant demo. Show the before (what breaks on Duo) and the after when the fix is non-obvious.

## Adding a rule to the audit

Rules live in the `RULES` table in `plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py`. A rule needs an id, severity, title, why, fix, and an Apple source. Add a line to the `fixtures/BadApp` project that triggers it and a test. Run:

```
python3 -I plugins/duo-ready/skills/duo-audit/scripts/test_duo_audit.py
```

## Keeping up with Apple

Apple updates these pages. When you notice a change, open an issue with the URL and the diff, or a PR that updates the reference and the `Last checked` date at the top of the affected file.

## Pull requests

Small and focused. Describe what you tested on (simulator pose, Xcode build, device if you have one). Be kind in review; everyone here is learning a new device at the same time.
