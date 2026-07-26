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

1. Fork, branch (see **Branch naming** below), make the change.
2. `uv run pytest` must stay green; if you touch phase 0–3 code, keep the
   pure logic unit-testable offline (no network in tests).
3. Keep each phase folder standalone — someone should be able to link
   directly to any phase.
4. Add the two docs entries (see **Required docs entries**) and open a PR
   describing *what a learner gains* from the change.

## Setting up

You do **not** need Ollama, an OpenAI/Anthropic key, or a LangSmith key to
contribute. `.env.example` describes what you need to *run* a phase, not what
you need to *change* one — the test suite is entirely offline and finishes in
well under a second.

Install [`uv`](https://docs.astral.sh/uv/), then from the repo root:

```bash
uv sync            # create the venv + install dependencies (pytest included)
uv run pytest      # the offline suite — no network, no keys, no model
uvx ruff check .   # the same lint CI runs
```

Python 3.11 or newer (`requires-python = ">=3.11"`). `.python-version` pins
3.12 for local work, but CI runs the suite on **3.11, 3.12, 3.13 and 3.14** —
a change that only works on your interpreter will fail there.

If you change a dependency in `pyproject.toml`, commit the refreshed `uv.lock`
alongside it. CI installs with `uv sync --locked` and fails on a stale lock.

## Branch naming

Name the branch `<type>/<slug>` — `feat`, `feature`, `fix`, `chore`, `docs` or
`refactor`. This is load-bearing, not style: CI strips the `<type>/` prefix,
turns any remaining `/` into `-`, and then looks for docs files carrying that
slug. So `fix/typo-phase1` → slug `typo-phase1`.

> Editing a file through GitHub's web UI creates a branch called `patch-1`.
> That fails the docs gate. Create a properly-named branch instead.

## Required docs entries

Every PR adds **two** files, both named `<YYYY-MM-DD>-<slug>.md`. On branch
`fix/typo-phase1`, opened on 25 July 2026, they are exactly:

```text
docs/features/2026-07-25-typo-phase1.md    # what changed and why
docs/summaries/2026-07-25-typo-phase1.md   # the prompts and steps that produced it
```

The date prefix is the day you open the PR; the slug has to match the branch.
Copy the shape from
[`docs/features/2026-07-05-mastery-gates-2026-refresh.md`](docs/features/2026-07-05-mastery-gates-2026-refresh.md)
and its matching summary. This gate is the most common reason a first-time PR
goes red, so it is worth getting right before you push.

## Does my change need a test?

Yes, by default: **CI fails any PR that changes a `.py` file without changing
a test file.** New behaviour in a worked example is behaviour a learner will
copy, so it gets a test — `tests/` is the reference for what "offline" means
in practice.

The exception is the kind of fix this page asks for at the top: an outdated
API name, a broken command in a docstring, a comment that lies. There is
nothing to assert. Say so in the PR description and a maintainer will apply the
**`skip-coverage-gate`** label, which stands the gate down for that PR. Only a
maintainer can apply it and it stays visible on the PR, so the decision is on
the record rather than hidden in a CI setting.

Markdown-only PRs — sharper gate questions, FDE scenarios, a
`phase6/completions.md` row — never trip this gate at all.

## Checks that must pass

Merging to `main` requires a pull request with every check below green, all
review conversations resolved, and one approving review from the code owner
(@Tatendaz). These are enforced by the `protect-main` branch ruleset, applied
when the change that introduced this file lands — if you are reading this on
that PR itself, treat it as the agreed policy rather than something GitHub is
already blocking on. The required checks:

| Check | What it runs |
|---|---|
| `Tests (py3.11)` … `Tests (py3.14)` | `uv sync --locked` then `pytest`, one leg per Python version |
| `Lint (ruff)` | `ruff check .` |
| `Docs gate (features + summaries)` | the two files above exist and match the branch |
| `New code has new tests` | a `.py` change comes with a test change |

Plus **one approving review from a code owner** (@Tatendaz). You cannot approve
your own pull request — GitHub does not allow it — so every contribution gets a
second pair of eyes before it lands.

If this is your first PR here, your workflow runs sit **pending approval** until
a maintainer clicks "Approve and run". That is GitHub's fork policy, not broken
CI.

## Never in a PR

Secrets, API keys, `.env`. `.gitignore` already covers `.env` and `.env.*`
(keeping `.env.example`) — don't defeat it with `git add -f`.

And the standing rule for tests: **never add a test that needs a key or the
network.** Stub the transport instead; `tests/test_phase1.py` does exactly that
for `fetch_url`, the one tool in the curriculum that makes a real HTTP call. If
a change genuinely needs a live model, mark the test `@pytest.mark.live` — it is
registered in `pyproject.toml`, excluded from PR CI (fork PRs never receive
secrets anyway), and runs only in the manually-dispatched `Live smoke` job.

## Questions

Open a GitHub issue titled `question(phase N): …` — answered questions
regularly graduate into the READMEs.

## License of contributions

Code contributions land under MIT; prose under CC BY 4.0 (see README
"Using or sharing this curriculum").
