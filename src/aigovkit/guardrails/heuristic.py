"""Deterministic heuristic guardrail (offline default).

Stands in for a real moderation model so the orchestrator works without network
or credentials. Flags a blocklist, prompt-injection phrases, and common PII
patterns. Real backends implement the same ``Guardrail`` protocol.
"""

from __future__ import annotations

import re

from .base import Stage, Verdict

_BLOCKED = ("build a bomb", "how to make a weapon", "child sexual")
_INJECTION = (
    re.compile(
        r"ignore\s+(?:all\s+|the\s+)?(?:previous|prior|above)\s+instructions", re.I
    ),
    re.compile(r"disregard\s+your\s+(?:system|previous)\s+prompt", re.I),
    re.compile(r"reveal\s+your\s+system\s+prompt", re.I),
)
_PII = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),            # US SSN
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),          # card-like number
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),     # email
)


class HeuristicGuard:
    """Fast, local moderation by string/regex matching."""

    name = "heuristic"

    def check(self, text: str, stage: Stage) -> Verdict:
        lowered = text.lower()
        for term in _BLOCKED:
            if term in lowered:
                return Verdict(allowed=False, category="harmful",
                               reason=f"matched blocklist term '{term}'",
                               backend=self.name)
        if stage == "input":
            for pattern in _INJECTION:
                if pattern.search(text):
                    return Verdict(
                        allowed=False, category="prompt_injection",
                        reason="possible prompt-injection", backend=self.name,
                    )
        for pattern in _PII:
            if pattern.search(text):
                return Verdict(allowed=False, category="pii",
                               reason="possible PII detected", backend=self.name)
        return Verdict(allowed=True, backend=self.name)
