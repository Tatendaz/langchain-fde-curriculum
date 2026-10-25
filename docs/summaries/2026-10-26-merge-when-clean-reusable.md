# Session: merge-when-clean calls the shared workflow

**Branch:** security/merge-when-clean-reusable
**Date:** 2026-10-26

## Prompt
> Replace the copy in each consumer repo with a short caller pinned to
> `@merge-when-clean-v1`, and allow that one first-party ref in zizmor.

## Steps
- Replaced `.github/workflows/merge-when-clean.yml` with the caller. Kept `.github/merge-hold-paths`.
- Added `.github/zizmor.yml` with a `ref-pin` policy for `Tatendaz/coderabbit-failover/*`.
- actionlint and zizmor clean locally.
