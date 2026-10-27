#!/usr/bin/env python3
"""duo_audit.py - iPhone Duo readiness audit for iOS projects (iOS 27.1 / Xcode 27.1).

Scans an iOS project directory for code and configuration patterns that Apple
says break or degrade apps on the foldable iPhone Duo, and prints a prioritized
report. Zero dependencies: Python 3.9+ standard library only.

Usage:
    python3 duo_audit.py <path> [--format text|json|markdown]
                                [--min-severity P0|P1|P2] [--ignore <glob>]...
                                [--no-color] [--list-rules]

Exit codes: 0 = no P0 findings, 1 = at least one P0 finding, 2 = usage error.

Every rule carries a "source" that points at Apple's own guidance. Rules whose
*detection* is a pattern-matching approximation are tagged "heuristic"; the
Apple guidance they cite still applies, but expect false positives. Rules
with no Apple statement behind them say so explicitly in their source field.

Main Apple sources (all cited inline in the rule table below):
  * Three steps to make your app shine on iPhone Duo
      https://developer.apple.com/iphone-duo/prepare/
  * Preparing your app for iPhone Duo (Technology Overviews)
      https://developer.apple.com/documentation/technologyoverviews/preparing-your-app-for-iphone-duo
  * Tech Talks 111461 (Prepare), 111462 (Raise the bar), 111463 (Strike a pose),
    111464 (Multiple displays and scenes), 111465 (Camera), 111466 (Design)
      https://developer.apple.com/videos/play/tech-talks/<id>/
  * DTS "A Summary of the iPhone Duo Group Lab"
      https://developer.apple.com/forums/thread/847644
  * TN3192 Migrating your app from the deprecated UIRequiresFullScreen key
      https://developer.apple.com/documentation/technotes/tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key
  * Xcode 27.1 Release Notes
      https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes
  * App Store Connect screenshot specifications
      https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications

Inline suppression: append ``// duo-audit: ignore`` (all rules) or
``// duo-audit: ignore DUO-003`` (one or more rule ids) to the offending line,
or put the comment on its own line immediately above it.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import plistlib
import re
import sys
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

__version__ = "1.0.0"

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

SEVERITIES: Tuple[str, ...] = ("P0", "P1", "P2")
SKIP_DIRS = frozenset({
    ".git", ".hg", ".svn", "Pods", "DerivedData", "node_modules", ".build",
    "Carthage", "build", ".swiftpm", "xcuserdata", ".idea", ".vscode",
})
MAX_FILE_BYTES = 2 * 1024 * 1024  # skip generated monsters

# Apple sources (every URL / Tech Talk id below appears in Apple's Duo material).
SRC_PREPARE = "https://developer.apple.com/iphone-duo/prepare/"
SRC_OVERVIEW = ("https://developer.apple.com/documentation/technologyoverviews/"
                "preparing-your-app-for-iphone-duo")
SRC_TT_PREPARE = "Tech Talk 111461 https://developer.apple.com/videos/play/tech-talks/111461/"
SRC_TT_BARS = "Tech Talk 111462 https://developer.apple.com/videos/play/tech-talks/111462/"
SRC_TT_POSE = "Tech Talk 111463 https://developer.apple.com/videos/play/tech-talks/111463/"
SRC_TT_SCENES = "Tech Talk 111464 https://developer.apple.com/videos/play/tech-talks/111464/"
SRC_TT_CAMERA = "Tech Talk 111465 https://developer.apple.com/videos/play/tech-talks/111465/"
SRC_TT_DESIGN = "Tech Talk 111466 https://developer.apple.com/videos/play/tech-talks/111466/"
SRC_GROUPLAB = "https://developer.apple.com/forums/thread/847644"
SRC_UIKIT_QA = ("Apple UIKit Q&A https://developer.apple.com/forums/activities/1670080 "
                "(summary: https://antongubarenko.substack.com/p/iphone-duo-uikit-q-and-a-forums)")
SRC_TN3192 = ("https://developer.apple.com/documentation/technotes/"
              "tn3192-migrating-your-app-from-the-deprecated-uirequiresfullscreen-key")
SRC_HIG = "https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo"
SRC_XCODE_RN = "https://developer.apple.com/documentation/xcode-release-notes/xcode-27_1-release-notes"
SRC_ASC_NEWS = "https://developer.apple.com/news/?id=kkphp5qo"
SRC_ASC_SHOTS = ("https://developer.apple.com/help/app-store-connect/reference/"
                 "app-information/screenshot-specifications")
SRC_HEURISTIC = "Heuristic - no Apple statement covers this exact pattern."


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Rule:
    """One audit rule. ``pattern`` is None for project-level rules."""
    id: str
    severity: str
    title: str
    why: str
    fix: str
    source: str
    pattern: Optional[str] = None            # trigger regex (code rules only)
    kinds: Tuple[str, ...] = ("swift", "objc")
    veto: Optional[str] = None               # skip if this matches the trigger line
    window: int = 0                          # look-ahead lines for confirm/veto_window
    confirm: Optional[str] = None            # must match within the window
    veto_window: Optional[str] = None        # must not match within the window
    heuristic: bool = False                  # detection is approximate


@dataclass
class Finding:
    rule_id: str
    severity: str
    title: str
    file: str
    line: int
    snippet: str
    why: str
    fix: str
    source: str
    heuristic: bool = False


@dataclass
class Adopted:
    key: str
    name: str
    description: str
    file: str
    line: int
    count: int = 1


@dataclass
class PlistInfo:
    rel: str
    text: str
    data: dict
    is_app: bool


@dataclass
class PbxInfo:
    rel: str
    text: str
    last_upgrade: Optional[int]
    is_app: bool
    catalyst: bool
    settings: Dict[str, str]  # INFOPLIST_KEY_* -> value (first seen)


@dataclass
class ProjectFacts:
    """Cross-file facts gathered during the walk, consumed by project rules."""
    plists: List[PlistInfo] = field(default_factory=list)
    pbxprojs: List[PbxInfo] = field(default_factory=list)
    has_app_delegate: bool = False
    has_scene_delegate: bool = False
    has_swiftui_app: bool = False
    has_available_271: bool = False
    webview_files: List[Tuple[str, int]] = field(default_factory=list)
    api271_files: Dict[str, Tuple[int, bool]] = field(default_factory=dict)  # rel -> (line, guarded)
    framework_hits: Dict[str, Tuple[str, int, str]] = field(default_factory=dict)  # rule -> (rel, line, snippet)


# --------------------------------------------------------------------------- #
# Rule table (data, not code)
# --------------------------------------------------------------------------- #

_SCREEN_SCALE = (r"(?:UIScreen\.main|UIScreen\.mainScreen\(\)|\[UIScreen mainScreen\])\s*\.?\s*"
                 r"(?:native)?[sS]cale\b|\[\[UIScreen mainScreen\]\s+(?:native)?[sS]cale\]")
_DEVICE_DIMS = r"(?:320|375|390|393|402|414|428|430|440|480|568|667|736|812|844|852|874|896|926|932|956)"
_HARDCODED_DIM = (
    r"(?i)(?:width|height)\s*(?:==|!=|>=|<=|>|<)\s*(?<![\d.])" + _DEVICE_DIMS + r"(?:\.0+)?(?![\d.])"
    r"|(?<![\d.])" + _DEVICE_DIMS + r"(?:\.0+)?\s*(?:==|!=|>=|<=|>|<)\s*[\w.]*(?:width|height)\b"
    r"|/\s*(?<![\d.])(?:375|390|393|402|414|428|430|440)(?:\.0+)?(?![\d.])"
)
_BAR_NAMES = r"(?:TabBar|Tabbar|ToolBar|Toolbar|BottomBar|NavBar|NavigationBar)"
API_271_PATTERN = (
    r"\bArrangementView\b|UIArrangementViewController|reservedRegions\(|\bReservedRegion\b|"
    r"onHingeChange|UIHingeInteraction|CameraCaptureAccessory|toolbarVerticalBehavior|"
    r"preferredVerticalBarBehavior|toolbarVerticalEdge|verticalBarEdge|"
    r"AVCaptureDeviceDirectionCoordinator|\.axisBehavior\b|\.visibilityPriority\b|"
    r"ToolbarOverflowMenu|additionalOverflowItems|presentationPlacement\("
)

RULES: Tuple[Rule, ...] = (
    Rule("DUO-001", "P0", "UIScreen.main used for layout",
         why="Apple: UIScreen.main is \"ambiguous on two-display devices and will be deprecated\"; "
             "its bounds go stale when the device folds and the scene is resized mid-session.",
         fix="Replace with view.bounds / window.bounds (SwiftUI: GeometryReader or onGeometryChange); "
             "re-read sizes in layoutSubviews, viewDidLayoutSubviews or viewWillTransition(to:with:); "
             "never store a UIScreen - reach it via view.window?.windowScene?.screen.",
         source=f"{SRC_PREPARE} ; {SRC_TT_PREPARE}",
         pattern=r"UIScreen\.main\b|UIScreen\.mainScreen\(\)|\[UIScreen mainScreen\]",
         veto=_SCREEN_SCALE),
    Rule("DUO-002", "P1", "UIScreen.main.scale used instead of displayScale",
         why="Apple's Tech Talk shows `let screenScale = UIScreen.main.scale` as the 'before' and "
             "`traitCollection.displayScale` as the 'after'; the main screen is ambiguous on iPhone Duo.",
         fix="Use traitCollection.displayScale (UIKit) or @Environment(\\.displayScale) (SwiftUI).",
         source=f"{SRC_TT_PREPARE} ; {SRC_PREPARE}",
         pattern=_SCREEN_SCALE),
    Rule("DUO-003", "P1", "UIWindow created from a frame instead of a window scene",
         why="Apple lists `UIWindow(frame: UIScreen.main.bounds)` among the patterns to fix: the window "
             "must belong to a scene so the system can resize it between displays.",
         fix="Create windows with UIWindow(windowScene:) from your UIWindowSceneDelegate.",
         source=SRC_PREPARE,
         pattern=r"UIWindow\(frame:|\[\[UIWindow alloc\]\s+initWithFrame:"),
    Rule("DUO-004", "P0", "userInterfaceIdiom used to choose a layout",
         why="Apple: \"Don't use UIDevice.userInterfaceIdiom ... for layout decisions\"; iPhone Duo has "
             "no idiom of its own and \"iPhone apps can have any combination of size classes\".",
         fix="Branch on traitCollection.horizontalSizeClass / verticalSizeClass (or the SwiftUI "
             "environment values) and on the container's bounds; don't treat regular width as iPad.",
         source=f"{SRC_OVERVIEW} ; {SRC_PREPARE} ; {SRC_GROUPLAB}",
         pattern=(r"userInterfaceIdiom\s*(?:==|!=)\s*\.(?:pad|phone)\b|UIUserInterfaceIdiom(?:Pad|Phone)\b|"
                  r"UI_USER_INTERFACE_IDIOM\(\)|switch\s+[\w.]*userInterfaceIdiom")),
    Rule("DUO-005", "P0", "Device or interface orientation used for layout",
         why="Apple: remove layout logic based on UIDevice.current.orientation, statusBarOrientation, "
             "interfaceOrientation or windowScene.effectiveGeometry.interfaceOrientation; the inner "
             "display does not honor supported orientations.",
         fix="Compare available width vs height, or use size classes; observe geometry via "
             "viewWillTransition(to:with:) / windowScene(_:didUpdateEffectiveGeometry:).",
         source=f"{SRC_PREPARE} ; {SRC_TT_PREPARE}",
         pattern=(r"UIDevice\.current\.orientation\b|\[\[UIDevice currentDevice\]\s+orientation\]|"
                  r"\[UIDevice currentDevice\]\.orientation|statusBarOrientation\b|\binterfaceOrientation\b|"
                  r"UIInterfaceOrientationIs(?:Portrait|Landscape)|UIDeviceOrientationIs(?:Portrait|Landscape)|"
                  r"orientation\.isPortrait\b|orientation\.isLandscape\b|orientationDidChangeNotification|"
                  r"UIDeviceOrientationDidChangeNotification")),
    Rule("DUO-006", "P1", "supportedInterfaceOrientations override is portrait-only",
         why="Apple: \"The inner display doesn't honor your declared interface orientations\"; portrait-only "
             "apps still receive compact and regular size-class changes and are shown wide on the inner display.",
         fix="Support all orientations (TN3192 migration checklist) and lay out from size classes; "
             "games may lock orientation but must still fill the screen in every pose.",
         source=f"{SRC_GROUPLAB} ; {SRC_TT_PREPARE} ; {SRC_TN3192}",
         pattern=r"supportedInterfaceOrientations", window=4,
         confirm=r"\.portrait\b|UIInterfaceOrientationMaskPortrait\b",
         veto_window=r"(?i)landscape|\.all\b|allButUpsideDown|UIInterfaceOrientationMaskAll\b"),
    Rule("DUO-007", "P1", "Info.plist UISupportedInterfaceOrientations is portrait-only",
         why="Apple: UISupportedInterfaceOrientations is honored on the outer display only; the inner "
             "display ignores it, so the app must still handle regular-width, wide layouts.",
         fix="Declare all orientations and drive layout from size classes; remove any assumption "
             "that a portrait lock means a tall, narrow canvas.",
         source=f"{SRC_GROUPLAB} ; {SRC_TT_PREPARE}"),
    Rule("DUO-008", "P1", "UIRequiresFullScreen = YES (deprecated)",
         why="TN3192: UIRequiresFullScreen is deprecated and \"no longer opts your app out of resizing\"; "
             "with the iOS 27 SDK it only yields discrete resizing, and the app still resizes on fold/unfold.",
         fix="Remove UIRequiresFullScreen (and INFOPLIST_KEY_UIRequiresFullScreen), support all "
             "orientations, and observe windowScene(_:didUpdateEffectiveGeometry:).",
         source=f"{SRC_TN3192} ; {SRC_TT_PREPARE}"),
    Rule("DUO-009", "P0", "No scene lifecycle (UIApplicationSceneManifest / scene delegate missing)",
         why="Apple's UIKit Q&A: \"Xcode 27 requires the scene lifecycle, so migrate first\"; React Native "
             "0.88 rc failed to launch on the Duo simulator with \"UIScene life cycle is required\".",
         fix="Add UIApplicationSceneManifest to Info.plist, add a UIWindowSceneDelegate, and move "
             "window creation from the AppDelegate to scene(_:willConnectTo:options:).",
         source=f"{SRC_UIKIT_QA} ; https://github.com/react/react-native/issues/58606"),
    Rule("DUO-010", "P0", "No launch screen (UILaunchScreen / UILaunchStoryboardName)",
         why="TN3192: \"Starting in iOS 27 and iPadOS 27, a launch screen is required for App Store "
             "submission\" (TN3208).",
         fix="Add a UILaunchScreen dictionary (or UILaunchStoryboardName) to Info.plist, or set "
             "INFOPLIST_KEY_UILaunchScreen_Generation = YES in build settings.",
         source=SRC_TN3192),
    Rule("DUO-011", "P0", "Hard-coded iPhone screen dimension compared against width/height",
         why="Apple: remove checks like `bounds.height == 844` and \"avoid fixed widths, breakpoints, and "
             "metrics tied to a specific screen\". The literal set this rule matches is a heuristic list.",
         fix="Size views relative to their container; choose layouts from size classes and the "
             "container's bounds, not device point sizes.",
         source=f"{SRC_PREPARE} ; {SRC_TT_DESIGN}",
         pattern=_HARDCODED_DIM, heuristic=True),
    Rule("DUO-012", "P1", "Magic width/height breakpoint",
         why="Apple: \"avoid fixed widths, breakpoints, and metrics tied to a specific screen\"; a fixed "
             "threshold can never be hit (or always hit) on a display the threshold wasn't written for.",
         fix="Replace numeric breakpoints with horizontalSizeClass/verticalSizeClass checks, "
             "or derive thresholds from content (e.g. minimum column width).",
         source=SRC_TT_DESIGN,
         pattern=r"(?i)\b\w*(?:width|height)\s*(?:>=|<=|>|<)\s*(?<![\d.])(?:[3-9]\d{2}|\d{4})(?:\.0+)?(?![\d.])",
         veto=_HARDCODED_DIM + r"|sizeClass", heuristic=True),
    Rule("DUO-013", "P2", "Fill content mode on media without a focal point",
         why="Apple: \"Hero images and video set to .scaleAspectFill or .aspectRatio(contentMode: .fill) can "
             "lose important content on wider displays.\"",
         fix="\"Use the current size classes or aspect ratio to choose between fill and fit, or set a focal "
             "point.\" Lines mentioning a focal point are not flagged.",
         source=SRC_PREPARE,
         pattern=(r"\.scaleAspectFill\b|UIViewContentModeScaleAspectFill|"
                  r"\.aspectRatio\([^)]*contentMode:\s*\.fill\s*\)|\.scaledToFill\(\)|"
                  r"resizeAspectFill\b|AVLayerVideoGravityResizeAspectFill"),
         veto=r"(?i)focal|focus|sizeClass", heuristic=True),
    Rule("DUO-014", "P2", "Fixed 16:9 aspect ratio",
         why="Apple: \"Don't assume fixed ratios. Resize to fit each pose, favor changing aspect ratio over "
             "letterboxing\"; Split View and PiP mean apps \"may run at varying aspect ratios\".",
         fix="Let players and media fill the available bounds (AVKit resizes automatically); if padding "
             "is unavoidable, add artwork to it (HIG).",
         source=f"{SRC_GROUPLAB} ; {SRC_TT_DESIGN} ; {SRC_HIG}",
         pattern=(r"(?<![\d.])16(?:\.0)?\s*/\s*9(?:\.0)?(?![\d.])|(?<![\d.])9(?:\.0)?\s*/\s*16(?:\.0)?(?![\d.])|"
                  r"(?<![\d.])1\.77[78]\d*|(?<![\d.])0\.5625(?!\d)"),
         heuristic=True),
    Rule("DUO-015", "P1", "Device model string sniffed for layout",
         why="Apple: no API identifies iPhone Duo - \"Design from size, traits, and reserved regions, not "
             "hardware names or screen dimensions\"; Duo has no UIUserInterfaceIdiom of its own.",
         fix="Delete model-name tables; use size classes, scene geometry and reservedRegions(kind:).",
         source=f"{SRC_UIKIT_QA} ; {SRC_GROUPLAB}",
         pattern=(r"\butsname\b|hw\.machine|UIDevice\.current\.(?:model|localizedModel|name)\b|"
                  r"\[\[UIDevice currentDevice\]\s+(?:model|localizedModel|name)\]|"
                  r"\[UIDevice currentDevice\]\.(?:model|localizedModel|name)\b|\"iPhone\d{1,2},\d{1,2}\""),
         veto=r"^\s*#?(?:import|include)\b"),
    Rule("DUO-016", "P2", "Status bar hidden - side inset still applies",
         why="Apple: safe areas \"are often asymmetric on iPhone Duo. Handle each side independently.\" A "
             "developer report (skarol.dev) found that hiding the status bar hides the icons but not the "
             "side-column safe-area inset.",
         fix="Constrain to safeAreaLayoutGuide / keep .ignoresSafeArea() for backgrounds only, and "
             "verify the hidden-status-bar screens in the iPhone Duo simulator.",
         source=f"{SRC_TT_PREPARE} ; report: https://skarol.dev/posts/getting-your-app-ready-for-iphone-duo/",
         pattern=r"prefersStatusBarHidden|\.statusBarHidden\(|\.statusBar\(hidden:|setStatusBarHidden:|statusBarHidden\s*=",
         window=3, confirm=r"\btrue\b|\bYES\b", heuristic=True),
    Rule("DUO-017", "P1", "Custom tab/tool bar built from plain views",
         why="Apple: \"Only system containers adapt automatically (TabView, UITabBarController, toolbars "
             "with standard items). Custom bars and UIToolbar subviews do not.\"",
         fix="Set toolbar items on a view controller inside a navigation controller / use "
             ".toolbar(content:) on NavigationStack; use UITabBarController or TabView for tabs.",
         source=f"{SRC_GROUPLAB} ; {SRC_OVERVIEW}",
         pattern=(r"^\s*(?:@objc\s+)?(?:(?:final|public|internal|private|fileprivate|open)\s+)*(?:class|struct)\s+"
                  r"\w*" + _BAR_NAMES + r"\w*\s*:\s*(?:UIView|UIStackView|UIControl|UIVisualEffectView|View)\b|"
                  r"@interface\s+\w*" + _BAR_NAMES + r"\w*\s*:\s*(?:UIView|UIStackView|UIControl)\b"),
         heuristic=True),
    Rule("DUO-018", "P2", "Navigation bar hidden (custom top bar will not go vertical)",
         why="Apple: if the system doesn't present your bars vertically, \"check that you're using the bar "
             "support that navigation containers ... provide\"; a hidden system bar replaced by a custom "
             "header stays horizontal.",
         fix="Keep the system navigation bar and add items with .toolbar(content:) / navigationItem; "
             "extend hero art under the bar with backgroundExtensionEffect() or UIBackgroundExtensionView.",
         source=SRC_OVERVIEW,
         pattern=(r"\.navigationBarHidden\(\s*true\s*\)|\.toolbar\(\s*\.hidden\b|\.toolbarVisibility\(\s*\.hidden\b|"
                  r"setNavigationBarHidden\(\s*true|setNavigationBarHidden:\s*YES|isNavigationBarHidden\s*=\s*true|"
                  r"navigationBarHidden\s*=\s*YES|\.navigationBar\.isHidden\s*=\s*true"),
         heuristic=True),
    Rule("DUO-019", "P1", "Project not upgraded to Xcode 27.1 (LastUpgradeCheck < 2710)",
         why="Apple: apps built with the iOS 26 SDK run centered with empty space; iOS 27 SDK fills most of "
             "the inner display; only the iOS 27.1 SDK uses the full display with vertical bars. "
             "LastUpgradeCheck is a heuristic proxy for the Xcode version that last touched the project.",
         fix="Build with Xcode 27.1 (iOS 27.1 SDK) and re-test every pose. Developer tip (blakecrosley.com): "
             "verify the SDK stamp with `otool -l <binary> | grep -A4 LC_BUILD_VERSION`.",
         source=f"{SRC_PREPARE} ; {SRC_TT_PREPARE}", heuristic=True),
    Rule("DUO-020", "P1", "iOS 27.1-only API in a Mac Catalyst target without #if !targetEnvironment(macCatalyst)",
         why="Xcode 27.1 release notes: iOS 27.1-only APIs produce compile errors for Mac Catalyst "
             "(185924957); the documented workaround is #if !targetEnvironment(macCatalyst).",
         fix="Wrap ArrangementView / reservedRegions / hinge / vertical-bar calls in "
             "#if !targetEnvironment(macCatalyst) and gate with if #available(iOS 27.1, *).",
         source=f"{SRC_XCODE_RN} ; {SRC_GROUPLAB}"),
    Rule("DUO-021", "P2", "WKWebView content cannot see the fold",
         why="Apple's UIKit Q&A: \"Query geometry in the host and pass it to the page. Viewport-segment and "
             "posture APIs are experimental Safari features, not available in WKWebView. CSS insets don't "
             "account for the fold.\"",
         fix="Read reservedRegions / safe areas in the host view and inject them into the page; use "
             "responsive layout in the web content instead of device detection.",
         source=f"{SRC_UIKIT_QA} ; {SRC_GROUPLAB}"),
    Rule("DUO-022", "P0", "Symmetric safe-area math",
         why="Apple's Tech Talk shows `view.bounds.width - view.safeAreaInsets.left * 2` as the anti-pattern: "
             "\"Safe areas and layout margins are often asymmetric on iPhone Duo. Handle each side independently.\"",
         fix="Use view.bounds.inset(by: view.safeAreaInsets) / safeAreaLayoutGuide and read left and "
             "right (leading and trailing) insets separately.",
         source=SRC_TT_PREPARE,
         pattern=(r"safeAreaInsets\.(?:left|right|leading|trailing)\s*\*\s*2\b|"
                  r"2\s*\*\s*[\w.]*safeAreaInsets\.(?:left|right|leading|trailing)\b|"
                  r"max\(\s*[\w.]*safeAreaInsets\.(?:left|leading|right|trailing)\s*,\s*"
                  r"[\w.]*safeAreaInsets\.(?:left|leading|right|trailing)\s*\)")),
    Rule("DUO-023", "P1", "Window frame read from UIApplication.shared.windows / keyWindow",
         why="Heuristic: a frame captured from the key window at launch is a cached screen size, which goes "
             "stale when the scene resizes on fold/unfold. No Apple statement names this exact API.",
         fix="Read geometry from the view's own window / windowScene at layout time "
             "(layoutSubviews, viewDidLayoutSubviews, onGeometryChange).",
         source=SRC_HEURISTIC,
         pattern=(r"UIApplication\.shared\.(?:keyWindow|windows)\b|"
                  r"\[UIApplication sharedApplication\]\s*\.?\s*(?:keyWindow|windows)\b"),
         heuristic=True),
    # Cross-platform framework advice (project-level, detected from config files).
    Rule("DUO-030", "P1", "React Native project: scene lifecycle and stale Dimensions",
         why="RN 0.88.0-rc.0 failed to launch on the Duo simulator (\"UIScene life cycle is required\"), fixed "
             "in 0.88; Apple's UIKit Q&A says the scene lifecycle is required with Xcode 27.",
         fix="Upgrade to RN 0.88+ or add SceneDelegate + UIApplicationSceneManifest (Expo: "
             "expo-build-properties ios.enableSceneSupport). Third-party guidance (iphoneduosupport.com): "
             "use useWindowDimensions() instead of module-scope Dimensions.get, per-edge safe-area insets.",
         source=f"https://github.com/react/react-native/issues/58606 ; {SRC_UIKIT_QA}"),
    Rule("DUO-031", "P2", "Flutter project: orientation lock and multi-scene limits",
         why="Apple: the inner display ignores declared orientations. Flutter's engine \"does not fully "
             "support multi-scene\" (flutter #193056, duplicate of #48838).",
         fix="Drive layout from MediaQuery size, not setPreferredOrientations; third-party guidance "
             "(iphoneduosupport.com): use per-side MediaQuery padding, pause on `paused` not `inactive`.",
         source=f"{SRC_TT_PREPARE} ; https://github.com/flutter/flutter/issues/193056"),
    Rule("DUO-032", "P2", "Capacitor/Ionic project: web content cannot see the fold",
         why="Apple: posture/viewport-segment APIs are not available in WKWebView and CSS insets don't "
             "account for the fold; web developers should use responsive design, not device detection.",
         fix="Pass fold geometry from the native host into the page; third-party guidance "
             "(iphoneduosupport.com): viewport-fit=cover, per-side env() insets, 100dvh, ResizeObserver.",
         source=f"{SRC_UIKIT_QA} ; {SRC_GROUPLAB}"),
    Rule("DUO-033", "P2", "Unity project: fixed aspect ratio and cached screen size",
         why="Apple HIG for games: \"fill the screen as the device pose changes ... Prefer changing the aspect "
             "ratio over letterboxing or pillarboxing\". No Unity-specific Apple guidance exists.",
         fix="Re-read Screen.width/height and Screen.safeArea each frame (insets are asymmetric) and "
             "avoid letterboxing; add artwork to unavoidable padding (HIG).",
         source=f"{SRC_HIG} ; {SRC_GROUPLAB}"),
)
RULES_BY_ID: Dict[str, Rule] = {r.id: r for r in RULES}

# Positive detections -> "Already adopted". Names come from Apple's Duo material.
ADOPTED_PATTERNS: Tuple[Tuple[str, str, str, str], ...] = (
    ("size_classes", "Size classes", "horizontalSizeClass/verticalSizeClass drive layout (111461)",
     r"horizontalSizeClass|verticalSizeClass"),
    ("display_scale", "displayScale", "Scale read from traits/environment instead of UIScreen.main.scale (111461)",
     r"\bdisplayScale\b"),
    ("geometry", "Geometry observation", "onGeometryChange / viewWillTransition / didUpdateEffectiveGeometry / "
     "registerForTraitChanges (prepare page, TN3192)",
     r"onGeometryChange|viewWillTransition\(to:|didUpdateEffectiveGeometry|registerForTraitChanges|viewSafeAreaInsetsDidChange"),
    ("scene_window", "Scene-based windows", "UIWindow(windowScene:) / windowScene.screen (prepare page)",
     r"UIWindow\(windowScene:|windowScene\??\.screen"),
    ("reserved_regions", "Reserved regions", "reservedRegions(kind:) for fold (division) and camera (occlusion) (111463)",
     r"reservedRegions\(|\bReservedRegion\b"),
    ("arrangement", "Arrangement views", "ArrangementView / UIArrangementViewController (111463)",
     r"\bArrangementView\b|UIArrangementViewController|arrangementViewStyle"),
    ("hinge", "Hinge APIs", "onHingeChange / UIHingeInteraction for effects (111464)",
     r"onHingeChange|UIHingeInteraction|\bDeviceHinge\b|\bUIHinge\b"),
    ("scene_accessory", "Scene accessories", "CameraCaptureAccessory / sceneAccessory / registerSceneAccessory (111464)",
     r"CameraCaptureAccessory|sceneAccessory|registerSceneAccessory|UISceneAccessory"),
    ("vertical_bars", "Vertical bar APIs", "toolbarVerticalBehavior, axisBehavior, visibilityPriority, "
     "ToolbarOverflowMenu, toolbarVerticalEdge/verticalBarEdge (111462)",
     r"toolbarVerticalBehavior|preferredVerticalBarBehavior|toolbarVerticalEdge|verticalBarEdge|\.axisBehavior\b|"
     r"\.visibilityPriority\b|ToolbarOverflowMenu|additionalOverflowItems|toolbarVerticalCompressionBehavior|"
     r"verticalBarCompressionBehavior|pinnedTrailingGroup|topBarPinnedTrailing"),
    ("camera_direction", "Camera direction coordinator",
     "AVCaptureDeviceDirectionCoordinator / inner+outer ultra-wide device types (111465)",
     r"AVCaptureDeviceDirectionCoordinator|builtInOuterUltraWideCamera|builtInInnerUltraWideCamera"),
    ("background_extension", "Background extension", "backgroundExtensionEffect / UIBackgroundExtensionView (overview)",
     r"backgroundExtensionEffect|UIBackgroundExtensionView"),
    ("sheet_placement", "Sheet placement", "presentationPlacement / preferredPlacement (overview)",
     r"presentationPlacement\(|\.preferredPlacement\b"),
    ("availability", "iOS 27.1 availability gating", "#available(iOS 27.1, *) around Duo APIs (Group Lab)",
     r"#available\(iOS 27\.1|@available\(iOS 27\.1|canImport\(SwiftUI,\s*_version"),
    ("multi_scene", "Multiple scenes", "UIApplicationSupportsMultipleScenes / UIWindowSceneActivationAction (111464)",
     r"UIApplicationSupportsMultipleScenes|UIWindowSceneActivationAction"),
)

# Fact regexes (whole-file).
_RX = {
    "webview": re.compile(r"\bWKWebView\b"),
    "scene_delegate": re.compile(r"UIWindowSceneDelegate|UISceneDelegate"),
    "swiftui_app": re.compile(r"\bstruct\s+\w+\s*:\s*(?:SwiftUI\.)?App\b"),
    "app_delegate": re.compile(r"UIApplicationDelegate\b|@UIApplicationMain|UIApplicationMain\("),
    "catalyst_guard": re.compile(r"targetEnvironment\(macCatalyst\)"),
    "avail_271": re.compile(r"#available\(iOS 27\.1|@available\(iOS 27\.1|canImport\(SwiftUI,\s*_version"),
    "api_271": re.compile(API_271_PATTERN),
    "suppress": re.compile(r"duo-audit:\s*ignore\b((?:[\s,]*DUO-\d{3})*)"),
    "debug_if": re.compile(r"^\s*#if\b(.*)$"),
    "debug_cond": re.compile(r"\bDEBUG\b|targetEnvironment\(simulator\)|\bTESTING\b|\bTEST\b"),
    "test_file": re.compile(r"(?:Tests?|Spec)\.swift$|(?:Tests?|Spec)\.m$"),
}
_COMPILED: Dict[str, re.Pattern] = {}


def rx(pattern: str) -> re.Pattern:
    """Compile-and-cache helper so the rule table stays plain strings."""
    pat = _COMPILED.get(pattern)
    if pat is None:
        pat = _COMPILED[pattern] = re.compile(pattern)
    return pat


# --------------------------------------------------------------------------- #
# Source preprocessing: comments, #if DEBUG, suppressions
# --------------------------------------------------------------------------- #

@dataclass
class Line:
    raw: str
    code: str                       # comment-stripped
    in_debug: bool
    suppress: Optional[set]         # None = not suppressed; empty set = all rules


def _strip_line_comment(code: str) -> str:
    """Remove a trailing // comment, ignoring // inside string literals (approximate)."""
    idx = 0
    while True:
        idx = code.find("//", idx)
        if idx < 0:
            return code
        if code.count('"', 0, idx) % 2 == 0:
            return code[:idx]
        idx += 2


