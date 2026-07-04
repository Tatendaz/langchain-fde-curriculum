# Phase 4 — Evaluation & observability (build guide)

**Goal:** an evaluation suite for the Phase 3 agent, a CI gate that blocks
regressions, and a production monitoring loop — so that *"how do you know it
works?"* always has a real answer.

This phase is a **build guide**, not a worked example: from here on you write
the code. Phases 0–3 taught you the machine; this phase teaches you to prove
the machine works — the skill that separates "built a demo" from "shipped to
a client," and the single most-probed topic in FDE interviews.

## The mental model

Evaluation splits on *when it runs*:

- **Offline evals** run before you ship: a **dataset** of examples → your
  agent runs each → **evaluators** score the outputs → an **experiment** you
  can compare against the last one. Catches regressions before clients do.
- **Online evals & monitoring** run in production: dashboards (cost, latency,
  error rate), sampled LLM-as-judge scoring on live traffic, and **annotation
  queues** where humans review flagged traces.

The loop that makes both compound: **a bad production trace → annotated →
added to the dataset → a regression test forever.** (This is how the top
agent shops — Sierra calls it the Agent Development Life Cycle — actually
operate.)

## What you build

Work against your Phase 3 agent. Install the evaluator libraries first:

```bash
uv add openevals agentevals
```

### 1 · A dataset (~1 evening)

Create a LangSmith dataset with **12–15 examples** covering:

- **Policy questions with reference answers** (from `KB_DOCS`): *"How many
  PTO days roll over?"* → reference: *"up to 5 days."* Include at least one
  question whose wording shares no keywords with the source chunk.
- **Expected-trajectory cases:** inputs where you know which tools should
  run (e.g. a PTO question should call `search_knowledge_base`, not answer
  from the model's guess).
- **Out-of-scope / adversarial cases:** *"What's our policy on office
  jetpacks?"* (correct behavior: say the KB doesn't cover it — not
  hallucinate) and one prompt-injection attempt via a tool result.

