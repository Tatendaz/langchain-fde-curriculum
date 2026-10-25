# Session: Security hardening, October 2026

**Branch:** security/hardening-2026-10-25
**Date:** 2026-10-25

## Prompts

1. "PHASE 2 from coordinator (owner approved): read HARDENING.md and do it for
   each of your repos."
2. "Add the auto-merge job from templates/merge-when-clean.yml." (later: v6)
3. "Delete .github/workflows/dependabot-auto-merge.yml in every hardening PR."

## Steps taken

- Wrote `.github/dependabot.yml`; `check-jsonschema` against the schemastore
  Dependabot schema: ok.
- Tried `exclude-newer = "7 days"` in a scratch copy: `uv lock --dry-run`
  printed `Update certifi v2026.10.19 -> v2026.10.18`. Not adopted.
- Added `zizmor.yml` and the merge-when-clean template (v6, sha256
  af7e7bd9...). Removed `dependabot-auto-merge.yml`.
- `zizmor .github/workflows`: no findings. `actionlint`: clean.
  `uv run pytest -q`: passed.

## Decisions

- zizmor 1.31.1 (released 2026-10-15), not the 1.32 release candidate.
- No `.coderabbit.yaml` change: Dependabot PRs need CodeRabbit's review so
  merge-when-clean can merge them.