def preprocess(text: str) -> List[Line]:
    """Split into lines with comment stripping, #if DEBUG tracking and suppressions."""
    out: List[Line] = []
    in_block = False
    debug_stack: List[bool] = []
    prev_suppress: Optional[set] = None
    for raw in text.splitlines():
        # Suppression comments are read from the raw line before stripping.
        m = _RX["suppress"].search(raw)
        suppress: Optional[set] = None
        if m:
            suppress = set(re.findall(r"DUO-\d{3}", m.group(1) or ""))
        code = raw
        # Block comments (may span lines).
        buf = []
        i = 0
        while i < len(code):
            if in_block:
                end = code.find("*/", i)
                if end < 0:
                    i = len(code)
                    break
                in_block, i = False, end + 2
            else:
                start = code.find("/*", i)
                if start < 0:
                    buf.append(code[i:])
                    break
                buf.append(code[i:start])
                in_block, i = True, start + 2
        code = _strip_line_comment("".join(buf))
        # Conditional compilation.
        stripped = code.strip()
        dm = _RX["debug_if"].match(stripped)
        if dm:
            debug_stack.append(bool(_RX["debug_cond"].search(dm.group(1))) and not dm.group(1).strip().startswith("!"))
        elif stripped.startswith("#else") and debug_stack:
            debug_stack[-1] = not debug_stack[-1]
        elif stripped.startswith("#elseif") and debug_stack:
            debug_stack[-1] = bool(_RX["debug_cond"].search(stripped))
        elif stripped.startswith("#endif") and debug_stack:
            debug_stack.pop()
        # A standalone suppression comment applies to the next line.
        effective = suppress if suppress is not None else prev_suppress
        prev_suppress = suppress if (suppress is not None and not stripped) else None
        out.append(Line(raw, code, any(debug_stack), effective))
    return out


