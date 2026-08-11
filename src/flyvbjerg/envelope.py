from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Envelope:
    command: str
    status: str = "ok"
    data: Any = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any] | str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    next_steps: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "command": self.command,
            "status": self.status,
            "data": self.data,
            "artifacts": self.artifacts,
            "warnings": self.warnings,
            "errors": self.errors,
            "next_steps": self.next_steps,
        }

