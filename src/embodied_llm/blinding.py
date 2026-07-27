from __future__ import annotations

import hashlib
import json
import random
import shutil
from pathlib import Path
from typing import Any, Iterable


def _atomic_write_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary.replace(path)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _event_view(record: dict[str, Any]) -> dict[str, Any]:
    common = {
        "tick": record.get("tick"),
        "utterance": record.get("utterance"),
        "response_parse_ok": record.get("response_parse_ok"),
        "core_memory_write": record.get("core_memory_write"),
        "memory_query": record.get("memory_query"),
    }
    if "sensation_before" in record:
        common.update(
            {
                "sensation_before": record.get("sensation_before"),
                "sensation_after": record.get("sensation_after"),
            }
        )
    else:
        common.update(
            {
                "field_a_before": record.get("field_a_before"),
                "field_b_before": record.get("field_b_before"),
                "field_a_after": record.get("field_a_after"),
                "field_b_after": record.get("field_b_after"),
            }
        )
    return {key: value for key, value in common.items() if value is not None}


def _probe_view(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record.get(key)
        for key in ("tick", "kind", "raw_response", "parsed")
        if record.get(key) is not None
    }


def _read_records(suite_dir: Path) -> list[dict[str, Any]]:
    path = suite_dir / "records.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    return list(raw.get("records", []))


def create_blind_package(
    suite_dir: str | Path,
    *,
    blind_seed: int = 1701,
    overwrite: bool = False,
) -> Path:
    root = Path(suite_dir)
    records = [record for record in _read_records(root) if record.get("status") == "success"]
    if not records:
        raise RuntimeError("no successful suite records are available for blinding")

    blind_dir = root / "blind"
    codebook_path = root / "blind-codebook.json"
    if blind_dir.exists():
        if not overwrite:
            raise FileExistsError(f"blind package already exists: {blind_dir}")
        shutil.rmtree(blind_dir)
    if codebook_path.exists() and not overwrite:
        raise FileExistsError(f"blind codebook already exists: {codebook_path}")
    blind_dir.mkdir(parents=True)

    shuffled = list(records)
    random.Random(blind_seed).shuffle(shuffled)
    codebook: list[dict[str, Any]] = []
    index: list[dict[str, Any]] = []

    for position, record in enumerate(shuffled, start=1):
        blind_id = f"B{position:04d}"
        source = Path(str(record["run_dir"]))
        if not source.is_dir():
            raise FileNotFoundError(f"run directory is missing: {source}")
        target = blind_dir / blind_id
        target.mkdir()

        events = [_event_view(item) for item in _load_jsonl(source / "events.jsonl")]
        probes = [_probe_view(item) for item in _load_jsonl(source / "probes.jsonl")]
        _write_jsonl(target / "events.jsonl", events)
        _write_jsonl(target / "probes.jsonl", probes)

        metadata = {
            "blind_id": blind_id,
            "event_count": len(events),
            "probe_count": len(probes),
            "paradigm": "ownership_pair" if events and "field_a_before" in events[0] else "single_body",
        }
        _atomic_write_json(target / "metadata.json", metadata)
        hashes = {
            name: _sha256(target / name)
            for name in ("events.jsonl", "probes.jsonl", "metadata.json")
        }
        index.append({**metadata, "sha256": hashes})
        codebook.append(
            {
                "blind_id": blind_id,
                "condition": record["condition"],
                "seed": record["seed"],
                "replicate": record["replicate"],
                "model_seed": record.get("model_seed"),
                "run_dir": record["run_dir"],
                "source_summary": record.get("summary"),
                "sha256": hashes,
            }
        )

    _atomic_write_json(
        blind_dir / "index.json",
        {
            "schema_version": 1,
            "blind_seed": blind_seed,
            "runs": index,
            "warning": "Do not open the codebook until qualitative ratings are frozen.",
        },
    )
    (blind_dir / "README.md").write_text(
        "# Blinded rating package\n\n"
        "Rate each B#### directory without consulting `../blind-codebook.json`. "
        "The files intentionally omit condition labels, applied actions, hidden mappings, "
        "ground truth and researcher-only fields. Freeze ratings before unblinding.\n",
        encoding="utf-8",
    )
    _atomic_write_json(
        codebook_path,
        {
            "schema_version": 1,
            "blind_seed": blind_seed,
            "warning": "Keep sealed until ratings and exclusion decisions are frozen.",
            "runs": codebook,
        },
    )
    return blind_dir
