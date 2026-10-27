---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We're a two-person team shipping a UIKit field-service app (work orders, photo capture, signatures). I just moved the project to Xcode 27.1 on my Mac and it builds. The plan is to submit 4.0 to App Store Connect on Friday as our first build that "supports the new folding iPhone" so sales can mention it.

Project is at ./FieldOps. Relevant bits I know of:
- `FieldOps/AppDelegate.swift` creates the window in `didFinishLaunching` with `UIWindow(frame: UIScreen.main.bounds)`; there's no SceneDelegate.
- `FieldOps/Info.plist` has `UIRequiresFullScreen = YES` and `UISupportedInterfaceOrientations` portrait only. I don't think we have a launch storyboard, we removed it years ago to speed up launch.
- Screenshots are from an iPhone 15 Pro, taken in 2024.
- We have a Mac Catalyst target too, used by two customers.

Can you walk me through a release checklist for Friday? Tell me what will actually block the submission vs what's nice to have, and whether I should even ship with the 27.1 SDK or stay on the 27.0 SDK for this release. Also what do I need to do about screenshots for the April deadline I keep reading about?
