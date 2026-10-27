---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I'm building a SwiftUI creator app (iOS 27.1 min target, Xcode 27.1). Feature request from our top users: when they open the phone flat and film themselves with the rear camera, they want their script to scroll on the small outside screen so they can read while being filmed, plus a 3-2-1 countdown before recording starts. Our camera screen is `RecordView` (uses `AVCaptureSession` via a `@Observable RecorderModel`, preview in a `UIViewRepresentable`), and the script lives in `RecorderModel.script`.

Questions:
1. Is there an API for putting content on the outside screen? I found `openWindow` but it doesn't seem to go to the other display.
2. Do I need a new scene in Info.plist for the second screen?
3. Can I put the record/stop button on the outside screen too so the person being filmed can start it?
4. I tried something with `CameraCaptureAccessory` and it showed up in the iPhone Duo simulator even before I started the session, so I assume it works everywhere. Is that right?

Please write the SwiftUI integration for `RecordView` and tell me what to test.