Build it with the SDK (`Client().create_dataset(...)` +
`create_examples(...)`) so it's reproducible from a script checked into
`phase4/` — datasets built by hand in the UI die with the UI. Docs:
[LangSmith datasets](https://docs.langchain.com/langsmith/manage-datasets).

### 2 · Evaluators (~2 evenings)

Three kinds, because they catch different failures:

- **Correctness (LLM-as-judge):** `create_llm_as_judge` from
  [`openevals`](https://github.com/langchain-ai/openevals) with its
  `CORRECTNESS_PROMPT`, judging output vs reference answer. Use your
  strongest available model as judge — never a weaker one than the agent.
- **Groundedness (RAG-specific):** judge whether the answer is supported by
  the *retrieved chunks* (openevals has RAG helpers) — this catches the
  agent answering plausibly from parametric memory while ignoring retrieval.
- **Trajectory:** `create_trajectory_match_evaluator` from
  [`agentevals`](https://github.com/langchain-ai/agentevals) — assert the
  right tools ran (start with `trajectory_match_mode="superset"`; `strict`
  breaks on harmless reordering). Right answer via the wrong path is a
  latent bug: it's luck, cost, or a security problem waiting.

Sanity-check the judge itself: label 5 outputs yourself first, then confirm
the judge agrees with you on at least 4 — **an unaligned judge is worse than
no judge**, because it launders wrong answers into green dashboards.

### 3 · Run experiments (~1 evening)

Run the suite with `evaluate()` ([docs](https://docs.langchain.com/langsmith/evaluation)),
then change something real — retrieval `k` from 2→4, a different `MODEL`, a
reworded system prompt — and run it again. Open both experiments side by side
in LangSmith and find: what improved, what regressed, what it did to latency
and tokens. That comparison view is the artifact clients buy.

### 4 · The CI regression gate (~1 evening)

A pytest test (marked so it only runs when secrets are present) that runs the
eval suite and **fails below thresholds** you choose, e.g. correctness ≥ 0.8
and trajectory ≥ 0.9:

```python
scores = run_eval_suite()          # wraps evaluate(...)
assert scores["correctness"] >= 0.80
assert scores["trajectory_superset"] >= 0.90
```

Wire it into GitHub Actions on PRs. Two practical rules: pin `temperature=0`
everywhere to reduce flake, and gate on *bands* not exact scores — an eval
suite that cries wolf gets deleted within a month.

### 5 · The production loop (~1 evening)

- Run your agent ~15 times with varied real-ish questions to generate
  traffic.
- In LangSmith: check the built-in **cost / latency / error dashboards**, set
  up an **annotation queue**, review 5 traces, annotate at least one genuine
  failure.
- **Close the loop:** convert that annotated failure into a new dataset
  example and re-run the experiment. You have now done, end to end, the
  thing this entire phase exists to teach.

## Deliverable — definition of done

- [ ] `phase4/` contains a dataset-builder script, evaluator definitions, and
      an eval-runner — reproducible by `uv run`, not UI clicks.
- [ ] Dataset has ≥ 12 examples including reference answers, ≥ 2
      expected-trajectory cases, and ≥ 2 out-of-scope/adversarial cases.
- [ ] Correctness + groundedness + trajectory evaluators all run in one
      `evaluate()` suite.
- [ ] Two experiments exist in LangSmith with a config change between them,
      and you can articulate the difference in one sentence.
- [ ] A CI job fails when scores drop below your thresholds (prove it once by
      deliberately breaking the system prompt).
- [ ] One production failure went trace → annotation → dataset example.

## Phase gate — pass this before Phase 5

Write your answers *before* expanding the blocks. This gate also re-tests
two earlier phases — that's deliberate spaced review, not filler.

### 1 · Concept check *(closed book)*

**Q1.** Offline and online evaluation — when does each run, and name one
failure class each catches that the other structurally can't.

<details><summary>Answer</summary>

Offline runs pre-ship against a fixed dataset; online runs on live
production traffic. Offline catches **regressions before users see them**
(you control inputs and have references to compare against) but can't catch
what it doesn't contain: the real, shifting input distribution. Online
catches **drift and novel failure modes** — questions you never thought to
test, cost/latency creep, degradation after a provider model update — but
has no ground-truth references, so it leans on reference-free judges,
metrics, and human annotation. You need both; each feeds the other (online
failures become offline examples).

</details>

**Q2.** Your agent got the right final answer, but the trajectory evaluator
failed the run. Why is that still a bug worth failing? Give two concrete
reasons.

<details><summary>Answer</summary>

Because the *process* is the product in an agent. Concretely: (1) it may
have answered from parametric memory instead of calling
`search_knowledge_base` — right today on your test question, wrong the day
the policy changes, and ungrounded for every question the model doesn't
happen to know; (2) wrong paths have costs even when outputs look right —
skipped approval gates (safety), redundant tool calls (latency/tokens), or
reliance on a lucky guess that won't transfer. Trajectory evals turn "it
happened to work" into "it works the way we designed."

</details>

**Q3.** What's the biggest failure mode of LLM-as-judge evaluation, and what
did you do in this phase to protect against it?

<details><summary>Answer</summary>

The judge being confidently miscalibrated — systematically accepting wrong
answers (or rejecting right ones), which *launders* failures into green
dashboards. Protection: align the judge with human labels — label a handful
of outputs yourself, check agreement, and tune the judge prompt (or model)
until it matches; keep spot-checking as the system evolves. Secondary
hygiene: use a strong judge model, give it a rubric and the reference
answer, and never let the agent's own model grade itself as the sole signal.

</details>

**Q4.** Where do the best new dataset examples come from once you're in
production, and what's the mechanism that gets them there?

<details><summary>Answer</summary>

From real failures. Production traces get flagged (low judge score, negative
user feedback, or sampling), land in an **annotation queue**, a human
reviews and annotates, and the annotated trace is added to the dataset as a
new example — where it becomes a regression test that runs on every change
forever. Hand-written examples start the dataset; production failures grow
it into something no competitor can copy, because it encodes *this client's*
actual distribution.

</details>

**Q5.** *(Review — Phase 2.)* Your CI eval job re-runs an agent that uses
`interrupt()` approval gates. Why must any side effect in a gated node sit
*after* the `interrupt()` call?

<details><summary>Answer</summary>

Because resuming re-executes the node **from the top** — `interrupt()`
returns the resume value on replay instead of pausing. Anything before it
runs twice: once before the pause, again on resume. A side effect placed
before the interrupt (a DB write, an email) executes before approval was
granted *and* duplicates on resume. Gate first, act second.

</details>

**Q6.** *(Review — Phase 3.)* A teammate proposes testing long-term memory
by saving a fact in one thread and recalling it in another, both under the
same store namespace `("memories",)`. What will the test prove, and what
production bug will it still completely miss?

<details><summary>Answer</summary>

It proves cross-thread persistence — the Store outlives any single
`thread_id`, unlike the checkpointer. It misses **cross-user leakage**: with
a global namespace every user shares one memory pool, so user B recalls user
A's facts. The namespace needs the tenant key — `("memories", user_id)` with
`user_id` from the auth layer — and your eval suite should include a
two-user isolation test precisely because nothing else will catch it.

</details>

### 2 · Apply it — an FDE scenario

> Your client's provider announces the model behind your agent is being
> deprecated in 30 days; its replacement is "better on benchmarks." The
> client asks: *"Will anything break?"* Walk through what you actually do.

<details><summary>What a strong answer covers</summary>

You don't guess — you run the switch as an **experiment**: point the agent
at the new model, run the full offline suite, and compare experiments side
by side — correctness, groundedness, trajectory, latency, cost per run.
Investigate regressions in the traces (tool-calling formats and stop
behavior often shift between models), fix prompts if needed, re-run until
scores meet the bar, then ship behind the CI gate and watch online metrics
during rollout. The meta-point to say out loud: *this 30-day fire drill cost
an afternoon because the eval suite already existed* — that's what the
client is paying for. Benchmarks measure the vendor's model; your suite
measures *their* workload.

</details>

### ✅ Gate passed?

All DoD boxes ticked, at most one concept miss, scenario answered — tick
Phase 4 in the [progress checklist](../README.md#progress-checklist) and move
to [Phase 5](../phase5/README.md). You now have the artifact that sells
everything else.

## Resources

- [LangSmith evaluation docs](https://docs.langchain.com/langsmith/evaluation) —
  the primary reference for datasets, `evaluate()`, experiments, annotation
  queues.
- [`openevals`](https://github.com/langchain-ai/openevals) ·
  [`agentevals`](https://github.com/langchain-ai/agentevals) — prebuilt
  evaluators; read both READMEs end to end, they're short.
- LangChain Academy: *Introduction to Agent Observability & Evaluations*.
- [Hamel Husain's evals field guide](https://hamel.dev/blog/posts/field-guide/) —
  the error-analysis mindset behind all of this.
