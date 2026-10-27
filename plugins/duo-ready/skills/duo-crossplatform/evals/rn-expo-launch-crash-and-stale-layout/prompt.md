---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We have an Expo app (bare workflow, `react-native` 0.87.2, `expo` SDK 57) called Ledgerly. I installed Xcode 27.1 yesterday so we can test on the new folding iPhone simulator, and now the app won't even start there. The simulator shows "Application failed to launch: UIScene life cycle is required for apps built with this SDK." On an iPhone 18 Pro simulator it still runs fine.

Our `ios/Ledgerly/AppDelegate.swift` creates the window with `UIWindow(frame: UIScreen.main.bounds)` and there is no SceneDelegate. `ios/Ledgerly/Info.plist` has `UISupportedInterfaceOrientations` set to portrait only.

Second problem: once I got it running on the regular simulator and resized the window with the Resizable iPhone, our dashboard columns don't change. We have `const { width } = Dimensions.get('window');` at the top of `src/screens/Dashboard.tsx` and a `const isTablet = Platform.isPad;` in `src/theme/layout.ts` that picks a two-column layout. Our safe-area code does `paddingHorizontal: Math.max(insets.left, insets.right)`.

Can you tell me exactly what to change, in what order, and what is actually confirmed vs. guesswork? We also want to know whether we should pick up one of those react-native "duo" packages on npm to detect the hinge.
