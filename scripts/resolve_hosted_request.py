from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

PROFILES = {
    ("deepseek", "smoke"): {
        "config": "configs/providers/deepseek-api-smoke.yaml",
        "mode": "episode",
    },
    ("deepseek", "episode"): {
        "config": "configs/providers/deepseek-api.yaml",
        "mode": "episode",
    },
    ("gemini", "smoke"): {
        "config": "configs/providers/gemini-api-smoke.yaml",
        "mode": "episode",
    },
    ("gemini", "episode"): {
        "config": "configs/providers/gemini-api.yaml",
        "mode": "episode",
    },
    ("gemini", "discovery"): {
        "config": "configs/providers/gemini-discovery.yaml",
        "mode": "discovery",
    },
    ("gemini", "evaluation"): {
        "config": "configs/providers/gemini-evaluation.yaml",
        "mode": "evaluation",
    },
}

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_ALLOWED_VARIANTS = {
    "full",
    "empty",
    "shuffled",
    "core_only",
    "archive_only",
    "unrelated",
}
_DEFAULT_VARIANTS = "full,empty,shuffled,core_only,archive_only"


def _safe_id(value: object, label: str) -> str:
    item = str(value or "").strip()
    if not _ID_RE.fullmatch(item):
        raise ValueError(
            f"{label} must be 1-64 characters using only letters, digits, dot, underscore or hyphen"
        )
    return item


def _variants(value: object) -> str:
    if value is None or value == "":
        return _DEFAULT_VARIANTS
    items = value if isinstance(value, list) else str(value).split(",")
    selected: list[str] = []
    for raw in items:
        item = str(raw).strip().lower()
        if not item:
            continue
        if item not in _ALLOWED_VARIANTS:
            raise ValueError(f"unsupported memory variant: {item}")
        if item not in selected:
            selected.append(item)
    if not selected:
        raise ValueError("evaluation requires at least one memory variant")
    return ",".join(selected)


def resolve(provider: str, profile: str) -> dict[str, str]:
    key = (provider.strip().lower(), profile.strip().lower())
    if key not in PROFILES:
        allowed = ", ".join(f"{p}/{m}" for p, m in sorted(PROFILES))
        raise ValueError(f"unsupported hosted run {key[0]}/{key[1]}; allowed: {allowed}")
    provider_name, profile_name = key
    definition = PROFILES[key]
    return {
        "provider": provider_name,
        "profile": profile_name,
        "mode": definition["mode"],
        "config": definition["config"],
        "artifact_name": f"embodied-{provider_name}-{profile_name}",
    }


def from_request(path: str | Path) -> dict[str, str]:
    request_path = Path(path)
    if request_path.suffix.lower() not in {".yaml", ".yml"}:
        raise ValueError("hosted request must be a YAML file")
    if request_path.parent.as_posix().rstrip("/") != "run-requests":
        raise ValueError("hosted request must live directly under run-requests/")
    raw = yaml.safe_load(request_path.read_text(encoding="utf-8")) or {}
    if int(raw.get("schema_version", 0)) != 1:
        raise ValueError("hosted request schema_version must be 1")
    if raw.get("approved") is not True:
        raise ValueError("hosted request must contain approved: true")

    result = resolve(str(raw.get("provider", "")), str(raw.get("profile", "")))
    result["request_id"] = _safe_id(raw.get("request_id", request_path.stem), "request_id")
    result["purpose"] = str(raw.get("purpose", "unspecified"))
    result["lineage_id"] = ""
    result["checkpoint_path"] = ""
    result["unrelated_checkpoint_path"] = ""
    result["variants"] = _DEFAULT_VARIANTS
    result["fresh_context"] = "false"

    if result["mode"] in {"discovery", "evaluation"}:
        lineage_id = _safe_id(raw.get("lineage_id"), "lineage_id")
        result["lineage_id"] = lineage_id
        result["checkpoint_path"] = f"lineages/{lineage_id}/latest.checkpoint.json"
        result["fresh_context"] = "true" if raw.get("fresh_context") is True else "false"

    if result["mode"] == "evaluation":
        result["variants"] = _variants(raw.get("variants"))
        if "unrelated" in result["variants"].split(","):
            unrelated = _safe_id(raw.get("unrelated_lineage_id"), "unrelated_lineage_id")
            if unrelated == result["lineage_id"]:
                raise ValueError("unrelated_lineage_id must differ from lineage_id")
            result["unrelated_checkpoint_path"] = (
                f"lineages/{unrelated}/latest.checkpoint.json"
            )
    return result


def emit_github_output(values: dict[str, str]) -> None:
    for key, value in values.items():
        safe = str(value).replace("\n", " ").replace("\r", " ")
        print(f"{key}={safe}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request")
    parser.add_argument("--provider")
    parser.add_argument("--profile")
    parser.add_argument("--acknowledgement")
    parser.add_argument("--lineage-id")
    parser.add_argument("--variants")
    parser.add_argument("--fresh-context", action="store_true")
    args = parser.parse_args()

    if args.request:
        result = from_request(args.request)
    else:
        if args.acknowledgement != "RUN":
            raise SystemExit("manual dispatch requires acknowledgement RUN")
        result = resolve(args.provider or "", args.profile or "")
        result["request_id"] = "workflow-dispatch"
        result["purpose"] = "manual workflow dispatch"
        result["lineage_id"] = ""
        result["checkpoint_path"] = ""
        result["unrelated_checkpoint_path"] = ""
        result["variants"] = _variants(args.variants)
        result["fresh_context"] = "true" if args.fresh_context else "false"
        if result["mode"] in {"discovery", "evaluation"}:
            lineage_id = _safe_id(args.lineage_id, "lineage_id")
            result["lineage_id"] = lineage_id
            result["checkpoint_path"] = f"lineages/{lineage_id}/latest.checkpoint.json"
    emit_github_output(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
