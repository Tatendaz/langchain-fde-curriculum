# Phase 6 — Capstone + the FDE layer (build guide)

**Goal:** one end-to-end vertical agent built against a client brief,
delivered the way real engagements (and real FDE take-homes) are delivered:
working system + case study + demo video — plus four drills for the
non-coding skills that actually decide interviews and deals.

Budget ~2 weeks: one for the build (you're assembling phases 2–5, not
inventing), one for the deliverables and drills. **The FDE drills are not
optional garnish** — by reported account of 2025–26 applied-AI loops, the
rounds that trip up candidates who cleared the coding screens are exactly the
ones drilled here: discovery, decomposition, and presenting to non-technical
people. (Reported experience, not a published study — see the README's
[sourcing note](../README.md#the-fde-layer--what-the-market-actually-tests).)

## The capstone

### The brief (default — or bring your own client)

> **From:** Dana Okafor, VP Customer Experience, Meridian Analytics (B2B
> SaaS, ~2,000 customers)
> **Subject:** support copilot?
>
> Our support team is drowning. Most tickets are answered from our help
> docs, our refund/credit policy, or account context the agent has to look
> up. We want an assistant that drafts responses for the easy ones and
> escalates the rest. Two hard requirements from legal: **nothing gets sent
> to a customer without human approval**, and **customer data must not leak
> between accounts**. Can you show us something working this month? Also —
> how would we know it's actually good?

Deliberately underspecified — that's the exercise. Before building, write
down (as if replying to Dana): 5 clarifying questions, your assumed answers,
explicit success criteria, and what's out of scope. That reply is capstone
artifact #1, and the discovery drill below will show you how much you missed.

### Requirements (map: every phase reappears)

- **Knowledge base (Phase 3):** ingest a plausible doc set — write ~10
  short help-center/policy docs, or reuse any real docs you may use freely.
- **A ticket system (Phases 2–3):** a mock ticket API as an **MCP server**
  (extend `phase3/mcp_server.py`): `get_ticket`, `get_customer_context`,
  `draft_reply`, `escalate`. Keep it in-memory; realism lives in the
  *shapes*, not the storage.
- **HITL (Phase 2/5):** `draft_reply` is a write — no reply goes out
  without approval (interrupt or `HumanInTheLoopMiddleware`).
- **Memory + isolation (Phase 3):** per-customer context that provably
  doesn't leak across accounts — include the two-user isolation test.
- **Evals (Phase 4):** dataset ≥ 15 examples (easy tickets, policy edge
  cases, out-of-scope, one injection attempt via ticket text), correctness +
  groundedness + trajectory evaluators, thresholds in CI.
- **Deployed & observed (Phase 5):** your Phase 5 path, streaming,
  middleware hardening, traces + dashboards live.

Alternative briefs if support isn't your vertical (same requirements, same
rigor): an internal IT-helpdesk copilot; a research/analyst agent over
filings or papers with a citations requirement; a contract-review assistant
with a redline-approval gate.

### Deliverable 1 — the case study (one page)

Written for Dana, not for engineers: **Problem → Approach → Architecture**
(one diagram) **→ Results → Limitations → Next steps**. Results means
numbers from your eval suite ("correctness 0.87 on a 15-case suite built
from realistic tickets; 100% of replies gated behind approval"), not vibes.
The **limitations section is mandatory** — in hiring managers' own words,
honest limitations are what separate serious portfolios from tutorial
clones.

### Deliverable 2 — the demo video (3 minutes)

Screen recording, one take is fine:

1. (30s) The problem, in Dana's terms.
2. (90s) The agent answering an easy ticket — **with the LangSmith trace
   open**: retrieval hits, tool calls, the approval pause, resume, streamed
   reply.
3. (30s) **A failure handled well** — the injection attempt caught, or an
   out-of-scope question refused and escalated. Showing recovery builds
   more trust than showing success.
4. (30s) The eval dashboard: "here's how we know it works, and how we'd
   catch it regressing."

### Deliverable 3 — the repo

README with quickstart, architecture diagram, eval instructions, and the
case study linked front and center. A stranger should reach "running agent +
passing evals" in under 15 minutes.

## The FDE drills (~1 evening each)

Each drill produces a written artifact — keep them in `phase6/drills/` in
your fork. They compound: discovery notes feed the case study; the
decomposition doc is your interview rehearsal.

### Drill 1 · The discovery call

Roleplay a 45-minute discovery call about the capstone brief — a friend
plays Dana, or an LLM does (prompt it: *"You are a VP of CX evaluating an
AI vendor. You're enthusiastic but non-technical, you have an unstated
budget ceiling, a failed chatbot pilot last year you only mention if asked
about prior attempts, and a compliance team you defer to on data
questions."*).

Your goal is to leave with: success criteria in the client's words, the
data/systems access map, constraints (legal, budget, timeline), how they'll
measure ROI, and what the failed pilot taught them. **The anti-pattern that
fails real candidates: pitching or demoing instead of asking.** If you
talked more than a third of the time, run it again.

**Artifact:** one-page discovery notes + a follow-up email proposing scope.

### Drill 2 · The decomposition case (timed)

The make-or-break round in FDE loops. Set a 60-minute timer, open a blank
doc, and work this brief (don't design it in advance):

> A logistics company wants an agent that reroutes delayed shipments. Data
> lives in SAP; weather and traffic come from external APIs; 500 warehouse
> managers would use it; a wrong reroute costs real money. They want a
> pilot in 6 weeks.

Produce, in order: clarifying questions you'd ask first · assumptions you'll
proceed on · a **walking skeleton** (the thinnest end-to-end slice you'd
ship in week 1) · the eval plan (how you'd know it works *before* it touches
a real shipment — think shadow mode) · top 3 risks with mitigations. Scoring
yourself: did you ask before designing? Is the skeleton genuinely end to
end? Does the eval plan gate the risky action?

**Artifact:** the timed doc, warts included.

### Drill 3 · The non-technical presentation

Applied-AI take-homes commonly include presenting to a non-technical
audience, and several loops test it live. Prepare a **20-minute
presentation of your capstone for Dana**: the problem, what you built (one
diagram, zero jargon unaccompanied by a translation), a live demo or the
video, "how we know it works" (the eval dashboard, framed as quality
control), limitations and the roadmap, and what you need from her org.
Deliver it to someone real and take questions; recording yourself is the
fallback.

**Artifact:** slides or a memo + one thing you'd change after delivering it.

### Drill 4 · The packaging one-pager

Write the one-pager you'd hand a prospective client: scope of a pilot
engagement · pricing model with a rationale (fixed-scope build vs. monthly
retainer vs. outcome-based — pick one primary and defend it) · the security
FAQ answered preemptively (where data lives, what third parties see, PII
handling, deployment options from SaaS to self-hosted — you wrote these
answers in Phase 5) · handoff: what the client's team gets (runbook, docs,
eval suite, training session) so you're not a hostage vendor.

**Artifact:** the one-pager. This is the document that turns "I have
skills" into "I have a service."

## Final gate — the whole loop

The last gate is cumulative: it checks the curriculum stuck, not just the
capstone. Closed book, written answers, then check.

### 1 · Portfolio check

- [ ] Capstone deployed and demoable *right now*, evals green in CI.
- [ ] Case study, demo video, and repo README done — the trio you can send
      to any prospect or hiring manager cold.
- [ ] All four drill artifacts exist in `phase6/drills/`.
- [ ] Isolation test proves account A's context never reaches account B.

### 2 · The 60-second answers

An FDE gets these questions from executives with no warning. Say each
answer aloud in under a minute — if you stumble, write it out and retry
tomorrow:

1. *"How do you know it works?"*
2. *"What happens when it's wrong?"* (approval gates, escalation, the
   failure→dataset loop)
3. *"Where does our data go?"*
4. *"What does it cost per conversation, and how does that scale?"*
5. *"Why shouldn't we just wait for the model vendors to build this?"*

### 3 · Cumulative concept check *(closed book — one question per phase)*

**Q0.** A structured-output call returns a validated Pydantic object. What
actually enforced the schema — the model or your code — and why does the
distinction matter?

<details><summary>Answer</summary>

Both, in sequence: the request constrains the model toward the schema
(tool/JSON-schema forcing), but the *guarantee* comes from client-side
parsing and Pydantic validation — the model's output is a claim, the
validation is the contract. It matters because downstream systems consume
the object; when the model drifts, you want a loud validation error at the
boundary, not silently malformed data in a database.

</details>

**Q1.** Why does an agent loop terminate at all — what's the structural
stop condition, and what are the two failure modes on either side of it?

<details><summary>Answer</summary>

The loop ends when the model's message contains no tool calls. Fail one
way: the model stops too early (no tools, no useful text — the empty-answer
bug). Fail the other: it never stops calling tools (loops, cost blowups) —
which is why production adds call limits. The stop condition is structural,
so both failures are prompt/guardrail problems, not framework problems.

</details>

**Q2.** A pending human approval survives a server restart. Name the two
mechanisms that make that true.

<details><summary>Answer</summary>

`interrupt()` pauses by **checkpointing** the graph's exact state, and a
**durable checkpointer** (Postgres) stores that checkpoint outside the
process keyed by `thread_id`. Resume loads the checkpoint — on any replica —
and replays the node, with `interrupt()` returning the resume value. Note
the split: *any* checkpointer enables pause/resume, but an in-memory one
dies with the process — **durability across restarts is specifically what
Postgres adds**. Pause = persist; that's why no checkpointer means no
interrupts.

</details>

**Q3.** Checkpointer, Store, vector store: one sentence each on what it
remembers and for how long.

<details><summary>Answer</summary>

Checkpointer: the conversation state of one thread, for the life of that
thread. Store: durable facts across all threads (namespaced — per user, if
you did it right), until deleted. Vector store: your knowledge corpus as
embeddings for semantic retrieval — updated when the docs change, not by
the conversation.

</details>

**Q4.** Your eval suite scores 0.9 correctness. Give two distinct reasons
that number could be lying to you.

<details><summary>Answer</summary>

(1) **Judge miscalibration** — an unaligned LLM-as-judge accepting wrong
answers; you spot-check against human labels to keep it honest.
(2) **Dataset unrepresentativeness** — 0.9 on hand-written easy cases says
little about production's distribution; datasets must grow from real
annotated failures. (Also acceptable: right answers via wrong trajectories,
which correctness alone never sees.)

</details>

**Q5.** Why is "the app tier is stateless" the load-bearing sentence in
your scaling story — and name the two bottlenecks that sentence does *not*
solve.

<details><summary>Answer</summary>

Because all state lives in Postgres (checkpoints, store) and LangSmith
(traces), replicas are interchangeable — HPA can add pods and any pod can
serve any thread. It does not solve: **model-provider rate limits/latency**
(needs routing, fallbacks, caching) and **the database itself** (pooling,
sizing) — in practice your ceiling is almost never CPU.

</details>

**Q6.** You've shipped. The client asks for three things that would make
this agent *better next quarter*. What's the defensible answer?

<details><summary>Answer</summary>

Grow the eval dataset from production annotation queues (every failure
becomes a test); use online scores to find and fix the top failure clusters
(retrieval gaps, missing tools, prompt fixes — verified by experiment
comparison); and only then expand scope (new intents/tools) behind the same
gates. Improvement is the eval loop run continuously — not a bigger model
next quarter. If they push for features first, the dashboard is how you
negotiate: "here's what failing looks like today; here's what that costs."

</details>

### ✅ Curriculum complete

Tick Phase 6. You can now design, build, evaluate, deploy, and *sell* a
production agent — and you have the artifacts to prove all five verbs.
Add your capstone to [completions.md](completions.md) (PRs welcome), share
the case study, and go take a discovery call for real.
