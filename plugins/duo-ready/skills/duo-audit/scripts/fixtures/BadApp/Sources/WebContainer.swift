import UIKit
import WebKit

final class WebContainerViewController: UIViewController {
    private let webView = WKWebView(frame: .zero)

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(webView)
    }
}
