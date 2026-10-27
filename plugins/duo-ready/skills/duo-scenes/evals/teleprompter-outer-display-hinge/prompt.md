---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I maintain a SwiftUI video-recording app (`RecorderApp`, iOS 27.1 target, Xcode 27.1). Two feature requests for the new foldable iPhone:

a) When someone films a friend with the rear camera on the open phone, we want the friend to see the script scrolling on the small outside screen. I found `UISceneAccessory` and `CameraCaptureAccessory` but I'm confused: which one do I use from SwiftUI, do I need to add a second scene to `UIApplicationSceneManifest` for it, and can I also show the script on the outer screen when we're NOT recording (e.g. a "get ready" countdown before the session starts)? Our capture view is `CaptureView.swift` and the model is `RecorderModel`. It seems to work in the simulator already without a session running, so is that good enough to ship?

b) Designers want "tent mode": when the phone is folded past about 110 degrees and standing up, switch to a two-pane layout with the preview on top and controls on the bottom, and add a little parallax on the record button that follows the hinge. Which hinge API gives me the angle and the enum for closed/partially open/fully open, and what thresholds does Apple use for tent vs laptop?

Please write the actual code. We don't want anything that isn't in Apple's docs.
