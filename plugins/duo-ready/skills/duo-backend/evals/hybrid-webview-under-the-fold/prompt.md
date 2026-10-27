---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We ship a hybrid news reader: a thin UIKit shell with a full-screen `WKWebView` hosting our React app, plus the same web bundle served to Safari as a PWA. On the new folding iPhone, when the phone is half open on a table, our sticky article header and the bottom reading toolbar land right on the crease, and when the phone opens the layout jumps from the phone design to the tablet design because our breakpoint is `@media (min-width: 640px)`.

The web team read about CSS viewport segments and `navigator.devicePosture` and wants to use them to keep content out of the crease. Before they spend a sprint on it: does that work inside our `WKWebView` on iOS 27.1? Does it work in Safari? If not, what is the supported way to tell the page where the crease and the camera are?

Relevant bits:

`Shell/ArticleWebViewController.swift`
```swift
final class ArticleWebViewController: UIViewController {
    private let webView = WKWebView(frame: .zero)

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(webView)
        webView.frame = UIScreen.main.bounds
        webView.scrollView.contentInsetAdjustmentBehavior = .never
    }
}
```

`web/src/styles/layout.css`
```css
.reader { height: 100vh; padding: 0 16px; }
.toolbar { position: fixed; bottom: 0; left: 0; right: 0; height: 56px; }
@media (min-width: 640px) { .reader { max-width: 720px; margin: 0 auto; } }
```

`web/src/platform.ts`
```ts
export const isTablet = /iPad/.test(navigator.userAgent) || window.innerWidth >= 640;
```

Give me the honest answer on what Apple supports today and a concrete plan for both the shell and the web bundle.
