"""In-memory audit aggregator with a query API.

A real deployment persists to Postgres + ships to Loki via OpenTelemetry; this
in-memory store keeps the toolkit hermetic and gives the query/redaction surface
a testable home behind the same API.
"""

from __future__ import annotations

from .schema import AuditEvent


class AuditAggregator:
    """Append-only store of audit events with filtered queries."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self._events.append(event)

    def query(
        self,
        *,
        tenant_id: str | None = None,
        action: str | None = None,
        since: str | None = None,
        until: str | None = None,
    ) -> list[AuditEvent]:
        """Return events matching all provided filters (timestamps are ISO 8601)."""
        results = self._events
        if tenant_id is not None:
            results = [e for e in results if e.tenant_id == tenant_id]
        if action is not None:
            results = [e for e in results if e.action == action]
        if since is not None:
            results = [e for e in results if e.timestamp >= since]
        if until is not None:
            results = [e for e in results if e.timestamp <= until]
        return list(results)

    def redact(self, event_id: str) -> bool:
        """Redact a stored event's content in place. Returns True if found."""
        for i, event in enumerate(self._events):
            if event.event_id == event_id:
                self._events[i] = event.redacted()
                return True
        return False

    def __len__(self) -> int:
        return len(self._events)