def is_suppressed(line: Line, rule_id: str) -> bool:
    return line.suppress is not None and (not line.suppress or rule_id in line.suppress)


# --------------------------------------------------------------------------- #
# Scanners
# --------------------------------------------------------------------------- #

def scan_source(rel: str, text: str, kind: str, facts: ProjectFacts,
                findings: List[Finding], adopted: Dict[str, Adopted]) -> None:
    lines = preprocess(text)
    code_only = "\n".join(l.code for l in lines)
    # Whole-file facts.
    if _RX["app_delegate"].search(code_only):
        facts.has_app_delegate = True
    if _RX["scene_delegate"].search(code_only):
        facts.has_scene_delegate = True
    if _RX["swiftui_app"].search(code_only):
        facts.has_swiftui_app = True
    if _RX["avail_271"].search(code_only):
        facts.has_available_271 = True
    guarded = bool(_RX["catalyst_guard"].search(code_only))
    for i, line in enumerate(lines, 1):
        if _RX["webview"].search(line.code) and not any(f == rel for f, _ in facts.webview_files):
            facts.webview_files.append((rel, i))
        if rel not in facts.api271_files and _RX["api_271"].search(line.code):
            facts.api271_files[rel] = (i, guarded)
        for key, name, desc, pattern in ADOPTED_PATTERNS:
            if rx(pattern).search(line.code):
                if key in adopted:
                    adopted[key].count += 1
                else:
                    adopted[key] = Adopted(key, name, desc, rel, i)
    # Line rules.
    for rule in RULES:
        if rule.pattern is None or kind not in rule.kinds:
            continue
        trigger = rx(rule.pattern)
        for i, line in enumerate(lines, 1):
            if line.in_debug or not line.code.strip() or not trigger.search(line.code):
                continue
            # Vetoes see the raw line so an explanatory comment (e.g. "// focal point",
            # "// migrated to displayScale") can exempt the line.
            if rule.veto and rx(rule.veto).search(line.raw):
                continue
            if rule.window:
                window = "\n".join(l.code for l in lines[i - 1:i - 1 + rule.window + 1])
                if rule.confirm and not rx(rule.confirm).search(window):
                    continue
                if rule.veto_window and rx(rule.veto_window).search(window):
                    continue
            if is_suppressed(line, rule.id):
                continue
            findings.append(Finding(rule.id, rule.severity, rule.title, rel, i,
                                    line.raw.strip()[:160], rule.why, rule.fix, rule.source, rule.heuristic))


