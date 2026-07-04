# Phase 5 — Productionization & deployment (build guide)

**Goal:** your agent, hardened and deployed — persistent across restarts,
streaming, autoscaling, secretly-configured, fully traced — plus ready
answers to the enterprise questions that decide deals.

Two halves: **harden** (guardrails + reliability, ~1 evening each) and
**deploy** (pick one of two paths). If you're behind schedule at this point,
take the managed path and reclaim a week — the hardening half is not
skippable.

## Part 1 — Harden the agent

### Reliability & guardrails as middleware (~2 evenings)

In Phase 2 you built a human-approval gate *by hand* with `interrupt()`.
LangChain 1.x packages that pattern — and most other production concerns —
as **middleware** on `create_agent`
([docs](https://docs.langchain.com/oss/python/langchain/middleware)). Now
that you know what's under the hood, use the packaged versions. Add to your
Phase 3 agent:

- **`HumanInTheLoopMiddleware`** — approval on write tools (replaces your
  hand-rolled gate; compare its behavior to yours).
- **`PIIMiddleware`** — detect/redact emails, phone numbers, etc., before
  they reach the model or the trace.
- **`ModelFallbackMiddleware`** + **`ToolRetryMiddleware`** — a fallback
  model when the primary errors, retries with backoff for flaky tools.
- **`ModelCallLimitMiddleware`** / **`ToolCallLimitMiddleware`** — hard caps
  so a looping agent burns cents, not dollars.
- **`SummarizationMiddleware`** — compress old turns as threads grow
  (context engineering's bread and butter).

Then verify each one *in the trace*: force a tool failure, watch the retry;
send a fake phone number, watch the redaction. Middleware you haven't seen
fire is a rumor, not a guardrail.

> Pin your versions. Middleware hook signatures have churned between 1.x
> minors — this repo's lockfile is your friend.

### Prompt-injection defense in depth (~1 evening)

You proved the attack class exists in Phase 1 (hostile web page → tool
call). There is no single fix; production stacks layer:

1. **Least-privilege tools** — the agent gets the narrowest tools that do
   the job; separate read from write.
2. **HITL on writes** — the Phase 2 gate: irreversible actions need a human.
3. **Input/output validation** — schema-validate tool args; bound loops and
   spend with the limit middlewares.
4. **Isolation** — untrusted content (fetched pages, user uploads) is data,
   never instructions: mark it, sandbox tools that touch it, and never let
   it grant new capabilities.

Write these four down in your own words — they reappear in the gate and in
every enterprise security review you'll ever sit.

## Part 2 — Deploy (pick a path)

### Path A · Managed — LangSmith Deployment

*(Formerly "LangGraph Platform" — you'll see both names in the wild.)*
Least ops; the right call for many client engagements.

1. Add a `langgraph.json` pointing at your graph; run **`langgraph dev`**
   for the local dev server and poke your agent in **LangSmith Studio**.
2. Ship with **`langgraph deploy`** (or connect the GitHub repo in the UI).
3. Point [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui) at
   the deployment for an instant streaming front end with HITL support.
4. Know the deployment spectrum for client conversations: cloud SaaS →
   hybrid (their data plane, managed control plane) → fully self-hosted →
   standalone container (just Docker + your Postgres/Redis).

### Path B · DIY — FastAPI + k8s (the moat, if infra is your home turf)

1. **Serve:** a FastAPI app exposing `POST /threads/{id}/messages` that runs
   the graph with `PostgresSaver` (call `.setup()` once) and streams
   responses over **SSE** (`graph.astream(..., stream_mode="updates"`, or
   `"messages"` for tokens). Include approve/reject endpoints that resume an
   interrupted thread via `Command(resume=...)`.
2. **Isolate tenants:** derive `thread_id` and the store namespace from the
   *authenticated* user — the Phase 3 gate lesson, now enforced in an API
   layer.
3. **Containerize:** small image, non-root, config via env vars only.
4. **Deploy to `kind`/`minikube`:** Deployment + Service + Ingress, secrets
   in k8s `Secret`s (never the image), liveness/readiness probes, **HPA**
   with 2+ replicas, Postgres in-cluster or sidecar'd for the exercise.
5. **Prove the properties** (this is the deliverable, not the YAML):
   - kill the pod mid-conversation → same `thread_id` resumes with history
     intact on another replica;
   - kill it while an **approval is pending** → the interrupt survives and
     can be resumed (the Phase 2 payoff, now with real stakes);
   - `hey`/`k6` load → HPA scales out; tokens still stream; traces still
     arrive in LangSmith.

## Deliverable — definition of done

- [ ] Middleware stack live and *witnessed in traces*: one forced tool
      retry, one PII redaction, one fallback or call-limit trigger.
- [ ] Your four prompt-injection layers written down in your own words.
- [ ] Deployed via Path A **or** B, end-to-end traced, streaming to a client
      (Agent Chat UI or `curl -N`).
- [ ] State survives restart: conversation resumes, pending approval
      resumes. (Path A gives you this — verify it anyway.)
- [ ] Secrets out of code and images; config is env-only.
- [ ] Path B only: HPA observed scaling under load.

## Phase gate — pass this before Phase 6

### 1 · Concept check *(closed book)*

**Q1.** In the DIY path, any replica can serve any thread — a pod dies
mid-conversation and another picks it up seamlessly. What architectural
property makes that true, and which single line of Phase 2 code was the
seed of it?

<details><summary>Answer</summary>

The agent is **stateless at the process level**: all conversation state
lives in the checkpointer's Postgres tables keyed by `thread_id`, so any
replica can load any thread's latest checkpoint and continue — pods are
cattle, state is in the database. The seed was compiling the graph with a
checkpointer (`builder.compile(checkpointer=...)`) in Phase 2; swapping
`MemorySaver` for `PostgresSaver` moved that state out of the process,
which is the entire difference between a demo and a horizontally scalable
service.

</details>

**Q2.** Why do agent UIs stream (SSE/websockets) instead of returning the
final answer, and what are the two distinct things worth streaming?

<details><summary>Answer</summary>

An agent run can take tens of seconds across multiple model and tool calls;
a silent spinner that long reads as "broken," and users can't interrupt or
correct course. Streaming fixes perceived latency and enables HITL UX. Two
things to stream: **tokens** (the model's text as it generates —
`stream_mode="messages"`) and **steps/updates** (which node/tool is running
and what it returned — `stream_mode="updates"`), the latter being what lets
a UI show "Searching the knowledge base…" honestly.

</details>

**Q3.** What belongs in middleware versus in the graph itself? Give a rule
and one example of each.

<details><summary>Answer</summary>

**Middleware** wraps the agent loop with cross-cutting policy that isn't
this agent's business logic — retries, fallbacks, PII redaction, call
limits, summarization, generic approval gates. **Graph structure** encodes
the application's own control flow — which tools exist, domain routing
("billing questions go to the billing subgraph"), custom state fields. Rule
of thumb: if you'd want it on *every* agent you ship, it's middleware; if
it defines *this* agent, it's the graph. (You proved you can hand-roll
either in Phase 2 — that's what makes the packaged versions safe to use.)

</details>

**Q4.** *(Review — Phase 1.)* Your deployed agent's `fetch_url` tool reads
arbitrary pages. A security reviewer asks: "so a web page can instruct your
agent?" Answer honestly, then give your layered defense.

<details><summary>Answer</summary>

Honest answer: yes — fetched text enters the model's context, and models
can follow instructions found in data; prompt injection can't be fully
"patched" at the model layer. The defense is layers: least-privilege tools
(read/write separated), human approval on anything irreversible (Phase 2's
interrupt), schema validation and spend/loop limits on tool use, and
treating untrusted content strictly as data (sandboxed, never
capability-granting). The reviewer isn't looking for "it can't happen" —
they're checking you know it *can* and have bounded the blast radius.

</details>

**Q5.** *(Review — Phase 0/4.)* Tracing export is fail-open — a bad
LangSmith key never takes the agent down. Your CI eval gate is fail-closed —
bad scores block the merge. Why are opposite defaults both correct?

<details><summary>Answer</summary>

Because the cost asymmetry flips. In production, observability is a side
channel: losing a trace is cheap, taking the user's request down because a
telemetry endpoint hiccuped is expensive — so fail open. In CI, the whole
point is to stop bad changes: letting a regression through because the eval
errored is expensive, blocking a merge for an hour is cheap — so fail
closed. State the principle once and reviewers relax: *failure handling
follows the cost of being wrong, per path.*

</details>

### 2 · Apply it — an FDE scenario

> An enterprise security review, ten minutes in: *"Where does our data go?
> Which third parties see it? What happens to it if we cancel?"* — and then
> the CTO adds: *"launch is next month; what if traffic is 10× your
> estimate?"*

<details><summary>What a strong answer covers</summary>

**Data path, concretely:** prompts and tool data go to the model provider
(or nowhere off-box, if local/self-hosted models); traces go to LangSmith —
with PII middleware redacting before export, configurable sampling and
retention, and hybrid/self-hosted deployment options if traces must stay in
their cloud; conversation state lives in *their* Postgres. Offer the
spectrum: SaaS → hybrid → self-hosted/standalone container, priced by ops
burden. Cancellation: state is their database; export is a SQL dump.
**10× traffic:** the app tier is stateless so HPA handles replicas; the real
bottlenecks are model-provider rate limits (mitigate with routing, fallbacks,
caching) and Postgres (connection pooling, right-sizing) — and the honest
answer includes "we load-tested at N req/s; here's the trace-backed latency
distribution," because you did that in this phase.

</details>

### ✅ Gate passed?

Tick Phase 5 in the [progress checklist](../README.md#progress-checklist)
and open [Phase 6](../phase6/README.md) — the capstone. Everything from here
is assembly and polish; the hard skills are in place.

## Resources

- [LangSmith Deployment docs](https://docs.langchain.com/langsmith/deployments) —
  cloud / hybrid / self-hosted / standalone container, and the
  [CLI](https://docs.langchain.com/langsmith/cli) (`langgraph dev`,
  `langgraph deploy`).
- [Middleware docs](https://docs.langchain.com/oss/python/langchain/middleware) —
  the full built-in list; skim it so you know what exists before writing
  your own.
- [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui).
- LangChain Academy: *Introduction to LangSmith Deployment*, *Monitoring
  Production Agents*.
