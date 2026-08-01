# Session: Dependabot auto-merge workflow

**Branch:** ci/dependabot-auto-merge
**Date:** 2026-08-01

## Prompts

1. "Dependabot PRs are piling up across my repos waiting on a review I always
   give anyway — set up auto-merge."
2. "Roll the hardened template out to the active repos, including
   langchain-fde-curriculum."

## Steps taken

- Wrote the workflow once as a template in
  `Tatendaz/Quant_Backtest_Platform` and reviewed it there with the CodeRabbit
  CLI before replicating it, so the same review did not have to be spent per
  repo. Two majors came back: a TOCTOU window between classifying the bump and
  merging it (fixed with `--match-head-commit`), and a caveat about
  `GITHUB_TOKEN` merges under merge queues (not applicable — no queues on these
  repos, noted for later).
- Inspected this repo before writing anything: `allow_auto_merge` was `false`,
  `allow_squash_merge` `true`, and `main`'s protection had
  `required_pull_request_reviews` with one approving review and
  `required_status_checks: null`.
- Enabled `allow_auto_merge` on the repo, and set
  `can_approve_pull_request_reviews` on the Actions workflow permissions so the
  approve step can clear the review requirement. `default_workflow_permissions`
  was passed through unchanged as `read`.
- Read `pr-gate.yml` to derive what this PR itself owes the docs gate: branch
  `ci/dependabot-auto-merge` has its `ci/` prefix stripped to slug
  `dependabot-auto-merge`, so this file and its `docs/features` counterpart are
  named `2026-08-01-dependabot-auto-merge.md`.
- Applied the whole change through the GitHub API — branch ref, three file
  PUTs, PR, merge — with no local clone.

## Decisions

- **Patch and minor only.** A major bump is where a green suite is least
  informative: the breaking change is often in a code path the curriculum's
  offline tests never exercise. Those stay manual.
- **Author check over actor check.** `github.actor` is the account that
  triggered the current run, so a human pushing to a Dependabot branch becomes
  the actor. `pull_request.user.login` stays `dependabot[bot]` for the life of
  the PR.
- **Kept the sibling-check fallback even though this repo has branch
  protection.** The protection here requires a review but no status checks, so
  `--auto` has no required check to arm against and GitHub can refuse it. The
  fallback is what actually makes CI gate the merge on this repo.
- **`continue-on-error` on the approve step, not on the merge step.** A failed
  approval should leave the PR open for a human; a failed merge should be loud.
- No per-repo CodeRabbit review was requested for this PR — the template was
  reviewed centrally, and the PR description carries `@coderabbitai ignore`.
