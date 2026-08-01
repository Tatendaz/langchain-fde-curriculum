# Feature: Dependabot auto-merge for patch and minor bumps

**Branch:** ci/dependabot-auto-merge
**Date:** 2026-08-01

## Summary

Adds `.github/workflows/dependabot-auto-merge.yml`. A Dependabot PR that is a
`semver-patch` or `semver-minor` bump is approved and merged without a human;
`semver-major` bumps are left alone. The repo setting `allow_auto_merge` was
turned on alongside this workflow, and "Allow GitHub Actions to create and
approve pull requests" was enabled so the approve step can satisfy the one
required review on `main`.

## Motivation

`main` requires one approving review, so every Dependabot bump — including a
patch bump to a dev-only dependency — sat waiting for a manual click. The
backlog is pure overhead: the 3.11–3.14 matrix in `ci.yml` and both `pr-gate.yml`
policy jobs already tell you whether the bump is safe, and the docs gate
deliberately stands down for `dependabot[bot]` so a bump PR never needs docs
entries.

Major bumps are excluded on purpose. They can carry breaking changes that a
green suite does not catch, so they keep a human in the loop.

## What changed

- **New `.github/workflows/dependabot-auto-merge.yml`.**
  `dependabot/fetch-metadata` (SHA-pinned to v3.1.0) classifies the bump. The
  approve and merge steps are both gated on `update-type` being
  `version-update:semver-patch` or `version-update:semver-minor`.
- **Gated on the PR author, not the actor.** The job condition is
  `github.event.pull_request.user.login == 'dependabot[bot]'`. `github.actor`
  is whoever triggered the run, so a later pusher can change it; the author
  cannot be spoofed. This is the check GitHub's "Automating Dependabot"
  guidance asks for.
- **Merge pinned to the classified commit.** Both merge paths pass
  `--match-head-commit "$HEAD_SHA"`, closing the window where a commit pushed
  after the metadata step could merge under an earlier patch/minor verdict. The
  new commit gets its own `synchronize` run and is re-classified.
- **A fallback for when `--auto` is refused.** `main` has no required *status*
  checks (`required_status_checks` is null), only the review requirement, so
  GitHub can reject `gh pr merge --auto`. The fallback then polls
  `commits/$HEAD_SHA/check-runs` for up to 30 minutes, excludes this job's own
  check run, and refuses to merge if any sibling check concluded as anything
  other than success, neutral, or skipped. Checks that are not formally
  "required" still gate the merge.
- Workflow-level `permissions` are `contents: write`, `pull-requests: write`,
  `checks: read` — Dependabot-triggered runs get a read-only token by default,
  which cannot approve or merge. `concurrency` is keyed on the PR number with
  `cancel-in-progress`, and the job carries `timeout-minutes: 35`.

## Notes

- The approve step is `continue-on-error: true`. If the Actions approval setting
  is ever turned back off, the workflow degrades to "merge when checks pass"
  instead of failing the run.
- Nothing here changes what CI runs. The workflow only decides whether to merge
  after the existing jobs have reported.
- If a merge queue is ever enabled on this repo, revisit the merge step —
  `GITHUB_TOKEN`-driven merges interact differently with queues.
