# Production-Grade AI Agents — An FDE Learning Curriculum

> A 6-phase, deliverable-driven curriculum for going from *"I use LLMs"* to
> *"I can design, evaluate, and ship production agents on the LangChain /
> LangGraph / LangSmith stack — and deliver them as a service."*

The LangChain ecosystem moves fast. This curriculum optimizes for the
**durable skills** (agent architecture, evaluation, observability,
productionization) over memorizing today's API surface, and ends each phase in
a **working, traced artifact** rather than tutorial limbo.

---

## Who this is for

Engineers — especially infra / SRE / backend folks — who are comfortable in
Python and *use* LLMs daily, but haven't yet **architected and deployed a
stateful agent to production**. If that's you, the hardest part of shipping
(k8s, observability, reliability, secrets, autoscaling) is already your home
turf. The real gaps are narrower: **agent application architecture, the
LangChain / LangGraph / LangSmith APIs, and LLM-specific evaluation.** This plan
leans into those and treats infra as "you know this — here's the agent-specific
twist."

## Outcome

By the end you can **design, build, evaluate, and deploy a real production
agent**, with a **portfolio capstone + case study** you can show prospects.
That's "client-ready for SMB/startup engagements"; deep-enterprise polish (SOC 2
conversations, heavy multi-tenancy) comes with your first one or two real
projects.

## How to use this repo

- **Sized for evenings.** ~50–60 focused hours, structured as 6 phases. At
  ~8–10 hrs/week that's roughly 6 weeks; if weeks get eaten by other work it
  stretches to ~8–10 calendar weeks without breaking.
- **Every phase ends in a standalone deliverable.** A skipped week shifts the
  calendar, it doesn't break the plan. Those deliverables *become your
  portfolio.*
- **The core spine is `1 → 2 → 4 → 5 → capstone`.** If time gets tight,
  shorten Phase 3's RAG depth and defer multi-agent patterns — never drop the
  spine.
