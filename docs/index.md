# Production-Grade AI Agents

Seven phases. Seven shipped artifacts. **A mastery gate for each one.**

[Start on GitHub →](https://github.com/Tatendaz/langchain-fde-curriculum) [Phase 0](https://github.com/Tatendaz/langchain-fde-curriculum/blob/main/phase0/README.md)

- **~60–70 hrs** — 8 weeks, hard cap 2 months
- **~$0** — local Ollama + LangSmith free tier
- **7 artifacts** — they become your portfolio

## What it is

A free, self-paced curriculum that takes you from *"I use LLMs"* to *"I can design, evaluate, and ship production agents on the [LangChain](https://docs.langchain.com/oss/python/langchain/overview) / [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) / [LangSmith](https://smith.langchain.com) stack — and deliver them as a service."*

The ecosystem moves fast, so it optimizes for **durable skills** — agent architecture, evaluation, observability, productionization — over memorizing today's API surface. Two things make it different from the many agent tutorials out there.

- **🎯 Mastery gates** You don't move on by finishing the code. You move on by passing a gate — a build checklist, a closed-book concept check with hidden answer keys, and an "explain it to a client" scenario. Almost no free curriculum gates progression on demonstrated understanding.

- **📊 Evaluation as the spine, not a module** The most-asked question in FDE interviews is *"how do you know it works?"* Phase 4 exists so you always have a real answer, and every phase after it keeps that answer current.

## The 8-week map

| Week | Phase | Deliverable you ship | Hours |
|---|---|---|---|
| 1 | 0 — Foundations | Traced hello-world (tool call + structured output) | ~8 |
| 2 | 1 — First agent | One agent, 3 real tools, one nested trace | ~8 |
| 3 | 2 — LangGraph | Rebuilt agent: persistence + approval interrupt | ~10 |
| 4 | 3 — RAG, memory, MCP | Agent with knowledge base + long-term memory + MCP tool | ~10 |
| 5 | 4 — Evals & observability | Eval suite + CI regression gate + monitoring | ~10 |
| 6–7 | 5 — Production & deploy | Hardened agent on k8s (or LangSmith Deployment) | ~12 |
| 7–8 | 6 — Capstone + FDE drills | Capstone + case study + demo video + drill artifacts | ~12 |

The non-negotiable spine is **1 → 2 → 4 → 5 → capstone**: build an agent, make it stateful, prove it works, ship it. Phase 3 isn't skipped — it's the one phase whose *depth* flexes when you fall behind.

## How each phase works

1. **Run the worked example.** Phases 0–3 ship working, commented code: run it, read the trace, break it, fix it. Phases 4–6 are build guides — you write the code, which by then is the point.

2. **Modify before you build.** Swap a tool, change the retrieval `k`, reject an approval — friction should be conceptual, not syntactic.

3. **Ship the deliverable.** Every phase ends in a standalone artifact with an explicit definition-of-done. No tutorial limbo.

4. **Pass the gate.** Build check, concept check, FDE scenario. Miss more than one? Re-run the code the next day and retake it — that's the mastery loop working, not you failing.

## Who it's for

- **Engineers comfortable in Python** who use LLMs daily but haven't yet architected and deployed a **stateful agent to production**.

- **Infra / SRE / backend folks especially** The hardest parts of shipping — k8s, observability, reliability, secrets — are already your home turf. Your real gaps are narrower, and this plan leans into exactly those.

- **Aspiring or interviewing FDEs** Phase 6's drills mirror the actual loops: a build-for-a-fictional-customer take-home, a discovery-call simulation, and a non-technical presentation.

**Not for you if** you've never written Python, or you want ML research and model training — this is the applied agent-engineering layer.

## Getting started

```
# install uv + Ollama first, then from the repo root
ollama pull llama3.1                 # any tool-calling model works
uv sync                              # create the venv + install dependencies
cp .env.example .env                 # then set your Ollama + LangSmith values
uv run python -m phase0.hello_agent  # run the Phase 0 starter
uv run pytest                        # run the offline tests
```

Then open `phase0/README.md` and start the loop: run → modify → ship → gate.

## FAQ

### What does it cost to run?

About **$0** on the default path. Models run on local [Ollama](https://ollama.com) — if your machine is weak, a hosted provider works with a one-line `.env` change for a few dollars. LangSmith's free Developer tier covers the tracing, datasets and evaluations. Phase 5's DIY path runs on a local `kind`/`minikube` cluster, so no cloud bill; the managed path needs a paid plan and is presented as the client-engagement option, not a learning requirement.

### What's a mastery gate, exactly?

A build check (definition-of-done as checkboxes), a **closed-book** concept check with answers hidden behind collapsible blocks, and an FDE scenario. Write your answer down *before* peeking — generating the answer first is retrieval practice, the single best-supported technique in the learning literature, and it only works if you don't read ahead.

### Why gates instead of just more tutorials?

Retrieval practice and spacing are the only two techniques rated "high utility" in the canonical review of learning techniques, and mastery gates raise outcomes roughly half a standard deviation across 108 controlled studies. The [README](https://github.com/Tatendaz/langchain-fde-curriculum#readme) cites the papers if you want them.

### What do I finish with?

A deployed, evaluated, monitored capstone agent, plus a case study and a demo video — a portfolio that answers the question every FDE interview and client call comes down to: **"How do you know it works?"**

### Is it free and can I reuse it?

Yes. This repository's code and documentation are MIT-licensed. See the [LICENSE](https://github.com/Tatendaz/langchain-fde-curriculum/blob/main/LICENSE).

---

HTML version: https://tatendaz.github.io/langchain-fde-curriculum/ · Source: https://github.com/Tatendaz/langchain-fde-curriculum · More work: https://tatendaz.github.io/ · Agent guide: https://tatendaz.github.io/llms.txt
