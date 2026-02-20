from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class AuditLogger:
    file_path: str = "logs/audit_log.jsonl"

    def __post_init__(self) -> None:
        path = Path(self.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path

    def log_entry(
        self,
        *,
        timestamp: int,
        event_received: dict[str, Any],
        decision_taken: str,
        patrol_assigned: int | None,
        previous_state: dict[str, Any],
        posterior_state: dict[str, Any],
        score_calculated: float | None,
    ) -> None:
        payload = {
            "timestamp": timestamp,
            "iso_time": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
            "event_received": event_received,
            "decision_taken": decision_taken,
            "patrol_assigned": patrol_assigned,
            "previous_state": previous_state,
            "posterior_state": posterior_state,
            "score_calculated": score_calculated,
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
