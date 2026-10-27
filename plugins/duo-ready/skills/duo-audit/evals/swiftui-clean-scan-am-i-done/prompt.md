---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Quick sanity check before I submit. My app is pure SwiftUI: a TabView with four tabs, each tab is a NavigationStack with .toolbar items, a List-based home screen, a player screen that shows video on top and an "Up next" list underneath, and a camera screen for recording short clips. No UIKit, no UIScreen.main anywhere, I already use @Environment(\.horizontalSizeClass) for the two-column layout and I rebuilt with Xcode 27.1 yesterday. It launched fine in the iPhone Duo simulator and I did not see anything obviously broken when I opened and closed it a couple of times.

I pulled the relevant screens into a small sample project so you can look at them: plugins/duo-ready/skills/duo-audit/scripts/fixtures/GoodApp in this repo.

So... am I done? Anything else I need to do before I upload the build and the new screenshots, or can I ship?