- Track yourself with the [progress checklist](#progress-checklist) at the
  bottom.

## Repo layout

```
.
├── README.md          # this curriculum
├── pyproject.toml     # uv project (dependencies shared across phases)
├── .env.example       # copy to .env and fill in your API keys
├── phase0/            # Phase 0 — traced hello-world (tool call + structured output)
├── phase1/            # Phase 1 — first agent via create_agent (one nested trace)
├── phase2/            # Phase 2 — LangGraph rebuild: persistence + human approval
└── tests/             # offline unit tests for the pure logic in each phase
```

**Getting started:** install [`uv`](https://docs.astral.sh/uv/), then from the
repo root:

```bash
uv sync                              # create the venv + install dependencies
cp .env.example .env                 # then set your Ollama + LangSmith values
uv run python -m phase0.hello_agent  # run the Phase 0 starter
uv run pytest                        # run the tests
```

See [`phase0/README.md`](phase0/README.md) for what Phase 0 does and what to
look for in LangSmith.

---

## Operating principles

1. **Observability-first.** Turn on LangSmith tracing on day one, before you
   write anything interesting. Most learners bolt this on too late.
2. **Every phase ships a deliverable.** No "tutorial limbo." These artifacts are
   your portfolio.
3. **Deployment + reliability is the moat.** Plenty of people "know LangChain."
   Few can ship a stateful, observable, autoscaling agent to k8s. Don't
   under-invest here thinking it's the boring part — it's the differentiator.
4. **Tiered model routing for cost.** Learn the stack model-agnostic, but build
   your cost story around routing by difficulty: a cheap/fast tier for
   routing/eval/classification, a workhorse for the agent loop, a top reasoning
   tier for the hardest steps (e.g. Claude Haiku → Sonnet → Opus).

---

## The curriculum

### Phase 0 — Foundations & mental model · *core* · ~3 evenings

Solidify the API-level model of LLM apps — you use them, now understand them as
primitives.

- Tokens, context windows, temperature, **structured output (Pydantic)**, and
  **tool / function calling** — the bedrock every agent is built on.
- Set up: `uv` (or Poetry), Python 3.11+, a model-provider API key, and a
  **LangSmith account + tracing env vars**.
- **Deliverable:** a traced "hello world" — a chat call that does one tool call
  and returns structured output, fully visible in a LangSmith trace.

### Phase 1 — LangChain core + your first agent · *core* · ~Week 1

- Chat models, messages, prompt templates, **structured output**, **tool
  definition & binding**.
- Just enough **LCEL / Runnables** to compose pipelines — don't rabbit-hole.
- **`create_agent`** (the standard tool-calling agent) — build a ReAct-style
  agent.
- **LangSmith trace-reading as a debugging skill:** runs, threads, latency,
  token counts.
- **Deliverable:** a single agent that calls 2–3 *real* tools/APIs (e.g. a
  search API + a calculator + an HTTP fetch), fully traced.

### Phase 2 — LangGraph: the production agent runtime · *core; the most important build week* · ~Week 2

This is the framework you'll actually ship. It's a state machine — which will
feel natural if you have an infra background.

- `StateGraph`: state schema, reducers, nodes, edges, **conditional routing,
  cycles**.
- **Persistence / checkpointers** (`MemorySaver` → **`PostgresSaver`**),
  threads, short-term memory.
- **Streaming** (tokens, steps, custom events) — table stakes for real UX.
- **Human-in-the-loop:** `interrupt()` + resume — approval gates before an agent
  takes a risky action. Enterprises *require* this.
- **Time-travel / replay** — debugging from state snapshots.
- **Deliverable:** rebuild Phase 1's agent in LangGraph with Postgres
  persistence + one approval interrupt before a "write" action.

### Phase 3 — RAG, memory & tools at production quality · *core; tune depth to time* · ~Week 3

- **RAG pipeline:** loaders → chunking strategies → embeddings → vector store
  (**`pgvector`** if you already operate Postgres) → retrievers → **hybrid
  search + reranking**.
- **Retrieval quality measurement** (recall / precision, faithfulness) — sets up
  Phase 4.
- **Long-term memory** via the LangGraph `Store` (semantic memory across
  sessions).
- **MCP integration** with `langchain-mcp-adapters` — wire MCP servers in as
  agent tools.
- **Deliverable:** an agent with a real knowledge base + long-term memory + one
  MCP-backed tool.

### Phase 4 — Evaluation & observability: the FDE differentiator · *core; do not skip* · ~Week 4

This is what lets you tell a business *"here's proof it works, and here's how
we'll know if it regresses."* It's the SLO mindset applied to agents.

- **LangSmith datasets, experiments, `evaluate()`**.
- **Evaluators:** LLM-as-judge, heuristic / exact-match, pairwise, and
  **trajectory / tool-use evals** (did the agent take the right *steps*, not just
  give the right answer?).
- **Regression testing in CI** (pytest + LangSmith) — gate merges on eval
  scores.
- **Online evaluation + production monitoring:** dashboards, alerts,
  **annotation queues** for human feedback, cost & latency tracking.
- **Deliverable:** an eval suite + a CI gate that blocks regressions + a live
  monitoring dashboard. *This single deliverable is your strongest sales
  asset.*

### Phase 5 — Productionization & deployment · *core; your home turf, your moat* · ~Week 5

- **Guardrails:** prompt-injection defense, PII handling, input/output
  validation, content moderation, tool sandboxing.
- **Reliability:** retries, fallbacks, **model routing**, timeouts, rate limits,
  **prompt caching + semantic caching** for cost/latency.
- **Deployment — two paths, pick per client:**
  - *Fast path:* **LangGraph Platform** (managed or **self-hosted LangGraph
    Server**) — least ops.
  - *DIY path:* **FastAPI + LangGraph + Postgres (checkpointer) + Redis**,
    containerized, **Helm chart on k8s with HPA, secrets, SSE streaming, and
    multi-tenant data isolation**, tracing wired to LangSmith.
- **Deliverable:** your agent deployed to a k8s cluster (local `kind` /
  `minikube` is fine) with persistence, autoscaling, secrets, and end-to-end
  tracing.

### Phase 6 — Capstone + FDE business skills · *core for portfolio* · ~Week 6

- **Capstone:** one end-to-end vertical agent that exercises the *whole* stack —
  LangGraph + RAG + memory + HITL + evals + deployed + monitored. Pick a
  believable use case (customer-support triage, internal-ops copilot, a
  research/analyst agent, a document drafting/review agent).
- **The FDE layer** — the skills that turn this into *a service*, not just a
  skill set. See below.
- **Deliverable:** capstone repo + a one-page case study + a 3-minute demo
  video. This trio *is* your sales kit.

---

## The FDE layer — turning skills into a service

Technical depth gets you a working agent. These get you paid for it.

- **Discovery & scoping** — turning a vague *"can AI do X for us?"* into a
  concrete agent spec with explicit success criteria.
- **ROI / success-metric framing** for non-technical buyers — lean on your
  Phase 4 eval dashboards as proof.
- **Demo-driven delivery** — ship a rough working demo in days, then iterate
  with the client in the loop.
- **Security & compliance conversations** (data residency, PII, SOC 2) —
  enterprises ask early; have answers.
- **Pricing & packaging** — fixed-scope build vs. monthly retainer vs.
  outcome-based.
- **Handoff** — docs, runbooks, and maintainability. (An ops background is a
  selling point here.)

---

## If a week gets eaten by other projects

Don't drop a phase — **shorten Phase 3's RAG depth** and **defer multi-agent
patterns** (supervisor / swarm) to a "later, when a client needs it" backlog.
The non-negotiable spine is **1 → 2 → 4 → 5 → capstone**: build an agent, make
it stateful, prove it works, ship it. Because each phase is self-contained, a
skipped week just shifts the calendar.

---

## Curated resources

*(Free unless noted. The ecosystem moves fast — treat official docs as
primary.)*

- **LangChain Academy** (`academy.langchain.com`) — *Introduction to LangGraph*
  is the single best use of your early hours.
- **DeepLearning.AI short courses** — *AI Agents in LangGraph*, *Functions,
  Tools & Agents with LangChain*, *Long-Term Agentic Memory with LangGraph*.
- **Official docs** — LangGraph (concepts + how-tos) and **LangSmith
  (evaluation section especially)**.
- **LangGraph Studio** — visual agent debugger; install during Phase 2.

## Recommended starter stack

`Python 3.11 + uv` · `langchain` + `langgraph` + a provider integration (e.g.
`langchain-ollama`) · `langsmith` · `pgvector` on Postgres ·
`langchain-mcp-adapters` · `FastAPI` for serving · `pytest` for eval CI ·
`Helm` / k8s for deploy.

---

## Progress checklist

- [x] **Phase 0** — Traced "hello world" (tool call + structured output)
- [x] **Phase 1** — Single agent calling 2–3 real tools, fully traced
- [ ] **Phase 2** — LangGraph rebuild with Postgres persistence + approval interrupt
- [ ] **Phase 3** — Agent with knowledge base + long-term memory + MCP tool
- [ ] **Phase 4** — Eval suite + CI regression gate + monitoring dashboard
- [ ] **Phase 5** — Agent deployed to k8s with persistence, autoscaling, tracing
- [ ] **Phase 6** — Capstone agent + one-page case study + demo video

---

*Curriculum drafted with Claude Code.*
