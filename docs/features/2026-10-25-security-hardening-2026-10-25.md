# Feature: Dependabot cooldown, zizmor in CI, merge when clean

**Branch:** security/hardening-2026-10-25
**Date:** 2026-10-25

## Summary

Adds a Dependabot config with a 7-day cooldown for `uv` and GitHub Actions, a
zizmor job that scans the workflows on every PR, and the owner's
merge-when-clean job. Removes the old Dependabot auto-merge workflow.

## Motivation

The October 2026 supply-chain attacks shipped as new versions of trusted
packages. A 7-day cooldown keeps Dependabot from proposing a release in its
first week, when most bad releases are caught and pulled.
`dependabot-auto-merge.yml` merged Dependabot PRs on green CI with no review;
`merge-when-clean.yml` merges them only after a real review.

## What changed

- `.github/dependabot.yml` (new): `uv` and `github-actions`, monthly,
  `cooldown: default-days: 7`, one group per ecosystem for minor + patch, at
  most 3 open PRs each. Validated against the schemastore Dependabot schema.
- `.github/workflows/zizmor.yml` (new): `pipx run zizmor==1.31.1
  --min-severity high .github/workflows`, read-only token, checkout pinned.
- `.github/workflows/merge-when-clean.yml` (new): the owner's template v6,
  unchanged.
- `.github/workflows/dependabot-auto-merge.yml`: removed.

## Notes

- No `[tool.uv] exclude-newer` cooldown. uv 0.11.21 accepts `"7 days"`, but
  `uv lock --dry-run` with it rolls `certifi` back from 2026.10.19 to
  2026.10.18, the version that still has GHSA-6q48-6c7w-9gw2. It would also
  make `uv sync --locked` in CI depend on the day it runs. Dependabot's
  cooldown covers the same risk for this repo.
- CI already installs with `uv sync --locked`, pins every action to a SHA, and
  runs with `contents: read`; nothing else to lock down.
