---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I maintain a UIKit document editor (about 60k lines, deployment target iOS 17). We moved to Xcode 27.1 and tested on the iPhone Duo simulator. Our editor screen's buttons don't move to the side at all when the phone is closed; they stay in a strip along the bottom and now the strip overlaps the column where the status bar lives. The screen is `EditorViewController`, pushed onto a `UINavigationController`. Years ago we hid the nav bar and built our own bars:

```swift
// EditorViewController.swift (excerpt)
override func viewDidLoad() {
    super.viewDidLoad()
    navigationController?.setNavigationBarHidden(true, animated: false)

    let bar = UIToolbar()
    bar.items = [
        UIBarButtonItem(title: "Close", style: .plain, target: self, action: #selector(close)),
        UIBarButtonItem.flexibleSpace(),
        UIBarButtonItem(customView: fontPicker),         // a UISegmentedControl: Body / Heading / Code
        UIBarButtonItem.flexibleSpace(),
        UIBarButtonItem(image: UIImage(systemName: "ellipsis.circle"), menu: moreMenu),
        UIBarButtonItem(title: "Done", style: .done, target: self, action: #selector(done)),
    ]
    view.addSubview(bar)
    // ... constraints pin `bar` to view.bottomAnchor
}
```

`moreMenu` has Export, Duplicate, Move to Folder, and Word Count. Two questions. First, what do I have to change so the system lays these out vertically like Apple's apps do, and in what order will Close / Done / the rest end up? Second, our full-screen "Focus mode" variant of the same editor (`FocusEditorViewController`, a subclass) should probably keep everything horizontal because it's one big canvas with a single Exit button. Can I opt just that subclass out, and is there a trait or property I can read to know which side the bar is on so I can shift my floating word-count pill away from it?
