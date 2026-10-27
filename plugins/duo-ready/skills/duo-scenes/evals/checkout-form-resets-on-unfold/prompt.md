---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We're a UIKit shopping app (deployment target iOS 17, now building with Xcode 27.1). QA got an iPhone Duo on Friday and filed two bugs I don't understand.

1. If you're half way through the checkout form on the outer screen and open the phone, the form comes back empty and scrolled to the top. Our `CheckoutViewController` overrides `traitCollectionDidChange` and, when `horizontalSizeClass` flips to `.regular`, it calls `rebuildLayout()` which removes all subviews and re-adds a two-column version. Someone suggested we implement `stateRestorationActivity(for:)` in the SceneDelegate to put the form fields back. Is that the right fix?

2. We still have `UIRequiresFullScreen = YES` in Info.plist from years ago (and the `INFOPLIST_KEY_UIRequiresFullScreen` build setting). Product wants to know if that's why the app "resizes weirdly" when the phone opens and whether removing it will break our iPad-less, portrait-only setup. We also pause the promo video in `sceneWillResignActive` and QA says it freezes when they put us next to Safari in Split View.

The relevant files are `Sources/App/SceneDelegate.swift`, `Sources/Checkout/CheckoutViewController.swift` and `Info.plist`. Tell me what Apple actually says happens on a fold and what to change, and please don't guess at anything Apple hasn't published.