def _plist_is_app(data: dict, rel: str) -> bool:
    if "NSExtension" in data or data.get("CFBundlePackageType") not in (None, "APPL"):
        return False
    if _RX["test_file"].search(rel) or "Tests" in rel.split(os.sep):
        return False
    return any(k in data for k in ("CFBundleExecutable", "UISupportedInterfaceOrientations",
                                   "UILaunchScreen", "UILaunchStoryboardName",
                                   "UIApplicationSceneManifest", "UIRequiresFullScreen", "CFBundlePackageType"))


def scan_plist(rel: str, raw: bytes, facts: ProjectFacts) -> None:
    try:
        data = plistlib.loads(raw)
    except Exception:  # noqa: BLE001 - malformed plist: fall back to key sniffing
        text = raw.decode("utf-8", "replace")
        data = {k: True for k in re.findall(r"<key>([A-Za-z_]+)</key>", text)}
    if not isinstance(data, dict):
        return
    facts.plists.append(PlistInfo(rel, raw.decode("utf-8", "replace"), data, _plist_is_app(data, rel)))


def scan_pbxproj(rel: str, text: str, facts: ProjectFacts) -> None:
    m = re.search(r"LastUpgradeCheck\s*=\s*(\d+)", text)
    settings: Dict[str, str] = {}
    for key, val in re.findall(r"(INFOPLIST_KEY_\w+|GENERATE_INFOPLIST_FILE)\s*=\s*(\"[^\"]*\"|[^;]+);", text):
        settings.setdefault(key, val.strip().strip('"'))
    facts.pbxprojs.append(PbxInfo(
        rel, text, int(m.group(1)) if m else None,
        is_app='productType = "com.apple.product-type.application"' in text,
        catalyst=bool(re.search(r"SUPPORTS_MACCATALYST\s*=\s*YES", text)),
        settings=settings))


