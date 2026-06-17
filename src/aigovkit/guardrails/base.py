"""Guardrail interfaces and value types."""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel

Stage = Literal["input", "output"]


class Verdict(BaseModel):
    """The result of a guardrail check."""

    allowed: bool
    category: str | None = None
    reason: str = ""
    backend: str = ""


@runtime_checkable
class Guardrail(Protocol):
    """A moderation backend (Llama Guard, Content Safety, Bedrock, NeMo, ...)."""

    name: str

    def check(self, text: str, stage: Stage) -> Verdict: ...
