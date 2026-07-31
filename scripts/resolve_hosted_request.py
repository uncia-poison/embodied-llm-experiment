from __future__ import annotations

import argparse
from pathlib import Path

import yaml

PROFILES = {
    ("deepseek", "smoke"): "configs/providers/deepseek-api-smoke.yaml",
    ("deepseek", "episode"): "configs/providers/deepseek-api.yaml",
    ("gemini", "smoke"): "configs/providers/gemini-api-smoke.yaml",
    ("gemini", "episode"): "configs/providers/gemini-api.yaml",
}


def resolve(provider: str, profile: str) -> dict[str, str]:
    key = (provider.strip().lower(), profile.strip().lower())
    if key not in PROFILES:
        allowed = ", ".join(f"{p}/{m}" for p, m in sorted(PROFILES))
        raise ValueError(f"unsupported hosted run {key[0]}/{key[1]}; allowed: {allowed}")
    provider_name, profile_name = key
    return {
        "provider": provider_name,
        "profile": profile_name,
        "config": PROFILES[key],
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
    result["request_id"] = str(raw.get("request_id", request_path.stem))
    result["purpose"] = str(raw.get("purpose", "unspecified"))
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
    args = parser.parse_args()

    if args.request:
        result = from_request(args.request)
    else:
        if args.acknowledgement != "RUN":
            raise SystemExit("manual dispatch requires acknowledgement RUN")
        result = resolve(args.provider or "", args.profile or "")
        result["request_id"] = "workflow-dispatch"
        result["purpose"] = "manual workflow dispatch"
    emit_github_output(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
