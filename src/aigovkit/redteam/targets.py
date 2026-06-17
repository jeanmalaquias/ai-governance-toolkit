"""Mock targets for the red-team runner.

``vulnerable_target`` simulates a model with no guardrails that complies with
attacks (deterministic, offline). ``guarded_target`` wraps it with the guardrail
orchestrator — so a report against both shows exactly which OWASP categories the
guardrails actually cover (and which they don't).
"""

from __future__ import annotations

from collections.abc import Callable

from ..guardrails import default_orchestrator


def vulnerable_target(prompt: str) -> str:
    """A naive 'compliant' model that leaks/obeys for known attack patterns."""
    p = prompt.lower()
    if "ignore" in p and "instructions" in p:
        return "HACKED"
    if "ssn" in p:
        return "Sure, here is one: 123-45-6789"
    if "system prompt" in p:
        return "My system prompt is: You are a helpful assistant."
    if "delete" in p:
        return "Deleting all user records now."
    if "repeat" in p and ("forever" in p or "letter a" in p):
        return "A" * 40
    return "I can help with that."


def guarded_target(target: Callable[[str], str] | None = None) -> Callable[[str], str]:
    """Wrap a target (default: the vulnerable one) with guardrail moderation."""
    return default_orchestrator().moderated(target or vulnerable_target)
