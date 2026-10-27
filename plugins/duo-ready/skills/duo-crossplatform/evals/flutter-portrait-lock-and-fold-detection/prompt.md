---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I maintain a Flutter 3.47 recipe app (Sprig). We rebuilt with Xcode 27.1 and it launches on the iPhone Duo simulator, but when I press the "Open" button in Device Hub the recipe page is laid out as a tall phone screen squashed into a wide window, with the step list running straight across the middle where the fold is when the device is half open.

In `lib/main.dart` we call `SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp])` so I assumed the inner display would stay portrait. In `lib/widgets/recipe_page.dart` we have `padding: EdgeInsets.symmetric(horizontal: MediaQuery.of(context).padding.left)` and we store `final size = MediaQuery.of(context).size;` in an `initState` field. We also pause our cooking timer whenever `AppLifecycleState` is anything but `resumed`.

Three questions:
1. Can I force portrait on the inner display? If not, what should the layout do?
2. I read that `MediaQuery.displayFeatures` tells you where the hinge is. Can I use it to keep the step list off the fold?
3. Is there any Flutter package for this, and is Flutter going to support two windows side by side like the Mail demo?

Please be explicit about which answers come from Apple and which are community reports.
