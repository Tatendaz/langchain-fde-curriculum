# Feature: CI hardening, gate fixes, and contributor documentation

**Branch:** chore/ci-hardening-and-contributor-docs
**Date:** 2026-07-25

## Summary

Splits CI into a real test/lint pipeline (`ci.yml`, Python 3.11–3.14) and a
policy-only PR gate, fixes two gate defects that made legitimate contributions
unmergeable or let empty ones through, adds the first tests for `fetch_url` and
the other untested pure logic in phases 0–3 (14 → 37 tests), and writes down
the rules an outside contributor previously had to guess.

## Motivation

An audit of `pr-gate.yml` found the gate was simultaneously too strict and too
loose, and undocumented in both directions.

Too strict: `coverage-for-new-code` hard-fails any PR that edits a `.py` file
without editing a test file. On a curriculum repo whose product *is* its worked
examples — and whose CONTRIBUTING.md explicitly invites "outdated API names"
fixes — that makes the single most-invited contribution permanently
unmergeable. A one-word docstring correction in `phase1/agent.py` has no
behaviour to assert, so "Add tests covering the new behavior" is an
unsatisfiable instruction.

Too loose: the docs gate matched `docs/features/*<slug>.md` — an unanchored
*suffix* match. Branch `chore/2026-refresh` was satisfied by the pre-existing
`2026-07-05-mastery-gates-2026-refresh.md`, so a feature branch could merge with
no documentation at all. The same expression demanded a file named
`<date>-feature-new-thing.md` for a `feature/`-prefixed branch (only `feat/` was
stripped), and an empty `GITHUB_HEAD_REF` degraded the pattern to
`docs/features/*.md`, which always matches.

Beyond the gate: CI tested one implicit Python version while `pyproject.toml`
promises `>=3.11`, installed with `--frozen` (which accepts a stale lock),
pinned actions to mutable tags, declared no `permissions`, no `concurrency` and
no `timeout-minutes`, and cached nothing. And `fetch_url` — the only outbound
HTTP path in the repo — had no test at all.

## What changed

- **New `.github/workflows/ci.yml`.** `Tests (py3.11…3.14)` with
  `fail-fast: false`, `astral-sh/setup-uv` with `enable-cache` keyed on
  `uv.lock`, `uv sync --locked` (not `--frozen`, so an unrefreshed lock fails
  loudly), and the suite run with the network poisoned
  (`OLLAMA_BASE_URL=http://127.0.0.1:1`, tracing off) so future network creep
  fails in CI rather than in review. A `Lint (ruff)` job runs
  `uvx ruff@0.14.5 check` — green today at zero cost. A `live-smoke` job is
  `workflow_dispatch`-only, so the one secret-consuming job can never fire on a
  fork PR. Workflow-level `permissions: contents: read`, PR-keyed `concurrency`,
  per-job `timeout-minutes`, all actions SHA-pinned.
- **`pr-gate.yml` is policy-only.** Its `tests:` job is deleted — keeping it
  alongside the matrix would have meant five test runs per PR and two competing
  `Tests` check names to wire into branch protection. Gains `permissions`,
  `concurrency`, `timeout-minutes`, SHA-pinned checkout, and `shell: bash` for
  `pipefail`.
- **Docs gate fixed.** The glob is anchored on the `YYYY-MM-DD` prefix
  (`docs/<dir>/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-<slug>.md`), the
  prefix list is normalised through one `sed` that also covers `feature/`,
  an empty `GITHUB_HEAD_REF` now fails closed, and both directories are checked
  in one step so a contributor missing both learns that in one run.
- **Coverage gate fixed.** A maintainer-applied `skip-coverage-gate` label
  stands the gate down for changes with no assertable behaviour; the failure
  message now names it. `labeled`/`unlabeled` were added to the trigger types,
  because re-running an existing run replays the old payload and would never see
  a newly-applied label. Also fixed: a dead `^test_` regex alternative that let
  a root-level `test_foo.py` count as source, `wc -l` reporting "1 file(s)" for
  an empty list, and a redundant `git fetch` replaced with the PR's `base.sha`.
- **Tests: 14 → 37.** `fetch_url` now has six tests covering status + body,
  2000-character truncation, non-2xx handling, network failure returning an
  error string, and the `timeout=15` / `follow_redirects=True` contract — all
  with `httpx.get` stubbed, no socket opened. Also added: division/negatives,
  the deliberately-unsupported `**`, and division-by-zero for `calculator`;
  `_last_text` in phases 2 and 3; `_wants_tools` for empty and absent
  `tool_calls`; a check that every `_WRITE_TOOLS` name is a registered tool (a
  rename on one side silently disables the human-approval interrupt);
  `_chunk` size and empty-input behaviour; `_office_status` normalisation and
  full office coverage; and `Analysis` rejecting a non-numeric `word_count`.
- **`pyproject.toml`:** registers the `live` marker so `-m live` is first-class.
  No dependency changed, so `uv.lock` is untouched and `uv sync --locked` still
  passes.
- **`CONTRIBUTING.md`:** extended, not rewritten — the existing headings and
  voice are intact. Adds setup (`uv` install, `uv sync`, `uvx ruff check .`),
  the supported-Python statement, branch naming with the `patch-1` warning, the
  docs-gate rule with a worked filename example, the test rule and its new
  exception, the required check names and review policy, and the standing rules
  about `@pytest.mark.live`, `.env`, and refreshing `uv.lock`.
- **`.github/CODEOWNERS`** and **`.github/PULL_REQUEST_TEMPLATE.md`** added.

## Notes

- Phases 4–6 remain deliberately code-free build guides, so no tests were
  written for them. Inventing coverage there would contradict the curriculum.
- `ruff format --check` is still not enabled: it wants to reformat four files
  nobody in this change touched. That needs a one-time formatting commit plus a
  `[tool.ruff] line-length` decision first.
- None of this gates anything until branch protection is enabled on `main` and
  the check names above are marked required.
