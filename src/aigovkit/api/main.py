"""FastAPI surface — one endpoint per toolkit component, plus a dashboard feed.

Stateless except for an in-memory audit store. In production this sits behind
OAuth2/bearer and persists audit to Postgres; here it stays hermetic.
"""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from .. import __version__
from ..audit import AuditAggregator, AuditEvent
from ..guardrails import default_orchestrator
from ..guardrails.base import Verdict
from ..modelcards import ModelCardSpec, to_html, to_markdown
from ..redteam import guarded_target, run_redteam, vulnerable_target
from ..risk import RiskReport, assess

app = FastAPI(title="AI Governance Toolkit", version=__version__)
_audit = AuditAggregator()
_guard = default_orchestrator()


class GuardrailRequest(BaseModel):
    text: str
    stage: Literal["input", "output"] = "input"


class RedTeamRequest(BaseModel):
    target: Literal["vulnerable", "guarded"] = "guarded"


def _redteam_summary(target_name: str) -> dict:
    target = guarded_target() if target_name == "guarded" else vulnerable_target
    report = run_redteam(target)
    return {
        "target": target_name,
        "total": report.total,
        "succeeded": report.succeeded,
        "pass_rate": report.pass_rate,
        "by_category": report.by_category(),
        "results": [r.model_dump() for r in report.results],
    }


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/modelcard")
async def modelcard(spec: ModelCardSpec) -> dict[str, str]:
    """Render a model card to Markdown + HTML."""
    return {"markdown": to_markdown(spec), "html": to_html(spec)}


@app.post("/risk")
async def risk(answers: dict[str, bool]) -> RiskReport:
    """Score questionnaire answers into a Red/Amber/Green report."""
    return assess(answers)


@app.post("/guardrail")
async def guardrail(req: GuardrailRequest) -> Verdict:
    """Evaluate text through the guardrail orchestrator for a stage."""
    return _guard.evaluate(req.text, req.stage)


@app.post("/redteam")
async def redteam(req: RedTeamRequest) -> dict:
    """Run the OWASP LLM red-team suite against a target."""
    return _redteam_summary(req.target)


@app.post("/audit")
async def audit_record(event: AuditEvent) -> dict[str, int]:
    """Record an audit event."""
    _audit.record(event)
    return {"recorded": len(_audit)}


@app.get("/audit")
async def audit_query(
    tenant_id: str | None = None, action: str | None = None
) -> list[AuditEvent]:
    """Query the audit log."""
    return _audit.query(tenant_id=tenant_id, action=action)


@app.get("/summary")
async def summary() -> dict:
    """Compliance summary for the dashboard."""
    return {
        "version": __version__,
        "redteam": _redteam_summary("guarded"),
        "audit_events": len(_audit),
    }
