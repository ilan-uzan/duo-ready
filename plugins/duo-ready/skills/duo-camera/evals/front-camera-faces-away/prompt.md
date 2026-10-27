---
tags: [duo-ready]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We ship a video-journal app (UIKit, AVFoundation, iOS 17 deployment target, just rebuilt with Xcode 27.1). Since the new foldable iPhone came out we're getting one-star reviews saying the selfie recorder "films the ceiling" or "shows my desk" when they open the phone, and a few say the preview is "mirrored the wrong way" when they use the back camera with the phone open flat on a stand.

Our camera setup is in `Sources/Capture/CaptureSessionController.swift`. The relevant part is:

```swift
final class CaptureSessionController {
    let session = AVCaptureSession()
    private var videoInput: AVCaptureDeviceInput?
    private(set) var isUsingFront = true

    func configure() throws {
        session.beginConfiguration()
        defer { session.commitConfiguration() }
        session.sessionPreset = .hd1920x1080
        let device = AVCaptureDevice.default(.builtInWideAngleCamera,
                                             for: .video,
                                             position: isUsingFront ? .front : .back)!
        let input = try AVCaptureDeviceInput(device: device)
        session.addInput(input)
        videoInput = input
        if let conn = session.connections.first {
            conn.isVideoMirrored = isUsingFront
        }
    }

    func flip() {
        isUsingFront.toggle()
        try? configure()
    }
}
```

The preview is an `AVCaptureVideoPreviewLayer` in `CapturePreviewView`. Two more things: product wants to offer 4K selfie recording on this device since Apple advertises it, and our marketing person says we should "just detect if it's the folding iPhone and use the outer camera". Can you tell me what's actually going on, what Apple says to do, and give me the concrete changes? I can't reproduce any of this in the simulator.
