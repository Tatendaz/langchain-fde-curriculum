# Feature: merge-when-clean calls the shared workflow

**Branch:** security/merge-when-clean-reusable
**Date:** 2026-10-26

## Summary
`.github/workflows/merge-when-clean.yml` is now a short caller of
`Tatendaz/coderabbit-failover/.github/workflows/reusable-merge-when-clean.yml@merge-when-clean-v1`.

## Why
The job's logic lived in a copy in every repo, and each fix was copied by hand. The shared
workflow has tests, and a fix now ships with one merge and a tag move in coderabbit-failover.
This also moves the repo from template v6 to v7: a bad or unreadable `.github/merge-hold-paths`
now fails the run, a failed read of one PR fails the run, and Dependabot release notes no longer
mark a minor update as major.

## What changed
- `merge-when-clean.yml`: same triggers, permissions and `status` filter; the job is `uses:`.
- `.github/zizmor.yml`: allows a tag pin for `Tatendaz/coderabbit-failover/*` only.
