import UIKit

/// A hand-rolled bottom bar built from a stack view; the system cannot move it vertically.
final class CustomTabBar: UIView {
    private let stack = UIStackView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        stack.axis = .horizontal
        addSubview(stack)
    }

    required init?(coder: NSCoder) { fatalError() }
}
