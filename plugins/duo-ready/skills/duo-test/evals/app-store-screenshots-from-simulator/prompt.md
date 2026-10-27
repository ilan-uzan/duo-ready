---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I maintain a recipe app (SwiftUI, Xcode project at ./Recipes, scheme "Recipes"). Marketing wants the "Made for iPhone Duo" badge before the holidays, so I need App Store screenshots for both of the new iPhone's screens. I don't have the device. I installed Xcode 27.1 yesterday and the iPhone Duo simulator boots, but when I ran `xcrun simctl io booted screenshot shot.png` I got a black PNG, and the one time it wasn't black it was 2007x2853 which doesn't match the "5.4-inch" numbers I expected. What sizes does Apple actually want, how do I get a screenshot of each display from the simulator, and can I script it so our release checklist runs it? Please don't make up simctl flags; our last release got blocked for a day because of a wrong size.
