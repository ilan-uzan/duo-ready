import UIKit
import AVFoundation

enum LayoutHelpers {
    // Cached at launch: goes stale on fold.
    static let screenScale = UIScreen.main.scale
    static let keyWindowFrame = UIApplication.shared.windows.first?.frame ?? .zero

    static var isTablet: Bool {
        return UIDevice.current.userInterfaceIdiom == .pad
    }

    static func columns(for view: UIView) -> Int {
        if UIDevice.current.orientation.isLandscape {
            return 3
        }
        if view.bounds.width == 375 {
            return 1
        }
        if view.bounds.width > 900 {
            return 2
        }
        let ratio = view.bounds.width / 375
        return ratio > 1 ? 2 : 1
    }

    static func contentWidth(in view: UIView) -> CGFloat {
        return view.bounds.width - view.safeAreaInsets.left * 2
    }

    static func horizontalInset(in view: UIView) -> CGFloat {
        return max(view.safeAreaInsets.left, view.safeAreaInsets.right)
    }

    static func modelIdentifier() -> String {
        var systemInfo = utsname()
        uname(&systemInfo)
        let mirror = Mirror(reflecting: systemInfo.machine)
        return mirror.children.compactMap { $0.value as? Int8 }.filter { $0 != 0 }.map { String(UnicodeScalar(UInt8($0))) }.joined()
    }

    static func isProMax() -> Bool {
        return modelIdentifier() == "iPhone16,2" || UIDevice.current.model.contains("iPad")
    }

    static func configureHero(_ imageView: UIImageView) {
        imageView.contentMode = .scaleAspectFill
    }

    static func playerHeight(for width: CGFloat) -> CGFloat {
        return width * 9.0 / 16.0
    }

    static func configurePlayer(_ layer: AVPlayerLayer) {
        layer.videoGravity = .resizeAspectFill
    }
}

final class RootViewController: UIViewController {
    override var prefersStatusBarHidden: Bool {
        return true
    }

    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return .portrait
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        navigationController?.setNavigationBarHidden(true, animated: false)
        if UIApplication.shared.statusBarOrientation.isPortrait {
            view.addSubview(CustomTabBar(frame: .zero))
        }
    }
}
