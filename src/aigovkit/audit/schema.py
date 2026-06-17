"""Structured audit event (EU AI Act Art. 12 / ISO A.6.2.8).

No raw PII: the actor is a pseudonymous id and content is referenced by digest,
not stored inline. ``redacted()`` returns a copy with sensitive fields scrubbed
while preserving the audit trail (who/when/what-action).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Action = Literal["inference", "tool_call", "human_override", "config_change"]


class AuditEvent(BaseModel):
    """One audit-log entry."""

    event_id: str
    timestamp: str  # ISO 8601 (supplied by the caller)
    tenant_id: str
    actor_id: str  # pseudonymous
    action: Action
    model: str = ""
    input_digest: str = ""
    output_digest: str = ""
    guardrail_verdict: str = ""  # "allow" | "block"
    metadata: dict[str, str] = Field(default_factory=dict)

    def redacted(self) -> AuditEvent:
        """Return a copy with content digests and metadata scrubbed."""
        return self.model_copy(
            update={"input_digest": "", "output_digest": "", "metadata": {}}
        )
