---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I maintain a recipe app (SwiftUI, TabView + NavigationStack, deployment target iOS 17). We push every release with fastlane `deliver` from `fastlane/Fastfile` and the screenshots live in `fastlane/screenshots/en-US/` as `iPhone 17 Pro Max-01.png` etc. Our CI archives with Xcode 26.4 on a macOS 26.5 runner.

Yesterday App Store Connect started showing two extra screenshot slots for the foldable iPhone and marketing is asking if we need them for the 3.2 release next week. Three questions:

1. What exact pixel sizes do those slots want, and are they required right now? Someone mentioned they become mandatory next year.
2. Can I just add them to the fastlane `screenshots` folder with a new device name, and if so what name?
3. If we don't rebuild with the new Xcode, what does our app actually look like on that phone? Marketing wants the "optimized" badge.

Give me the straight answer with Apple sources, I don't want guesses.
