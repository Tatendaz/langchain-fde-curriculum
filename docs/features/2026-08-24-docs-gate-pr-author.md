# Feature: Docs gate binds to the PR author, not the run actor

**Branch:** ci/docs-gate-pr-author
**Date:** 2026-08-24

## Summary

The `docs-gate` job in `.github/workflows/pr-gate.yml` now stands down when the
pull request *author* is `dependabot[bot]`
(`github.event.pull_request.user.login`), instead of when the run *actor* is
(`github.actor`). Dependabot bumps keep skipping the docs requirement no matter
who last touched the branch.

## Motivation

`github.actor` is whoever triggered the current run. Pressing "Update branch"
on a Dependabot PR starts a new `pull_request: synchronize` run whose actor is
the human who clicked, the skip stops firing, and the gate demands
`docs/features/<date>-dependabot-uv-….md` files a bump PR will never have. (A
plain re-run keeps the original actor; the person re-running only shows up as
`github.triggering_actor`.) That is exactly what happened on #9 (cryptography
49 → 50): the PR went red for a reason that had nothing to do with the change,
and because the `protect-main` ruleset lists the docs gate as a required check,
the merge was blocked until Dependabot recreated the branch.

`dependabot-auto-merge.yml` already binds to the PR author for the same reason;
this brings the docs gate in line with it.

## What changed

- `.github/workflows/pr-gate.yml`: the `docs-gate` condition is now
  `github.event.pull_request.user.login != 'dependabot[bot]'`. The comment
  above it explains why the author, not the actor, is the right handle.
- Nothing else. The coverage job, the checks themselves, and the required-check
  names in the ruleset are untouched.

## Notes

- The author check is also the one GitHub's Dependabot automation guidance
  recommends: a later pusher can change the actor, but not the PR author.
- Human PRs are unaffected — their author is never `dependabot[bot]`, so the
  docs gate still runs and still requires both entries.
