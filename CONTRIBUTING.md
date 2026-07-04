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
3. Keep each phase folder standalone — someone should be able to link
   directly to any phase.
4. Open a PR describing *what a learner gains* from the change.

## Questions

Open a GitHub issue titled `question(phase N): …` — answered questions
regularly graduate into the READMEs.

## License of contributions

Code contributions land under MIT; prose under CC BY 4.0 (see README
"Using or sharing this curriculum").
