---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I maintain a SwiftUI video app (iOS 27.1 min target, Xcode 27.1). Product wants a "tabletop mode": when the phone is half-folded and standing on a table, video on the top half and the playback controls plus the up-next list on the bottom half; when it's flat or closed, the controls float over the video like today.

Current code in `PlayerScreen.swift`:

```swift
struct PlayerScreen: View {
    @State private var showControls = true
    var body: some View {
        ScrollView {
            ZStack(alignment: .bottom) {
                VideoSurface()
                if showControls { ControlsBar() }
            }
            UpNextList()
        }
        .navigationTitle("Now Playing")
    }
}
```

Plan from a teammate: read the hinge angle with `onHingeChange`, and if it's between 90 and 150 degrees switch to a `VStack` with the video on top. Is there a pose enum I should use instead of guessing the angles? Also can I lock this screen to landscape when it's open?
