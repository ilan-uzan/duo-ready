import UIKit

/// Nothing in this file may be reported: every match is suppressed, commented out,
/// or inside a DEBUG-only block. The tests assert zero findings for this path.
enum Suppressed {
    static let legacyWidth = UIScreen.main.bounds.width // duo-audit: ignore
    static let legacyScale = UIScreen.main.scale // duo-audit: ignore DUO-002

    // duo-audit: ignore DUO-001
    static let legacyHeight = UIScreen.main.bounds.height

    // let old = UIScreen.main.bounds   <- a comment, not code
    /* if UIDevice.current.userInterfaceIdiom == .pad { return 2 }  block comment */

    static func debugOnly() -> CGFloat {
        #if DEBUG
        return UIScreen.main.bounds.width
        #else
        return 0
        #endif
    }
}
