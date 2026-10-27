---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I just inherited an old UIKit app from a contractor and my PM is asking whether it "works on the new folding iPhone" because a customer complained the app shows up small in the middle of the screen with black around it when the phone is open. I have never touched this codebase. There is an AppDelegate.swift, a LayoutHelpers.swift full of screen-size math, a CustomTabBar.swift, some Objective-C in Legacy.m, and a WebContainer.swift. The repo also seems to have leftover React Native, Flutter and Capacitor config files from an experiment someone did, plus a Unity ProjectSettings folder.

A stripped copy of the project lives in this repo at plugins/duo-ready/skills/duo-audit/scripts/fixtures/BadApp (that's the real structure, just trimmed).

Can you check it for me and tell me, in priority order, what to fix first? I don't want a 50-item list, I want to know what's actually blocking us and what I can ignore for now. Also, do I need Xcode 27.1 or is the Xcode I have (27.0) fine?
