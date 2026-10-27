---
type: llm
focus: trace
weight: 1
---

The result matches this description: it implements the teleprompter with `CameraCaptureAccessory(isEnabled:)` inside `.sceneAccessory` plus `onAvailabilityChange` on the camera view, states Apple's availability conditions and disappearance rules, says no Info.plist scene entry is needed, keeps the record button in the capture UI, explains that `openWindow` and non-camera drawing on the outer display are not supported, and corrects the simulator assumption by citing known issue 190155353 and "Simulator has no camera".
