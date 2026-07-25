# The curriculum — all seven phases

The full syllabus behind the README's
[curriculum table](../README.md#the-curriculum). Each phase README is
self-contained *as a document*, so you can link someone straight to one. The
**code** does build up: `phase2/agent.py` imports Phase 1's tools, and
Phases 4–6 all work against your Phase 3 agent.

Phases 0–3 are **worked examples** — code included, run and modify them.
Phases 4–6 are **build guides** — you write the code, which by then is the
point.

For the week-by-week calendar and the triage checkpoints, see the README's
[8-week map](../README.md#the-8-week-map). For how a gate works and what it
demands, see [How the phases work](../README.md#how-the-phases-work).

---

## Phase 0 — Foundations & mental model · ~3 evenings · [`phase0/`](../phase0/README.md)

Solidify the API-level model of LLM apps — you use them daily; now understand
them as primitives.

- Tokens, context windows, temperature, **structured output (Pydantic)**, and
  **tool / function calling** — the bedrock every agent is built on.
- Setup: `uv`, Python 3.11+, Ollama (or any provider), and a **LangSmith
  account with tracing env vars** — on from day one. (The README's
  [Getting started](../README.md#getting-started) has the full prerequisite
  list; get it in place before you open this phase.)
- **Deliverable:** a traced "hello world" — one chat call that makes one tool
  call and returns structured output, fully visible in a LangSmith trace.
- **Gate:** [phase0/README.md → Phase gate](../phase0/README.md#phase-gate--pass-this-before-phase-1)

## Phase 1 — LangChain core + your first agent · ~Week 2 · [`phase1/`](../phase1/README.md)

- Chat models, messages, prompt templates, structured output, **tool
  definition & binding**.
- **`create_agent`** — the standard tool-calling agent loop (import from
  `langchain.agents`; the older `langgraph.prebuilt.create_react_agent` is
  deprecated). Middleware is a Phase 5 topic; here you learn the loop itself.
- **LangSmith trace-reading as a debugging skill:** runs, threads, latency,
  token counts — and why the whole run is *one nested tree*.
- Tool safety: why every tool argument is untrusted input.
- **Deliverable:** a single agent calling 2–3 *real* tools (HTTP fetch +
  calculator + word count), fully traced.
- **Gate:** [phase1/README.md → Phase gate](../phase1/README.md#phase-gate--pass-this-before-phase-2)

## Phase 2 — LangGraph: the production agent runtime · ~Week 3 · [`phase2/`](../phase2/README.md)

The framework you'll actually ship. It's a state machine — natural territory
if you have an infra background. **The most important build week.**

- `StateGraph`: state schema, reducers, nodes, edges, **conditional routing,
  cycles** — the same loop as Phase 1, now with the machinery visible.
- **Persistence / checkpointers** (`MemorySaver` → **`PostgresSaver`**),
  threads, short-term memory. (Docs now call the in-memory one
  `InMemorySaver`; same thing.)
- **Human-in-the-loop:** `interrupt()` + `Command(resume=...)` — approval
  gates before risky actions, and why resume *replays the node*. Enterprises
  require this; you'll build it by hand so the packaged
  `HumanInTheLoopMiddleware` (Phase 5) is never magic to you.
- **Streaming** (tokens, steps) and **time-travel / replay** debugging.
- **Deliverable:** the Phase 1 agent rebuilt as an explicit graph with
  persistence + one approval interrupt gating a write action.
- **Gate:** [phase2/README.md → Phase gate](../phase2/README.md#phase-gate--pass-this-before-phase-3)

## Phase 3 — RAG, memory & tools at production quality · ~Week 4 · [`phase3/`](../phase3/README.md)

- **RAG pipeline:** loaders → chunking → embeddings → vector store
  (**`pgvector`** if you already run Postgres) → retrieval; stretch: hybrid
  search + reranking. Needs `ollama pull nomic-embed-text` (or your own
  `EMBED_MODEL`) before it will run.
- **Long-term memory** via the LangGraph `Store` — cross-thread memory, and
  the multi-tenancy trap (per-user namespaces) every client will ask about.
- **MCP integration** with `langchain-mcp-adapters` — wire an MCP server in
  as agent tools (stdio locally; streamable HTTP is the remote standard).
- **Deliverable:** an agent with a real knowledge base + long-term memory +
  one MCP-backed tool.
- **Gate:** [phase3/README.md → Phase gate](../phase3/README.md#phase-gate--pass-this-before-phase-4)

## Phase 4 — Evaluation & observability: the FDE differentiator · ~Week 5 · [`phase4/`](../phase4/README.md) · **do not skip**

The SLO mindset applied to agents: *"here's proof it works, and here's how
we'll know if it regresses."*

- **LangSmith datasets, experiments, `evaluate()`** — plus the open-source
  evaluator libraries **`openevals`** (LLM-as-judge, RAG groundedness) and
  **`agentevals`** (**trajectory evals** — did the agent take the right
  *steps*, not just give the right answer?). You install these yourself;
  they're not in the base lockfile.
- **Regression gating in CI** (pytest + LangSmith) — block merges on eval
  scores.
- **Online evaluation & monitoring:** dashboards, cost & latency tracking,
  **annotation queues** — and the production loop: annotated bad trace →
  dataset example → regression test.
- **Deliverable:** an eval suite + a CI gate that blocks regressions + a
  monitoring view. *This single deliverable is your strongest sales asset.*
- **Gate:** [phase4/README.md → Phase gate](../phase4/README.md#phase-gate--pass-this-before-phase-5)

## Phase 5 — Productionization & deployment · ~Weeks 6–7 · [`phase5/`](../phase5/README.md)

- **Guardrails & reliability as middleware:** `HumanInTheLoopMiddleware`,
  `PIIMiddleware`, model fallbacks & retries, tool retries, call limits —
  plus prompt-injection defense in depth, timeouts, and model routing.
- **Deployment — two paths, pick per client:**
  - *Managed:* **LangSmith Deployment** (the platform formerly called
    LangGraph Platform) — `langgraph dev` locally, `langgraph deploy` to
    ship; least ops. [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui)
    gives you a front end for free.
  - *DIY (your moat):* **FastAPI + LangGraph + `PostgresSaver` + Redis**,
    containerized, on k8s (`kind` is fine) with HPA, secrets, SSE streaming,
    health probes, and **multi-tenant isolation**.
- **Deliverable:** your agent deployed with persistence, autoscaling,
  secrets, and end-to-end tracing — and it survives a pod kill mid-approval.
- **Gate:** [phase5/README.md → Phase gate](../phase5/README.md#phase-gate--pass-this-before-phase-6)

## Phase 6 — Capstone + the FDE layer · ~Weeks 7–8 · [`phase6/`](../phase6/README.md)

- **Capstone:** one end-to-end vertical agent built against a **fictional
  client brief** (provided — or bring your own), exercising the whole stack:
  LangGraph + RAG + memory + HITL + evals + deployed + monitored.
- **FDE drills** — the skills that turn a skill set into a service, drilled
  the way interviews test them: a **discovery-call roleplay**, a timed
  **decomposition case study**, a **non-technical presentation**, and a
  **packaging/pricing one-pager**.
- **Deliverable:** capstone repo + one-page case study + 3-minute demo video.
  This trio *is* your sales kit — and your interview take-home rehearsal.
- **Gate:** [phase6/README.md → Final gate](../phase6/README.md#final-gate--the-whole-loop) —
  a cumulative check across all seven phases, one question per phase.

---

## Repo layout

```text
.
├── README.md          # start here
├── pyproject.toml     # uv project (dependencies shared across phases)
├── uv.lock            # exact tested versions — committed on purpose
├── .python-version    # 3.12 (pyproject allows >=3.11)
├── .env.example       # copy to .env and fill in your keys
├── phase0/            # worked example: traced hello-world
├── phase1/            # worked example: first agent via create_agent
├── phase2/            # worked example: LangGraph rebuild (persistence + HITL)
├── phase3/            # worked example: RAG + long-term memory + MCP
├── phase4/            # build guide: evals, CI gate, monitoring
├── phase5/            # build guide: guardrails, reliability, deployment
├── phase6/            # build guide: capstone brief + FDE drills
├── tests/             # 14 offline unit tests for the pure logic in phases 0–3
├── docs/              # this docs set, plus features/ and summaries/ (PR gate)
├── .github/workflows/ # PR gate: docs entries + tests + new-code-has-tests
├── CONTRIBUTING.md    # fixes, questions, and sharing your solutions
└── LICENSE            # MIT — code and prose alike
```
