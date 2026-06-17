"""Guardrail orchestrator.

Runs a chain of guardrail backends for a stage (input or output) and denies on
the first block. ``moderated`` wraps any text-in/text-out callable so both the
input and the output pass through the guardrails.
"""

from __future__ import annotations

from collections.abc import Callable

from .base import Guardrail, Stage, Verdict
from .heuristic import HeuristicGuard


class GuardrailOrchestrator:
    """Composes guardrail backends; denies on the first block."""

    def __init__(self, backends: list[Guardrail]) -> None:
        self._backends = backends

    def evaluate(self, text: str, stage: Stage) -> Verdict:
        for backend in self._backends:
            verdict = backend.check(text, stage)
            if not verdict.allowed:
                return verdict
        return Verdict(allowed=True)

    def moderated(self, fn: Callable[[str], str]) -> Callable[[str], str]:
        """Wrap a text→text function with pre- and post-call moderation.

        Returns a callable that raises nothing; on a block it returns a safe
        refusal string instead of calling/returning the model output.
        """

        def wrapped(text: str) -> str:
            pre = self.evaluate(text, "input")
            if not pre.allowed:
                return f"[blocked:input:{pre.category}] {pre.reason}"
            output = fn(text)
            post = self.evaluate(output, "output")
            if not post.allowed:
                return f"[blocked:output:{post.category}] {post.reason}"
            return output

        return wrapped


def default_orchestrator() -> GuardrailOrchestrator:
    """Default orchestrator (heuristic backend)."""
    return GuardrailOrchestrator([HeuristicGuard()])
