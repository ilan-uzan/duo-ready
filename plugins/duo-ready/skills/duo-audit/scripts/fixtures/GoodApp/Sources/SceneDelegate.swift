import UIKit
import AVKit

final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession,
               options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = AdaptiveViewController()
        window.makeKeyAndVisible()
        self.window = window
    }

    func windowScene(_ windowScene: UIWindowScene, didUpdateEffectiveGeometry previousGeometry: UIWindowScene.Geometry) {
        // Scene bounds changed (fold/unfold): layout re-reads sizes in viewDidLayoutSubviews.
    }
}

final class AdaptiveViewController: UIViewController {
    // Stored properties cannot be availability-gated; the iOS 27.1 type is exposed below.
    private var directionCoordinatorStorage: Any?
    @available(iOS 27.1, *)
    private var directionCoordinator: AVCaptureDeviceDirectionCoordinator? {
        get { directionCoordinatorStorage as? AVCaptureDeviceDirectionCoordinator }
        set { directionCoordinatorStorage = newValue }
    }

    @available(iOS 27.1, *)
    override var preferredVerticalBarBehavior: UIVerticalBarBehavior { .automatic }

    override func viewDidLoad() {
        super.viewDidLoad()
        registerForTraitChanges([UITraitHorizontalSizeClass.self, UITraitVerticalSizeClass.self]) {
            (self: Self, _: UITraitCollection) in self.view.setNeedsLayout()
        }
        if #available(iOS 27.1, *) {
            let hinge = UIHingeInteraction { _, update in _ = update.hinge?.angle }
            view.addInteraction(hinge)
        }
        let scale = traitCollection.displayScale
        _ = scale
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        let content = view.bounds.inset(by: view.safeAreaInsets)
        if #available(iOS 27.1, *) {
            let regions = view.reservedRegions(kind: .division)
            _ = (content, regions, traitCollection.horizontalSizeClass)
        } else {
            _ = (content, traitCollection.horizontalSizeClass)
        }
    }

    @available(iOS 27.1, *)
    func showSplit(primary: UIViewController, secondary: UIViewController) {
        let arrangementVC = UIArrangementViewController()
        arrangementVC.setViewController(primary, for: .primary)
        arrangementVC.setViewController(secondary, for: .secondary)
        arrangementVC.updateArrangement(.split.axes(.horizontal))
        present(arrangementVC, animated: true)
    }
}
