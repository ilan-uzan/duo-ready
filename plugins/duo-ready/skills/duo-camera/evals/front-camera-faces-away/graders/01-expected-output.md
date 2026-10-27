---
type: llm
focus: trace
weight: 1
---

The result matches this description: it diagnoses the Virtual Front Camera (1080p/60, no depth, auto-switching) behind `.builtInWideAngleCamera` at `.front`, recommends `.builtInOuterUltraWideCamera`/`.builtInInnerUltraWideCamera` with `AVCaptureDeviceDirectionCoordinator` for 4K and correct facing, fixes mirroring by setting `automaticallyAdjustsVideoMirroring = false` before `isVideoMirrored` and deciding from the direction map, refuses device-model detection, says the simulator has no camera, and labels the coordinator's initializer signature as inferred rather than confirmed.