def scan_framework_file(rel: str, name: str, text: str, facts: ProjectFacts) -> None:
    """Detect cross-platform frameworks from their config files (first hit wins)."""
    def hit(rule_id: str, line: int, snippet: str) -> None:
        facts.framework_hits.setdefault(rule_id, (rel, line, snippet))

    if name == "package.json":
        m = re.search(r"\"react-native\"\s*:\s*\"([^\"]+)\"", text)
        if m:
            hit("DUO-030", text.count("\n", 0, m.start()) + 1, f'"react-native": "{m.group(1)}"')
    elif name == "Podfile":
        m = re.search(r"use_react_native!|react_native_pods", text)
        if m:
            hit("DUO-030", text.count("\n", 0, m.start()) + 1, m.group(0))
    elif name == "pubspec.yaml":
        m = re.search(r"^\s*flutter\s*:|sdk\s*:\s*flutter\b", text, re.M)
        if m:
            hit("DUO-031", text.count("\n", 0, m.start()) + 1, "flutter dependency in pubspec.yaml")
    elif name.startswith("capacitor.config."):
        hit("DUO-032", 1, name)
    elif name in ("ProjectSettings.asset", "ProjectVersion.txt") and "ProjectSettings" in rel.split(os.sep):
        hit("DUO-033", 1, rel)


