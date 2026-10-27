#!/usr/bin/env python3
"""Tests for duo_audit.py. Run from the skill directory:

    python3 -I scripts/test_duo_audit.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)  # -I does not add the script directory

import duo_audit  # noqa: E402

SCRIPT = os.path.join(HERE, "duo_audit.py")
BAD = os.path.join(HERE, "fixtures", "BadApp")
GOOD = os.path.join(HERE, "fixtures", "GoodApp")
ALL_RULE_IDS = {r.id for r in duo_audit.RULES}


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True)


class RuleTableTests(unittest.TestCase):
    def test_ids_unique_and_well_formed(self):
        ids = [r.id for r in duo_audit.RULES]
        self.assertEqual(len(ids), len(set(ids)))
        for r in duo_audit.RULES:
            self.assertRegex(r.id, r"^DUO-\d{3}$")
            self.assertIn(r.severity, duo_audit.SEVERITIES)
            self.assertTrue(r.title and r.why and r.fix and r.source)

    def test_every_cited_rule_points_at_apple_material(self):
        for r in duo_audit.RULES:
            if r.source == duo_audit.SRC_HEURISTIC:
                self.assertTrue(r.heuristic, r.id)
                continue
            self.assertTrue("developer.apple.com" in r.source or "Tech Talk 1114" in r.source, r.id)

    def test_patterns_compile(self):
        for r in duo_audit.RULES:
            for pat in (r.pattern, r.veto, r.confirm, r.veto_window):
                if pat:
                    duo_audit.rx(pat)
        for _, _, _, pat in duo_audit.ADOPTED_PATTERNS:
            duo_audit.rx(pat)

    def test_list_rules_cli(self):
        res = run_cli("--list-rules")
        self.assertEqual(res.returncode, 0)
        for r in duo_audit.RULES:
            self.assertIn(r.id, res.stdout)
        self.assertIn("heuristic", res.stdout)


class BadAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.adopted, cls.scanned = duo_audit.audit(BAD)
        cls.by_rule = {}
        for f in cls.findings:
            cls.by_rule.setdefault(f.rule_id, []).append(f)

    def test_every_rule_fires_at_least_once(self):
        missing = ALL_RULE_IDS - set(self.by_rule)
        self.assertFalse(missing, f"rules never triggered by BadApp: {sorted(missing)}")

    def test_has_p0_and_exit_code(self):
        self.assertTrue(any(f.severity == "P0" for f in self.findings))
        self.assertEqual(duo_audit.summarize(BAD, self.findings, self.scanned)["exit_code"], 1)

    def test_suppressed_file_is_clean(self):
        offenders = [f for f in self.findings if f.file.endswith("Suppressed.swift")]
        self.assertEqual(offenders, [], [(f.rule_id, f.line, f.snippet) for f in offenders])

    def test_objc_detections(self):
        objc = {f.rule_id for f in self.findings if f.file.endswith("Legacy.m") or f.file.endswith("Legacy.h")}
        for rid in ("DUO-001", "DUO-002", "DUO-004", "DUO-005", "DUO-011", "DUO-013",
                    "DUO-015", "DUO-016", "DUO-017", "DUO-018", "DUO-023"):
            self.assertIn(rid, objc, rid)

    def test_plist_and_pbxproj_findings_point_at_lines(self):
        self.assertTrue(all(f.line > 0 for f in self.by_rule["DUO-007"] + self.by_rule["DUO-008"]))
        self.assertIn("LastUpgradeCheck = 2600", self.by_rule["DUO-019"][0].snippet)
        self.assertIn("27.1", self.by_rule["DUO-019"][0].snippet)  # notes #available(iOS 27.1 usage

    def test_scale_rule_does_not_double_fire_as_screen_main(self):
        scale_lines = {(f.file, f.line) for f in self.by_rule["DUO-002"]}
        main_lines = {(f.file, f.line) for f in self.by_rule["DUO-001"]}
        self.assertFalse(scale_lines & main_lines)

    def test_framework_rules_cite_config_files(self):
        self.assertTrue(self.by_rule["DUO-030"][0].file in ("package.json", "Podfile"))
        self.assertEqual(self.by_rule["DUO-031"][0].file, "pubspec.yaml")
        self.assertEqual(self.by_rule["DUO-032"][0].file, "capacitor.config.ts")
        self.assertIn("ProjectSettings", self.by_rule["DUO-033"][0].file)

    def test_heuristic_flag_propagates(self):
        self.assertTrue(all(f.heuristic for f in self.by_rule["DUO-017"]))
        self.assertFalse(any(f.heuristic for f in self.by_rule["DUO-001"]))


class GoodAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.adopted, cls.scanned = duo_audit.audit(GOOD)

    def test_no_findings(self):
        self.assertEqual(self.findings, [], [(f.rule_id, f.file, f.line, f.snippet) for f in self.findings])

    def test_adopted_detected(self):
        keys = {a.key for a in self.adopted}
        for k in ("size_classes", "display_scale", "reserved_regions", "arrangement", "hinge",
                  "scene_accessory", "vertical_bars", "camera_direction", "scene_window",
                  "availability", "geometry", "scene_manifest"):
            self.assertIn(k, keys, k)
        self.assertGreaterEqual(len(self.adopted), 5)

    def test_exit_code_zero(self):
        self.assertEqual(duo_audit.summarize(GOOD, self.findings, self.scanned)["exit_code"], 0)


class PreprocessTests(unittest.TestCase):
    def _scan(self, swift: str):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "A.swift"), "w") as fh:
                fh.write(swift)
            findings, _, _ = duo_audit.audit(tmp)
        return findings

    def test_comment_only_match_ignored(self):
        self.assertEqual(self._scan("// let w = UIScreen.main.bounds.width\nlet x = 1\n"), [])
        self.assertEqual(self._scan("/* UIScreen.main\n   .bounds */ let x = 1\n"), [])

    def test_debug_block_ignored_but_else_branch_scanned(self):
        src = "#if DEBUG\nlet a = UIScreen.main.bounds\n#else\nlet b = UIScreen.main.bounds\n#endif\n"
        found = self._scan(src)
        self.assertEqual([(f.rule_id, f.line) for f in found], [("DUO-001", 4)])

    def test_non_debug_conditional_still_scanned(self):
        found = self._scan("#if !targetEnvironment(macCatalyst)\nlet a = UIScreen.main.bounds\n#endif\n")
        self.assertEqual(len(found), 1)

    def test_inline_suppression_specific_and_blanket(self):
        self.assertEqual(self._scan("let s = UIScreen.main.scale // duo-audit: ignore DUO-002\n"), [])
        # Suppressing a different rule must not silence the match.
        found = self._scan("let s = UIScreen.main.scale // duo-audit: ignore DUO-001\n")
        self.assertEqual([f.rule_id for f in found], ["DUO-002"])
        self.assertEqual(self._scan("let s = UIScreen.main.scale // duo-audit: ignore\n"), [])

    def test_previous_line_suppression(self):
        self.assertEqual(self._scan("// duo-audit: ignore\nlet s = UIScreen.main.bounds\n"), [])

    def test_string_with_double_slash_is_not_a_comment(self):
        found = self._scan('let url = "https://x"; let w = UIScreen.main.bounds.width\n')
        self.assertEqual(len(found), 1)

    def test_portrait_only_override_vs_all_orientations(self):
        portrait = "override var supportedInterfaceOrientations: UIInterfaceOrientationMask {\n  return .portrait\n}\n"
        both = "override var supportedInterfaceOrientations: UIInterfaceOrientationMask {\n  return [.portrait, .landscape]\n}\n"
        self.assertEqual([f.rule_id for f in self._scan(portrait)], ["DUO-006"])
        self.assertEqual(self._scan(both), [])

    def test_fill_with_focal_point_not_flagged(self):
        self.assertEqual(self._scan("image.contentMode = .scaleAspectFill // focal point set below\n"), [])
        self.assertEqual([f.rule_id for f in self._scan("image.contentMode = .scaleAspectFill\n")], ["DUO-013"])

    def test_test_files_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "AppTests"))
            for rel in ("AppTests/LayoutTests.swift", "FooTests.swift"):
                with open(os.path.join(tmp, rel), "w") as fh:
                    fh.write("let w = UIScreen.main.bounds\n")
            findings, _, _ = duo_audit.audit(tmp)
        self.assertEqual(findings, [])

    def test_skip_dirs_and_ignore_glob(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "Pods"))
            os.makedirs(os.path.join(tmp, "Vendor"))
            for rel in ("Pods/X.swift", "Vendor/Y.swift", "Z.swift"):
                with open(os.path.join(tmp, rel), "w") as fh:
                    fh.write("let w = UIScreen.main.bounds\n")
            findings, _, _ = duo_audit.audit(tmp, ignore=["Vendor/*"])
        self.assertEqual([f.file for f in findings], ["Z.swift"])


class CliTests(unittest.TestCase):
    def test_exit_codes(self):
        self.assertEqual(run_cli(BAD, "--no-color").returncode, 1)
        self.assertEqual(run_cli(GOOD, "--no-color").returncode, 0)
        self.assertEqual(run_cli().returncode, 2)
        self.assertEqual(run_cli(os.path.join(HERE, "nope-does-not-exist")).returncode, 2)
        self.assertEqual(run_cli(BAD, "--format", "yaml").returncode, 2)

    def test_text_report_structure(self):
        out = run_cli(BAD, "--no-color").stdout
        self.assertIn("iPhone Duo readiness audit", out)
        self.assertIn("Files scanned:", out)
        self.assertRegex(out, r"\[P0\] DUO-001 UIScreen\.main used for layout — Sources/AppDelegate\.swift:\d+")
        self.assertIn("Why:", out)
        self.assertIn("Fix:", out)
        self.assertIn("Source:", out)
        self.assertIn("[heuristic]", out)
        self.assertIn("== Already adopted ==", out)
        self.assertIn("Next steps", out)
        self.assertIn("App Resizability", out)
        self.assertIn("Device Hub", out)
        self.assertIn("1398x2034", out)
        self.assertIn("2007x2853", out)
        self.assertIn("April 2027", out)

    def test_json_report(self):
        res = run_cli(BAD, "--format", "json")
        data = json.loads(res.stdout)
        self.assertEqual(set(data), {"summary", "findings", "adopted"})
        self.assertEqual(data["summary"]["exit_code"], 1)
        self.assertEqual(data["summary"]["by_severity"]["P0"],
                         sum(1 for f in data["findings"] if f["severity"] == "P0"))
        for key in ("rule_id", "severity", "title", "file", "line", "snippet", "why", "fix", "source", "heuristic"):
            self.assertIn(key, data["findings"][0])

    def test_markdown_report(self):
        out = run_cli(BAD, "--format", "markdown").stdout
        self.assertIn("## iPhone Duo readiness audit", out)
        self.assertIn("- [ ] **DUO-001", out)
        self.assertIn("### Already adopted", out)
        self.assertIn("_(heuristic)_", out)

    def test_min_severity_filter(self):
        data = json.loads(run_cli(BAD, "--format", "json", "--min-severity", "P0").stdout)
        self.assertTrue(all(f["severity"] == "P0" for f in data["findings"]))
        self.assertGreater(data["summary"]["hidden_by_min_severity"], 0)
        # P0 findings are still present, so the exit code stays 1.
        self.assertEqual(run_cli(BAD, "--min-severity", "P0").returncode, 1)

    def test_ignore_glob_cli(self):
        data = json.loads(run_cli(BAD, "--format", "json", "--ignore", "Sources/Legacy.*").stdout)
        self.assertFalse(any(f["file"].startswith("Sources/Legacy.") for f in data["findings"]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
