---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I'm the PM on Ladle, a recipe app (SwiftUI, TabView with four tabs, NavigationStack per tab). Our designer sent over Figma frames for the new foldable iPhone and I need to sign off tomorrow. I can't share the Figma link, but here is what the frames show:

Closed (outer display):
- Our own bottom tab bar, drawn as a custom view with text labels under each icon ("Home", "Search", "Saved", "Plan"), fixed at the bottom of the screen.
- A nav bar with a text-only "Save" button on the right and a "Filter" text button on the left.
- A hero photo at the top of each recipe, set to fill the full width and cropped from the center.

Open (inner display):
- A 3-column grid of recipe cards centered on the screen.
- The same tab bar, still at the bottom, with a sidebar nobody asked for removed.
- A new "Cook Mode" that only appears when the phone is propped on a table like a laptop: the recipe video on the top half, step-by-step instructions on the bottom half. The designer wants it to trigger at about 110 degrees. In Cook Mode the Save and Share buttons are hidden to keep it clean.

She also asked me what the point dimensions and margins of both screens are so she can tighten the frames, and whether we should make a special "half folded" frame too.

Can you review this against Apple's guidance and tell me what I should push back on before I sign off? Please quote Apple where you can so I can forward it.