def _line_of(text: str, needle: str) -> int:
    idx = text.find(needle)
    return text.count("\n", 0, idx) + 1 if idx >= 0 else 1


def _portrait_only(value) -> bool:
    items = value if isinstance(value, (list, tuple)) else re.split(r"[\s,]+", str(value))
    items = [str(x) for x in items if x]
    return bool(items) and all("Portrait" in x and "Landscape" not in x for x in items)


def _truthy(value) -> bool:
    return value is True or str(value).upper() in ("YES", "TRUE", "1")


def project_findings(facts: ProjectFacts, findings: List[Finding], adopted: Dict[str, Adopted]) -> None:
    """Rules that need the whole project: plist, pbxproj, framework and cross-file facts."""
    def emit(rule_id: str, rel: str, line: int, snippet: str) -> None:
        r = RULES_BY_ID[rule_id]
        findings.append(Finding(r.id, r.severity, r.title, rel, line, snippet, r.why, r.fix, r.source, r.heuristic))

    app_plists = [p for p in facts.plists if p.is_app]
    app_pbx = [p for p in facts.pbxprojs if p.is_app]
    is_app_project = bool(app_plists or app_pbx)
    anchor_rel, anchor_line = (app_plists[0].rel, 1) if app_plists else \
        ((app_pbx[0].rel, 1) if app_pbx else ("<project>", 0))
    pbx_settings: Dict[str, str] = {}
    for p in facts.pbxprojs:
        for k, v in p.settings.items():
            pbx_settings.setdefault(k, v)

    if is_app_project:
        # DUO-007 portrait-only orientations.
        for p in app_plists:
            if "UISupportedInterfaceOrientations" in p.data and _portrait_only(p.data["UISupportedInterfaceOrientations"]):
                emit("DUO-007", p.rel, _line_of(p.text, "UISupportedInterfaceOrientations"),
                     "UISupportedInterfaceOrientations = portrait only")
        if not any("UISupportedInterfaceOrientations" in p.data for p in app_plists):
            v = pbx_settings.get("INFOPLIST_KEY_UISupportedInterfaceOrientations") or \
                pbx_settings.get("INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone")
            if v and _portrait_only(v):
                p = facts.pbxprojs[0]
                emit("DUO-007", p.rel, _line_of(p.text, "INFOPLIST_KEY_UISupportedInterfaceOrientations"), v)
        # DUO-008 UIRequiresFullScreen.
        for p in app_plists:
            if _truthy(p.data.get("UIRequiresFullScreen", False)):
                emit("DUO-008", p.rel, _line_of(p.text, "UIRequiresFullScreen"), "UIRequiresFullScreen = YES")
        if _truthy(pbx_settings.get("INFOPLIST_KEY_UIRequiresFullScreen", "NO")):
            p = facts.pbxprojs[0]
            emit("DUO-008", p.rel, _line_of(p.text, "INFOPLIST_KEY_UIRequiresFullScreen"),
                 "INFOPLIST_KEY_UIRequiresFullScreen = YES")
        # DUO-009 scene lifecycle.
        manifest = any("UIApplicationSceneManifest" in p.data for p in app_plists) or \
            _truthy(pbx_settings.get("INFOPLIST_KEY_UIApplicationSceneManifest_Enabled", "NO"))
        if manifest:
            p = next((p for p in app_plists if "UIApplicationSceneManifest" in p.data), None)
            adopted.setdefault("scene_manifest", Adopted(
                "scene_manifest", "Scene lifecycle", "UIApplicationSceneManifest declared (required with Xcode 27)",
                p.rel if p else facts.pbxprojs[0].rel,
                _line_of(p.text, "UIApplicationSceneManifest") if p else 1))
        elif facts.has_app_delegate and not facts.has_scene_delegate and not facts.has_swiftui_app:
            emit("DUO-009", anchor_rel, anchor_line,
                 "no UIApplicationSceneManifest and no UIWindowSceneDelegate found (UIApplicationDelegate present)")
        # DUO-010 launch screen.
        has_launch = any(k in p.data for p in app_plists for k in ("UILaunchScreen", "UILaunchStoryboardName")) or \
            _truthy(pbx_settings.get("INFOPLIST_KEY_UILaunchScreen_Generation", "NO")) or \
            "INFOPLIST_KEY_UILaunchStoryboardName" in pbx_settings
        if not has_launch:
            emit("DUO-010", anchor_rel, anchor_line, "no UILaunchScreen / UILaunchStoryboardName key found")
        # DUO-019 Xcode version proxy.
        for p in facts.pbxprojs:
            if p.last_upgrade is not None and p.last_upgrade < 2710:
                note = " (code already references #available(iOS 27.1, *))" if facts.has_available_271 else ""
                emit("DUO-019", p.rel, _line_of(p.text, "LastUpgradeCheck"), f"LastUpgradeCheck = {p.last_upgrade}{note}")
    # DUO-020 Catalyst guard.
    if any(p.catalyst for p in facts.pbxprojs):
        for rel, (line, guarded) in sorted(facts.api271_files.items()):
            if not guarded:
                emit("DUO-020", rel, line, "iOS 27.1-only API used; SUPPORTS_MACCATALYST = YES; no targetEnvironment(macCatalyst) guard")
    # DUO-021 WKWebView.
    if facts.webview_files:
        rel, line = facts.webview_files[0]
        emit("DUO-021", rel, line, f"WKWebView referenced in {len(facts.webview_files)} file(s)")
    # DUO-03x frameworks.
    for rule_id, (rel, line, snippet) in sorted(facts.framework_hits.items()):
        emit(rule_id, rel, line, snippet)


