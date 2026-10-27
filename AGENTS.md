# For coding agents

This repository is a set of Agent Skills for making iOS apps ready for iPhone Duo (iOS 27.1, Xcode 27.1).

- Skills live in `plugins/duo-ready/skills/<name>/SKILL.md`. Read a skill's `SKILL.md` before advising on its topic; it points to `references/` for detail.
- Start with `duo-audit` when a project path is available: `python3 plugins/duo-ready/skills/duo-audit/scripts/duo_audit.py <path> --format markdown`.
- Every rule in this repo cites an Apple source. Keep that property: do not add guidance without a developer.apple.com URL or a Tech Talk ID, and label anything third-party or inferred as such.
- `docs/known-gaps.md` lists what Apple has not published. Say "Apple has not published this" rather than fill a gap.
