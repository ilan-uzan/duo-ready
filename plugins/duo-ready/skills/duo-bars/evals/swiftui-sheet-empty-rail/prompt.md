---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We rebuilt our recipe app with Xcode 27.1 last week and QA ran it on the new foldable iPhone in the simulator. With the phone closed, every sheet in the app now has a weird empty strip down the right side where the toolbar buttons should be, and the Done button is sitting up in the top bar like before. Our main screen's toolbar moved to the side fine, so it's just the sheets. Here's the sheet we present most often, in `Sources/Recipes/FilterSheet.swift`:

```swift
import SwiftUI

struct FilterSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Binding var filter: RecipeFilter

    var body: some View {
        NavigationStack {
            Form {
                Picker("Course", selection: $filter.course) {
                    ForEach(Course.allCases) { Text($0.title).tag($0) }
                }
                Toggle("Vegetarian only", isOn: $filter.vegetarianOnly)
                Stepper("Max time: \(filter.maxMinutes) min", value: $filter.maxMinutes, in: 10...180, step: 10)
            }
            .navigationTitle("Filters")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
                ToolbarItem(placement: .cancellationAction) {
                    Button("Reset") { filter = .default }
                }
            }
        }
    }
}
```

Our other sheets (`ShareSheet.swift`, `ServingsSheet.swift`) have the same shape: one or two text buttons. Is there a plist flag or something to turn this off for sheets, or are we doing it wrong? I'd rather not special-case every sheet.