# --------------------------------------------------------------------------- #
# Directory walk
# --------------------------------------------------------------------------- #

def _kind_of(name: str) -> Optional[str]:
    if name.endswith(".swift"):
        return "swift"
    if name.endswith((".m", ".mm", ".h")):
        return "objc"
    return None


def audit(root: str, ignore: Sequence[str] = ()) -> Tuple[List[Finding], List[Adopted], int]:
    """Scan ``root``; returns (findings, adopted, files_scanned)."""
    root = os.path.abspath(root)
    facts = ProjectFacts()
    findings: List[Finding] = []
    adopted: Dict[str, Adopted] = {}
    scanned = 0

    def ignored(rel: str) -> bool:
        return any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(os.path.basename(rel), g) for g in ignore)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.endswith(".xcassets"))
        rel_dir = os.path.relpath(dirpath, root)
        is_test_dir = any(part.endswith(("Tests", "UITests")) for part in rel_dir.split(os.sep))
        for name in sorted(filenames):
            rel = os.path.normpath(os.path.join(rel_dir, name))
            if ignored(rel):
                continue
            kind = _kind_of(name)
            is_plist = name.endswith(".plist") and "Info" in name
            is_pbx = name == "project.pbxproj"
            is_fw = name in ("package.json", "Podfile", "pubspec.yaml", "ProjectSettings.asset", "ProjectVersion.txt") \
                or name.startswith("capacitor.config.")
            if not (kind or is_plist or is_pbx or is_fw):
                continue
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
                with open(path, "rb") as fh:
                    raw = fh.read()
            except OSError:
                continue
            scanned += 1
            if is_plist:
                scan_plist(rel, raw, facts)
                continue
            text = raw.decode("utf-8", "replace")
            if is_pbx:
                scan_pbxproj(rel, text, facts)
            elif is_fw:
                scan_framework_file(rel, name, text, facts)
            elif kind and not (is_test_dir or _RX["test_file"].search(name)):
                scan_source(rel, text, kind, facts, findings, adopted)
    project_findings(facts, findings, adopted)
    findings.sort(key=lambda f: (SEVERITIES.index(f.severity), f.rule_id, f.file, f.line))
    return findings, sorted(adopted.values(), key=lambda a: a.name), scanned


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

