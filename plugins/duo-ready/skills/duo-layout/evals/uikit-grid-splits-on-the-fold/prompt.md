---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We shipped a UIKit photo app (Objective-C free, Swift 6, deployment target iOS 17) and a tester with the new foldable iPhone sent screenshots: when the phone is half open the fourth column of our photo grid is split right down the crease, and after she opens it fully the grid keeps the narrow layout until she scrolls. On the closed screen the "Close" button of our full-screen viewer is hidden behind the clock.

The grid is `PhotoGridViewController` using `UICollectionViewFlowLayout`. Column width comes from `LayoutMetrics.swift`:

```swift
enum LayoutMetrics {
    static let screenWidth = UIScreen.main.bounds.width
    static var columns: Int { UIDevice.current.userInterfaceIdiom == .pad ? 6 : 3 }
    static var itemWidth: CGFloat { (screenWidth - 16 * CGFloat(columns + 1)) / CGFloat(columns) }
}
```

`PhotoViewerViewController` pins its close button with `button.topAnchor.constraint(equalTo: view.topAnchor, constant: 54)` and `button.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16)`, and the controller sets `prefersStatusBarHidden = true`.

We rebuilt with Xcode 27.1 already. What exactly do I change, and how many points wide is the inner screen so I can pick the column count?
