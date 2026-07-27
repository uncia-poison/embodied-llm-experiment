from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RunLogger:
    def __init__(self, root: str | Path, run_name: str, seed: int):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.run_dir = Path(root) / f"{run_name}-{stamp}-s{seed}"
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.events_path = self.run_dir / "events.jsonl"
        self.probes_path = self.run_dir / "probes.jsonl"

    @staticmethod
    def _append(path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def write_manifest(self, record: dict[str, Any]) -> None:
        (self.run_dir / "manifest.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def event(self, record: dict[str, Any]) -> None:
        self._append(self.events_path, record)

    def probe(self, record: dict[str, Any]) -> None:
        self._append(self.probes_path, record)

    def write_summary(self, record: dict[str, Any]) -> None:
        (self.run_dir / "summary.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
