<!--
Thanks for contributing! The checklist below records this repository's
contribution requirements. CI enforces some of them — the tests, the
source-needs-tests rule and the docs entries. The rest (branch naming,
no secrets) a reviewer checks by eye, so a green build does not by itself
mean the checklist is satisfied.
-->

## What this changes

<!-- One or two sentences. What does this do, and why? -->

## What a learner gains

<!-- This is a curriculum. Say what someone working through the phases can now
     do, understand, or stop being confused by. -->

## Checklist

- [ ] **Branch is named `<type>/<slug>`** — e.g. `feat/`, `feature/`, `fix/`, `docs/`,
      `chore/`, `refactor/`. GitHub's web "Edit this file" button creates branches
      named `patch-1`, which fails the docs gate.
- [ ] **Tests pass locally:** `uv sync && uv run pytest`. No Ollama, no API key,
      and no network required — if a change needs any of those, the test is
      marked `@pytest.mark.live`.
- [ ] **Lint passes:** `uvx ruff check .`
- [ ] **Source changes come with test changes.** CI hard-fails a source-only diff.
      If your change genuinely cannot be unit-tested — a comment or docstring fix,
      a renamed upstream API symbol — say why here and a maintainer will apply the
      `skip-coverage-gate` label.
- [ ] **`docs/features/<YYYY-MM-DD>-<slug>.md` exists** describing what changed and why.
- [ ] **`docs/summaries/<YYYY-MM-DD>-<slug>.md` exists** — this repo requires both.
- [ ] **`uv.lock` is refreshed and committed** if `pyproject.toml` dependencies changed.
- [ ] **No secrets, API keys, or `.env` files** are included in the diff.

## Notes for the reviewer

<!-- Anything surprising, any tradeoff you made, anything you want a second opinion on. Delete if not needed. -->
