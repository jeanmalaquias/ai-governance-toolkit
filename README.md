# AI Governance Toolkit

> A deployable **runtime** for Responsible AI: a **model-card generator**, a
> **risk assessor**, a composable **guardrail orchestrator**, an **OWASP LLM
> red-team runner**, an **audit logger/aggregator**, a **FastAPI** surface, and a
> **Next.js compliance dashboard**. Runs offline with zero credentials.

<!-- Badges placeholder: CI, license, coverage -->

---

## Where it fits

The companion [ai-governance-mapping](https://github.com/jeanmalaquias/ai-governance-mapping)
project is the **controls catalog** (NIST AI RMF · EU AI Act · OWASP LLM Top 10 ·
ISO/IEC 42001). *This* project is the **code that enforces and evidences those
controls at runtime.**

## Components

| Component | In → Out |
|-----------|----------|
| **Model Card Generator** | model spec (YAML/dict) → Markdown + HTML card |
| **Risk Assessor** | questionnaire answers → Red/Amber/Green verdict + mapped controls + gaps |
| **Guardrail Orchestrator** | text + stage → allow/deny verdict (composable backends) |
| **Red-Team Runner** | a `target` LLM → scored OWASP LLM Top 10 report |
| **Audit Logger + Aggregator** | events → queryable, redactable audit trail |
| **FastAPI + Dashboard** | HTTP API + live Next.js compliance view |

Everything is offline-deterministic by default — the guardrail and red-team
backends use deterministic heuristics, so CI is hermetic and demos need no
secrets. Real backends (Llama Guard 3, Azure AI Content Safety, Bedrock
Guardrails, NeMo) implement the same interfaces and swap in by config.

## Quick start

```bash
pip install -e ".[dev]"

# Generate a model card
aigov modelcard examples/model_spec.yaml --out card

# Run a risk assessment
aigov risk examples/risk_answers.yaml

# Red-team a target (mock vulnerable vs. guarded)
aigov redteam --target guarded

# Serve the API + dashboard data
uvicorn aigovkit.api.main:app --port 8085
```

## Architecture

See [docs/architecture.md](docs/architecture.md).

## Status

- [ ] Model Card Generator
- [ ] Risk Assessor
- [ ] Guardrail Orchestrator
- [ ] Red-Team Runner
- [ ] Audit Logger + Aggregator
- [ ] FastAPI surface
- [ ] Next.js compliance dashboard
- [ ] Docker Compose + Helm + CI

## License

MIT (see [LICENSE](LICENSE)).
