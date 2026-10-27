---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I own the mobile BFF and the analytics pipeline for our shopping app (Swift app, Node BFF). Two things landed on my desk this week after the new folding iPhone shipped.

1. Product wants "the big-screen tablet layout" served to people using the phone open. Our BFF already has a `deviceClass` field the iOS client fills from `UIDevice.current.userInterfaceIdiom` (`"phone"` or `"pad"`), and the layout service returns `columns: 3` for `"pad"`. A teammate suggested we add the machine identifier to the request header and treat `iPhone19,4` as `"pad"`. The client code that builds the header is in `Sources/Networking/DeviceInfoHeader.swift`:

```swift
import UIKit

enum DeviceInfoHeader {
    static func value() -> String {
        let idiom = UIDevice.current.userInterfaceIdiom == .pad ? "pad" : "phone"
        let bounds = UIScreen.main.bounds
        let scale = UIScreen.main.scale
        return "class=\(idiom);w=\(Int(bounds.width));h=\(Int(bounds.height));scale=\(Int(scale))"
    }
}
```

2. Our Amplitude dashboards show a new "466x678" screen resolution with only ~400 users, which doesn't line up with the number of orders coming from the new phone according to support tickets. Also the crash tool has no way to tell me whether a crash happened folded or open.

What should the header carry, what should the BFF key the layout on, and what should I log so I can segment by the phone's state? Please be specific about what Apple actually supports vs. what is a guess, because the last time we device-sniffed it bit us.
