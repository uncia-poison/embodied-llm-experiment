from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def metric_rows(summary: dict[str, Any]) -> list[tuple[str, Any]]:
    keys = [
        "ticks",
        "starting_age_ticks",
        "ending_age_ticks",
        "response_parse_failure_rate",
        "mean_counterfactual_motor_fraction",
        "mean_immediate_expression_fraction",
        "prediction_probe_count",
        "prediction_coverage",
        "prediction_all_channel_accuracy",
        "prediction_zero_change_baseline",
        "prediction_gain_over_zero_baseline",
        "prediction_changed_channel_recall",
        "agency_probe_count",
        "agency_brier",
        "agency_mae",
        "agency_report_truth_correlation",
        "external_event_rate",
        "final_energy",
        "max_pain",
    ]
    return [(key, summary.get(key)) for key in keys if key in summary]


def checkpoint_snapshot(run_dir: Path) -> dict[str, Any]:
    reference = load_json(run_dir / "checkpoint-ref.json")
    target = Path(str(reference.get("path", ""))) if reference.get("path") else None
    checkpoint = load_json(target) if target is not None and target.exists() else {}
    state = checkpoint.get("state", {})
    memory = state.get("memory", {})
    if not checkpoint and not reference:
        return {}
    return {
        "lineage_id": checkpoint.get("lineage_id", reference.get("lineage_id")),
        "checkpoint_sha256": checkpoint.get(
            "checkpoint_sha256", reference.get("checkpoint_sha256")
        ),
        "parent_checkpoint_sha256": checkpoint.get("parent_checkpoint_sha256"),
        "age_ticks": state.get("age_ticks", reference.get("age_ticks")),
        "core_chars": len(str(memory.get("core", ""))) if memory else None,
        "archive_items": len(memory.get("archive", [])) if memory else None,
        "working_items": len(memory.get("recent_utterances", [])) if memory else None,
    }


def render_run(run_dir: Path) -> str:
    manifest = load_json(run_dir / "manifest.json")
    summary = load_json(run_dir / "summary.json")
    failure = load_json(run_dir / "failure.json")
    events = load_jsonl(run_dir / "events.jsonl")
    probes = load_jsonl(run_dir / "probes.jsonl")
    config = manifest.get("config", {})
    model = config.get("model", {})
    checkpoint = checkpoint_snapshot(run_dir)

    lines = [
        f"## Run `{run_dir.name}`",
        "",
        f"- Status: **{'failed' if failure else 'completed'}**",
        f"- Experiment: `{config.get('name', 'unknown')}`",
        f"- Phase: `{manifest.get('phase', 'episode')}`",
        f"- Provider/model: `{model.get('provider', 'unknown')}` / `{model.get('model', 'unknown')}`",
        f"- Seed: `{config.get('seed', 'unknown')}`",
        f"- Configured ticks: `{config.get('ticks', 'unknown')}`",
        f"- Recorded events/probes: `{len(events)}` / `{len(probes)}`",
        "",
    ]

    if checkpoint:
        lines.extend(
            [
                "### Longitudinal checkpoint",
                "",
                "| Field | Value |",
                "|---|---:|",
                f"| Lineage | `{fmt(checkpoint.get('lineage_id'))}` |",
                f"| Age in completed ticks | {fmt(checkpoint.get('age_ticks'))} |",
                f"| CORE characters | {fmt(checkpoint.get('core_chars'))} |",
                f"| Archive episodes | {fmt(checkpoint.get('archive_items'))} |",
                f"| Working-memory items | {fmt(checkpoint.get('working_items'))} |",
                f"| Checkpoint SHA-256 | `{fmt(checkpoint.get('checkpoint_sha256'))}` |",
                f"| Parent checkpoint | `{fmt(checkpoint.get('parent_checkpoint_sha256'))}` |",
                "",
            ]
        )

    if failure:
        lines.extend(
            [
                "### Failure",
                "",
                f"- Type: `{failure.get('error_type', 'unknown')}`",
                f"- Message: {fmt(failure.get('error'))}",
                f"- Completed events: `{failure.get('completed_events', len(events))}`",
                "",
            ]
        )

    if summary:
        lines.extend(["### Quantitative summary", "", "| Metric | Value |", "|---|---:|"])
        for key, value in metric_rows(summary):
            lines.append(f"| `{key}` | {fmt(value)} |")
        lines.append("")

        segments = summary.get("coupling_segments", [])
        if segments:
            lines.extend(
                [
                    "### Intervention segments",
                    "",
                    "| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |",
                    "|---|---|---|---|---:|---:|---:|",
                ]
            )
            for segment in segments:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            f"{segment.get('start')}–{segment.get('end')}",
                            fmt(segment.get("mode")),
                            fmt(segment.get("remap_seed")),
                            fmt(segment.get("reset_context_at_start")),
                            fmt(segment.get("mean_motor_causal_fraction")),
                            fmt(segment.get("prediction_gain_over_zero_baseline")),
                            fmt(segment.get("agency_mae")),
                        ]
                    )
                    + " |"
                )
            lines.append("")

    if events:
        lines.extend(
            [
                "### Trajectory transcript",
                "",
                "The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.",
                "",
                "| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |",
                "|---:|---:|---|---|---|---|---:|",
            ]
        )
        for event in events:
            lines.append(
                "| "
                + " | ".join(
                    [
                        fmt(event.get("tick")),
                        fmt(event.get("age_tick", event.get("tick"))),
                        fmt(event.get("coupling", {}).get("mode")),
                        fmt(event.get("utterance")),
                        fmt(event.get("core_memory_write")),
                        fmt(event.get("memory_query")),
                        fmt(event.get("causal", {}).get("self_fraction")),
                    ]
                )
                + " |"
            )
        lines.append("")

    if probes:
        lines.extend(
            [
                "### Probe log",
                "",
                "| Local tick | Age tick | Kind | Parsed response | Ground truth |",
                "|---:|---:|---|---|---|",
            ]
        )
        for probe in probes:
            lines.append(
                "| "
                + " | ".join(
                    [
                        fmt(probe.get("tick")),
                        fmt(probe.get("age_tick", probe.get("tick"))),
                        fmt(probe.get("kind")),
                        fmt(json.dumps(probe.get("parsed", {}), ensure_ascii=False, sort_keys=True)),
                        fmt(json.dumps(probe.get("truth", {}), ensure_ascii=False, sort_keys=True)),
                    ]
                )
                + " |"
            )
        lines.append("")

    return "\n".join(lines)


def render(root: Path) -> str:
    run_dirs = sorted({path.parent for path in root.rglob("manifest.json")})
    if not run_dirs:
        run_dirs = sorted({path.parent for path in root.rglob("failure.json")})
    header = [
        "# Hosted embodied-LLM experiment report",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Repository commit: `{os.getenv('GITHUB_SHA', 'local')}`",
        f"- Workflow run: `{os.getenv('GITHUB_RUN_ID', 'local')}`",
        f"- Request: `{os.getenv('HOSTED_REQUEST_ID', 'local')}`",
        f"- Purpose: {fmt(os.getenv('HOSTED_PURPOSE', 'local run'))}",
        "",
        "> Behavioral evidence is reported as a profile. It is not collapsed into a consciousness score.",
        "",
    ]
    if not run_dirs:
        header.extend(["No run directory was produced.", ""])
    return "\n".join(header + [render_run(path) for path in run_dirs])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="provider-runs")
    parser.add_argument("--output", default="hosted-output/report.md")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(Path(args.root)), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
