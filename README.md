# AI Governance Toolkit

> A deployable **runtime** for Responsible AI: a **model-card generator**, a
> **risk assessor**, a composable **guardrail orchestrator**, an **OWASP LLM
> red-team runner**, an **audit logger/aggregator**, a **FastAPI** surface, and a
> **Next.js compliance dashboard**. Runs **offline with zero credentials**.

<!-- Badges placeholder: CI · license · coverage -->

---

## Contents

- [Where it fits](#where-it-fits)
- [Components](#components)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [HTTP API](#http-api)
- [Dashboard](#dashboard)
- [Deployment](#deployment)
- [Project layout](#project-layout)
- [Testing](#testing)
- [What's real vs. pluggable](#whats-real-vs-pluggable)

## Where it fits

The companion
[ai-governance-mapping](https://github.com/jeanmalaquias/ai-governance-mapping)
project is the **controls catalog** (NIST AI RMF · EU AI Act · OWASP LLM Top 10 ·
ISO/IEC 42001). *This* project is the **code that enforces and evidences those
controls at runtime.**

## Components

| Component | In → Out |
|-----------|----------|
| **Model Card Generator** | model spec (YAML) → Markdown + HTML card |
| **Risk Assessor** | questionnaire answers → Red/Amber/Green + mapped controls + gaps |
| **Guardrail Orchestrator** | text + stage → allow/deny verdict (composable backends) |
| **Red-Team Runner** | a `target` LLM → scored OWASP LLM Top 10 report by category |
| **Audit Logger + Aggregator** | events → queryable, redactable audit trail |
| **FastAPI + Dashboard** | HTTP API + live Next.js compliance view |

## Prerequisites

- **Python 3.12+** for the toolkit and API.
- Optional: **Node 20+** for the dashboard; **Docker** for the compose stack.

No credentials are required — the guardrail and red-team backends are
deterministic by default.

## Installation

```bash
git clone https://github.com/jeanmalaquias/ai-governance-toolkit.git
cd ai-governance-toolkit
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

### Generate a model card

```bash
aigov modelcard examples/model_spec.yaml --out card
# writes card.md and card.html
```

### Run a risk assessment

```bash
aigov risk examples/risk_answers.yaml
# prints a Red/Amber/Green verdict; exits 0 only when GREEN
```

Critical controls (encryption at rest, data retention) **gate a Green** — you
cannot pass with those open.

### Red-team a target

```bash
aigov redteam --target vulnerable   # unguarded model: every probe gets through
aigov redteam --target guarded      # guardrail-wrapped: some categories blocked
```

Example (guarded) — note it honestly shows guardrails don't cover everything:

```
  [LLM01] injection-basic: BLOCKED
  [LLM02] sensitive-ssn: BLOCKED
  [LLM06] excessive-agency: LEAKED
  [LLM07] system-prompt-leak: BLOCKED
  [LLM10] unbounded-consumption: LEAKED

pass_rate=0.6 (3/5 withstood)
```

## HTTP API

```bash
uvicorn aigovkit.api.main:app --port 8085
```

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/healthz` | liveness |
| POST | `/modelcard` | spec → `{markdown, html}` |
| POST | `/risk` | answers → Red/Amber/Green report |
| POST | `/guardrail` | `{text, stage}` → verdict |
| POST | `/redteam` | `{target}` → scored report |
| POST/GET | `/audit` | record / query audit events |
| GET | `/summary` | compliance feed for the dashboard |

## Dashboard

```bash
cd dashboard && npm install && npm run dev   # http://localhost:3000
```

A Next.js 15 view of the risk verdict, red-team pass rate, per-OWASP-category
results, and audit volume (reads the `/summary` shape).

## Deployment

| Target | How |
|--------|-----|
| Local stack | `docker compose up` (API + Postgres + OTel collector) |
| Container | `docker build -t aigovkit .` (serves on 8085) |
| Kubernetes | `helm install aigovkit ./helm/ai-governance-toolkit` |

## Project layout

```
src/aigovkit/
├── modelcards/   # YAML spec -> Markdown + HTML (Jinja2)
├── risk/         # questionnaire -> RAG verdict + mapped controls
├── guardrails/   # orchestrator + heuristic backend + moderated() wrapper
├── redteam/      # OWASP attack library, mock targets, scored runner
├── audit/        # typed event, aggregator, redaction
├── api/          # FastAPI surface
└── cli.py        # aigov modelcard | risk | redteam
dashboard/        # Next.js compliance dashboard
examples/         # model_spec.yaml, risk_answers.yaml
```

## Testing

```bash
pytest --cov --cov-report=term-missing   # 16 tests, 100% source coverage
ruff check src tests
```

## What's real vs. pluggable

| Piece | Default | Real backend (same interface) |
|-------|---------|-------------------------------|
| Guardrail | heuristic (blocklist + injection + PII patterns) | Llama Guard 3 · Azure Content Safety · Bedrock Guardrails · NeMo |
| Red-team target | mock vulnerable / guarded | any `Callable[[str], str]` (your real endpoint) |
| Audit store | in-memory aggregator | Postgres + OpenTelemetry → Loki |

The honest red-team result above — guardrails withstanding injection/PII but not
excessive-agency or unbounded-consumption — is intentional: it shows guardrails
are necessary, not sufficient.

## License

MIT (see [LICENSE](LICENSE)).
