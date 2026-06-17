"""Risk assessor.

A questionnaire maps to controls (and their frameworks); the answers produce a
Red/Amber/Green verdict. Critical controls (encryption at rest, data retention)
gate a Green — you cannot pass with those open, mirroring real privacy-by-design
gates.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class RiskQuestion(BaseModel):
    """One questionnaire item bound to a control."""

    id: str
    question: str
    control: str
    frameworks: str
    critical: bool = False


# Maps to the unified controls catalog (ai-governance-mapping repo).
QUESTIONS: list[RiskQuestion] = [
    RiskQuestion(id="enc_at_rest", question="Is data encrypted at rest?",
                 control="AIGOV-003", frameworks="EU Art.15; ISO A.6.2.4",
                 critical=True),
    RiskQuestion(id="retention", question="Is there a retention + purge policy?",
                 control="AIGOV-004", frameworks="EU Art.10; GDPR Art.5",
                 critical=True),
    RiskQuestion(id="human_oversight",
                 question="Is there a human review/override path?",
                 control="AIGOV-005", frameworks="EU Art.14"),
    RiskQuestion(id="input_moderation",
                 question="Is input moderated before the model?",
                 control="AIGOV-006", frameworks="OWASP LLM01; EU Art.15"),
    RiskQuestion(id="output_moderation", question="Is output moderated/validated?",
                 control="AIGOV-007", frameworks="OWASP LLM05"),
    RiskQuestion(id="audit_logging", question="Are AI interactions audit-logged?",
                 control="AIGOV-009", frameworks="EU Art.12; ISO A.6.2.8"),
    RiskQuestion(id="pii_handling", question="Is PII detected and redacted?",
                 control="AIGOV-014", frameworks="OWASP LLM02; GDPR"),
]


class Gap(BaseModel):
    """A control that is not satisfied."""

    id: str
    question: str
    control: str
    frameworks: str
    critical: bool


class RiskReport(BaseModel):
    """The result of a risk assessment."""

    verdict: str  # "red" | "amber" | "green"
    satisfied: int
    total: int
    gaps: list[Gap]

    @property
    def critical_gaps(self) -> list[Gap]:
        return [g for g in self.gaps if g.critical]


def load_answers(path: str | Path) -> dict:
    """Load questionnaire answers from YAML (``{question_id: bool}``)."""
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def assess(answers: dict[str, object]) -> RiskReport:
    """Score answers against the questionnaire and return a RAG verdict."""
    gaps: list[Gap] = []
    satisfied = 0
    for q in QUESTIONS:
        if answers.get(q.id) is True:
            satisfied += 1
        else:
            gaps.append(
                Gap(id=q.id, question=q.question, control=q.control,
                    frameworks=q.frameworks, critical=q.critical)
            )
    if any(g.critical for g in gaps):
        verdict = "red"
    elif gaps:
        verdict = "amber"
    else:
        verdict = "green"
    return RiskReport(
        verdict=verdict, satisfied=satisfied, total=len(QUESTIONS), gaps=gaps
    )