NEXT_STEPS = (
    "1. Run Apple's resizability check: in Xcode 27.1 ask the coding assistant to \"get my app ready for "
    "iPhone Duo\" (App Resizability skill), or export it for other agents with `xcrun agent skills export`.",
    "2. Replace device assumptions: UIScreen.main, orientation and idiom checks, hard-coded sizes and "
    "symmetric safe-area math -> size classes, scene/container bounds, per-side safe areas.",
    "3. Test resizing: the Resizable iPhone simulator in Device Hub, iPhone Mirroring resized to extremes, "
    "and the iPhone Duo simulator (Closed / Partially Open / Open buttons; Option-drag the hinge slider).",
    "App Store: iPhone Duo screenshots are optional now (they earn the 'Made for iPhone Duo' badge) and "
    "required from April 2027. Apple's two pages differ on scope: the news post says 'any apps or games "
    "submitted', the specifications page says 'any app using the iOS 27.1 SDK or later'; plan for the "
    "broader reading. Sizes: outer 1398x2034, inner 2007x2853 (portrait; swap for landscape). "
    + SRC_ASC_NEWS + " ; " + SRC_ASC_SHOTS,
)


class Palette:
    def __init__(self, enabled: bool) -> None:
        self.e = enabled

    def _c(self, code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self.e else s

    def sev(self, s: str) -> str:
        return self._c({"P0": "1;31", "P1": "1;33", "P2": "1;36"}.get(s, "0"), f"[{s}]")

    def bold(self, s: str) -> str:
        return self._c("1", s)

    def dim(self, s: str) -> str:
        return self._c("2", s)

    def green(self, s: str) -> str:
        return self._c("32", s)


def summarize(path: str, findings: List[Finding], scanned: int) -> dict:
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITIES}
    return {"path": path, "files_scanned": scanned, "total": len(findings), "by_severity": counts,
            "exit_code": 1 if counts["P0"] else 0, "tool": "duo_audit", "version": __version__}


def render_text(summary: dict, findings: List[Finding], adopted: List[Adopted], color: bool) -> str:
    p = Palette(color)
    c = summary["by_severity"]
    out = [p.bold("iPhone Duo readiness audit"), f"Path: {summary['path']}",
           f"Files scanned: {summary['files_scanned']}    Findings: {summary['total']} "
           f"(P0: {c['P0']}, P1: {c['P1']}, P2: {c['P2']})", ""]
    for sev in SEVERITIES:
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        out.append(p.bold(f"== {sev} ({len(group)}) =="))
        for f in group:
            tag = p.dim(" [heuristic]") if f.heuristic else ""
            out.append(f"{p.sev(f.severity)} {f.rule_id} {f.title}{tag} — {f.file}:{f.line}")
            out.append(f"    > {f.snippet}")
            out.append(f"    Why:    {f.why}")
            out.append(f"    Fix:    {f.fix}")
            out.append(f"    Source: {f.source}")
            out.append("")
    if not findings:
        out.append(p.green("No findings.") + "\n")
    out.append(p.bold("== Already adopted =="))
    out.extend(f"  {p.green('+')} {a.name}: {a.description} — {a.file}:{a.line} (x{a.count})" for a in adopted)
    if not adopted:
        out.append("  (none of the iPhone Duo APIs or size-class patterns were detected)")
    out.append("")
    out.append(p.bold("== Next steps (Apple's three steps) =="))
    out.extend(f"  {s}" for s in NEXT_STEPS)
    return "\n".join(out) + "\n"


def render_markdown(summary: dict, findings: List[Finding], adopted: List[Adopted]) -> str:
    c = summary["by_severity"]
    out = ["## iPhone Duo readiness audit", "",
           f"**Path:** `{summary['path']}`  ", f"**Files scanned:** {summary['files_scanned']}  ",
           f"**Findings:** {summary['total']} (P0: {c['P0']}, P1: {c['P1']}, P2: {c['P2']})", ""]
    for sev in SEVERITIES:
        group = [f for f in findings if f.severity == sev]
        if not group:
            continue
        out.append(f"### {sev} ({len(group)})")
        out.append("")
        for f in group:
            tag = " _(heuristic)_" if f.heuristic else ""
            out.append(f"- [ ] **{f.rule_id} {f.title}**{tag} — `{f.file}:{f.line}`")
            out.append(f"  ```\n  {f.snippet}\n  ```")
            out.append(f"  - **Why:** {f.why}")
            out.append(f"  - **Fix:** {f.fix}")
            out.append(f"  - **Source:** {f.source}")
        out.append("")
    if not findings:
        out.append("_No findings._\n")
    out.append("### Already adopted")
    out.append("")
    out.extend(f"- {a.name}: {a.description} — `{a.file}:{a.line}` (x{a.count})" for a in adopted) or None
    if not adopted:
        out.append("- (none detected)")
    out.append("")
    out.append("### Next steps (Apple's three steps)")
    out.append("")
    out.extend(f"- {s}" for s in NEXT_STEPS)
    return "\n".join(out) + "\n"


def render_json(summary: dict, findings: List[Finding], adopted: List[Adopted]) -> str:
    return json.dumps({"summary": summary, "findings": [asdict(f) for f in findings],
                       "adopted": [asdict(a) for a in adopted]}, indent=2) + "\n"


def render_rules() -> str:
    rows = [(r.id, r.severity, ("heuristic" if r.heuristic else "cited"), r.title, r.source) for r in RULES]
    w = [max(len(row[i]) for row in rows + [("ID", "SEV", "KIND", "TITLE", "SOURCE")]) for i in range(4)]
    fmt = "{:<%d}  {:<%d}  {:<%d}  {:<%d}  {}" % tuple(w)
    lines = [fmt.format("ID", "SEV", "KIND", "TITLE", "SOURCE"), fmt.format(*("-" * n for n in w), "------")]
    lines += [fmt.format(*row) for row in rows]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="duo_audit.py",
                                 description="Audit an iOS project for iPhone Duo (iOS 27.1) readiness.")
    ap.add_argument("path", nargs="?", help="project directory to scan")
    ap.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    ap.add_argument("--min-severity", choices=SEVERITIES, default="P2",
                    help="hide findings less severe than this (P0 is most severe)")
    ap.add_argument("--ignore", action="append", default=[], metavar="GLOB",
                    help="glob of relative paths or basenames to skip (repeatable)")
    ap.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    ap.add_argument("--list-rules", action="store_true", help="print the rule table and exit")
    ap.add_argument("--version", action="version", version=f"duo_audit {__version__}")
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.list_rules:
        sys.stdout.write(render_rules())
        return 0
    if not args.path:
        ap.print_usage(sys.stderr)
        sys.stderr.write("duo_audit.py: error: a project path is required\n")
        return 2
    if not os.path.isdir(args.path):
        sys.stderr.write(f"duo_audit.py: error: not a directory: {args.path}\n")
        return 2
    findings, adopted, scanned = audit(args.path, args.ignore)
    max_idx = SEVERITIES.index(args.min_severity)
    shown = [f for f in findings if SEVERITIES.index(f.severity) <= max_idx]
    summary = summarize(os.path.abspath(args.path), shown, scanned)
    summary["hidden_by_min_severity"] = len(findings) - len(shown)
    if args.format == "json":
        sys.stdout.write(render_json(summary, shown, adopted))
    elif args.format == "markdown":
        sys.stdout.write(render_markdown(summary, shown, adopted))
    else:
        color = sys.stdout.isatty() and not args.no_color and os.environ.get("NO_COLOR") is None
        sys.stdout.write(render_text(summary, shown, adopted, color))
    return summary["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
