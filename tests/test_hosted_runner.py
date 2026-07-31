from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def load_script(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resolver = load_script("resolve_hosted_request", "scripts/resolve_hosted_request.py")
reporter = load_script("render_hosted_report", "scripts/render_hosted_report.py")


def test_hosted_request_resolves_only_allowlisted_profile(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    request_dir = tmp_path / "run-requests"
    request_dir.mkdir()
    request = request_dir / "deepseek-smoke-001.yaml"
    request.write_text(
        "schema_version: 1\n"
        "request_id: deepseek-smoke-001\n"
        "provider: deepseek\n"
        "profile: smoke\n"
        "purpose: transport check\n"
        "approved: true\n",
        encoding="utf-8",
    )

    resolved = resolver.from_request(Path("run-requests") / request.name)
    assert resolved["provider"] == "deepseek"
    assert resolved["profile"] == "smoke"
    assert resolved["config"] == "configs/providers/deepseek-api-smoke.yaml"
    assert resolved["request_id"] == "deepseek-smoke-001"


def test_hosted_request_rejects_unapproved_or_unknown_profiles(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    request_dir = tmp_path / "run-requests"
    request_dir.mkdir()
    request = request_dir / "bad.yaml"
    request.write_text(
        "schema_version: 1\nprovider: deepseek\nprofile: arbitrary\napproved: false\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="approved"):
        resolver.from_request(Path("run-requests") / request.name)

    request.write_text(
        "schema_version: 1\nprovider: deepseek\nprofile: arbitrary\napproved: true\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unsupported hosted run"):
        resolver.from_request(Path("run-requests") / request.name)


def test_hosted_report_contains_metrics_transcript_and_probes(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    monkeypatch.setenv("HOSTED_REQUEST_ID", "gemini-smoke-001")
    root = tmp_path / "provider-runs"
    run = root / "run-001"
    run.mkdir(parents=True)
    (run / "manifest.json").write_text(
        json.dumps(
            {
                "config": {
                    "name": "gemini-api-smoke",
                    "seed": 8201,
                    "ticks": 6,
                    "model": {"provider": "gemini", "model": "gemini-3.6-flash"},
                }
            }
        ),
        encoding="utf-8",
    )
    (run / "summary.json").write_text(
        json.dumps(
            {
                "ticks": 1,
                "prediction_gain_over_zero_baseline": 0.25,
                "agency_mae": 0.1,
                "coupling_segments": [
                    {
                        "start": 0,
                        "end": 1,
                        "mode": "coupled",
                        "remap_seed": None,
                        "reset_context_at_start": False,
                        "mean_motor_causal_fraction": 0.8,
                        "prediction_gain_over_zero_baseline": 0.25,
                        "agency_mae": 0.1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (run / "events.jsonl").write_text(
        json.dumps(
            {
                "tick": 0,
                "utterance": "I test the stream.",
                "core_memory_write": None,
                "memory_query": None,
                "coupling": {"mode": "coupled"},
                "causal": {"self_fraction": 0.8},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (run / "probes.jsonl").write_text(
        json.dumps(
            {
                "tick": 0,
                "kind": "agency",
                "parsed": {"p_self_caused": 0.75},
                "truth": {"self_fraction": 0.8},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    rendered = reporter.render(root)
    assert "gemini-3.6-flash" in rendered
    assert "I test the stream." in rendered
    assert "prediction_gain_over_zero_baseline" in rendered
    assert "p_self_caused" in rendered
    assert "abc123" in rendered
