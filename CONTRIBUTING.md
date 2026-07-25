# Contributing

Thanks for improving the curriculum. Ground rules keep it teachable:

## What's welcome

- **Fixes** — broken commands, outdated API names or product names (the
  ecosystem renames things; flag the source), unclear wording.
- **Sharper gate questions** — each concept question should target one
  specific misconception and have a hidden answer that settles it. Questions
  that can be answered by pattern-matching the question text are out.
- **Better FDE scenarios** — grounded in things clients/interviewers
  actually ask.
- **Your capstone** — add a row to `phase6/completions.md`.
- **Your solutions to phases 4–6** — keep them in your fork and link them
  from the completions wall, rather than PRing solution code into this repo.
  Phases 4–6 are build guides on purpose: the struggle is the curriculum.

## How

1. Fork, branch, make the change.
2. `uv run pytest` must stay green; if you touch phase 0–3 code, keep the
   pure logic unit-testable offline (no network in tests).
3. Keep each phase README self-contained *as a document* — someone should be
   able to link directly to any phase and follow it without the others. (The
   *code* does build up: `phase2/agent.py` imports Phase 1's tools, and phases
   4–6 work against your Phase 3 agent. That's fine; the prose is what has to
   stand alone.)
4. **Add the two docs entries the PR gate requires** — see below.
5. Open a PR describing *what a learner gains* from the change.

## The PR gate

`.github/workflows/pr-gate.yml` runs on every PR into `main` and has three
jobs. The first one catches people by surprise, so: **a PR with no
`docs/features/` and `docs/summaries/` entry is hard-failed**, whatever else
is in it.

| Job | What it does | How to satisfy it |
|---|---|---|
| Docs gate | Requires `docs/features/*<slug>.md` **and** `docs/summaries/*<slug>.md` | Add both, named `<YYYY-MM-DD>-<slug>.md` |
| Tests | `uv sync --frozen` then `uv run pytest -q` | Keep the suite green; re-run `uv lock` if you touch `pyproject.toml` |
| New code has new tests | Fails if source files changed and no test file did | Add or update a test under `tests/` |

The **slug** is your branch name with a leading `feat/`, `fix/`, `chore/`,
`docs/` or `refactor/` stripped and remaining `/` turned into `-`. So branch
`docs/readme-slim` → slug `readme-slim` → `docs/features/2026-07-25-readme-slim.md`.
Copy the shape of the entries already in those folders: the feature file says
what changed and why, the summary file records the prompts, steps and
decisions.

## Questions

Open a GitHub issue titled `question(phase N): …` — answered questions
regularly graduate into the READMEs.

## License of contributions

Contributions land under the repo's [MIT license](LICENSE), which by its own
wording covers "the Software and associated documentation files" — the code
*and* the prose.
