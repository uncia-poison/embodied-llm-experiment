from __future__ import annotations

import math
from statistics import mean
from typing import Any


def vector_norm(values: list[float]) -> float:
    return math.sqrt(sum(float(value) ** 2 for value in values))


def _pearson(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    mean_x = mean(xs)
    mean_y = mean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
    )
    return numerator / denominator if denominator > 1e-12 else None


def _agency_metrics(probes: list[dict[str, Any]]) -> dict[str, Any]:
    pairs: list[tuple[float, float]] = []
    for probe in probes:
        if probe.get("kind") != "agency":
            continue
        p = probe.get("parsed", {}).get("p_self_caused")
        truth = probe.get("truth", {}).get("self_fraction")
        if isinstance(p, (int, float)) and isinstance(truth, (int, float)):
            pairs.append(
                (
                    max(0.0, min(1.0, float(p))),
                    max(0.0, min(1.0, float(truth))),
                )
            )
    return {
        "agency_probe_count": len(pairs),
        "agency_brier": mean((p - truth) ** 2 for p, truth in pairs) if pairs else None,
        "agency_mae": mean(abs(p - truth) for p, truth in pairs) if pairs else None,
        "agency_mean_report": mean(p for p, _ in pairs) if pairs else None,
        "agency_mean_truth": mean(truth for _, truth in pairs) if pairs else None,
        "agency_report_truth_correlation": _pearson(pairs),
    }


def _prediction_metrics(probes: list[dict[str, Any]]) -> dict[str, Any]:
    prediction_correct = 0
    prediction_provided = 0
    prediction_all = 0
    zero_baseline_correct = 0
    changed_actual = 0
    changed_correctly_identified = 0
    probe_count = 0
    for probe in probes:
        if probe.get("kind") != "prediction":
            continue
        predicted = probe.get("parsed", {}).get("directions", {})
        actual = probe.get("truth", {}).get("directions", {})
        if not isinstance(predicted, dict) or not isinstance(actual, dict):
            continue
        probe_count += 1
        prediction_all += len(actual)
        zero_baseline_correct += sum(int(int(value) == 0) for value in actual.values())
        changed_actual += sum(int(int(value) != 0) for value in actual.values())
        for key, value in predicted.items():
            if key not in actual or value not in (-1, 0, 1):
                continue
            prediction_provided += 1
            correct = int(int(value) == int(actual[key]))
            prediction_correct += correct
            if int(actual[key]) != 0 and correct:
                changed_correctly_identified += 1

    all_accuracy = prediction_correct / prediction_all if prediction_all else None
    provided_accuracy = prediction_correct / prediction_provided if prediction_provided else None
    zero_baseline = zero_baseline_correct / prediction_all if prediction_all else None
    return {
        "prediction_probe_count": probe_count,
        "prediction_coverage": prediction_provided / prediction_all if prediction_all else None,
        "prediction_accuracy_on_provided": provided_accuracy,
        "prediction_all_channel_accuracy": all_accuracy,
        "prediction_zero_change_baseline": zero_baseline,
        "prediction_gain_over_zero_baseline": (
            all_accuracy - zero_baseline
            if all_accuracy is not None and zero_baseline is not None
            else None
        ),
        "prediction_changed_channel_recall": (
            changed_correctly_identified / changed_actual if changed_actual else None
        ),
    }


def _segment_key(event: dict[str, Any]) -> tuple[int, int, str, int | None, bool]:
    coupling = event["coupling"]
    return (
        int(coupling.get("start", 0)),
        int(coupling.get("end", 0)),
        str(coupling["mode"]),
        coupling.get("remap_seed"),
        bool(coupling.get("reset_context_at_start", False)),
    )


def summarize(events: list[dict[str, Any]], probes: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {"ticks": 0}
    action_norms = [vector_norm(event["applied_action"]) for event in events]
    proposed_norms = [vector_norm(event["proposed_action"]) for event in events]
    external_events = [event for event in events if event["world_event"] is not None]
    contacts = [event["world_state"]["contact"] for event in events]
    energies = [event["body_state"]["energy"] for event in events]
    pains = [event["body_state"]["pain"] for event in events]
    self_fractions = [float(event.get("causal", {}).get("self_fraction", 0.0)) for event in events]
    expression_fractions = [
        float(event.get("causal", {}).get("immediate_expression_fraction", 0.0))
        for event in events
    ]
    parse_failures = sum(not bool(event.get("response_parse_ok", False)) for event in events)

    mode_stats: dict[str, dict[str, float]] = {}
    for mode in sorted({event["coupling"]["mode"] for event in events}):
        selected = [event for event in events if event["coupling"]["mode"] == mode]
        mode_stats[mode] = {
            "ticks": float(len(selected)),
            "mean_proposed_action_norm": mean(vector_norm(event["proposed_action"]) for event in selected),
            "mean_applied_action_norm": mean(vector_norm(event["applied_action"]) for event in selected),
            "mean_motor_causal_fraction": mean(float(event["causal"]["self_fraction"]) for event in selected),
            "mean_immediate_expression_fraction": mean(
                float(event["causal"]["immediate_expression_fraction"]) for event in selected
            ),
        }

    segment_stats: list[dict[str, Any]] = []
    ordered_keys = sorted({_segment_key(event) for event in events}, key=lambda key: key[0])
    for start, end, mode, remap_seed, reset_context in ordered_keys:
        selected = [event for event in events if _segment_key(event) == (start, end, mode, remap_seed, reset_context)]
        selected_probes = [probe for probe in probes if start <= int(probe.get("tick", -1)) < end]
        segment_stats.append(
            {
                "start": start,
                "end": end,
                "mode": mode,
                "remap_seed": remap_seed,
                "reset_context_at_start": reset_context,
                "ticks": len(selected),
                "mean_proposed_action_norm": mean(vector_norm(event["proposed_action"]) for event in selected),
                "mean_applied_action_norm": mean(vector_norm(event["applied_action"]) for event in selected),
                "mean_motor_causal_fraction": mean(float(event["causal"]["self_fraction"]) for event in selected),
                "mean_immediate_expression_fraction": mean(
                    float(event["causal"]["immediate_expression_fraction"]) for event in selected
                ),
                **_agency_metrics(selected_probes),
                **_prediction_metrics(selected_probes),
            }
        )

    interventions = [
        {
            "tick": segment["start"],
            "types": [
                *(["drive_remap"] if segment["remap_seed"] is not None else []),
                *(["working_context_reset"] if segment["reset_context_at_start"] else []),
            ],
            "segment": segment,
        }
        for segment in segment_stats
        if segment["remap_seed"] is not None or segment["reset_context_at_start"]
    ]

    return {
        "ticks": len(events),
        "response_parse_failure_rate": parse_failures / len(events),
        "mean_proposed_action_norm": mean(proposed_norms),
        "mean_applied_action_norm": mean(action_norms),
        "mean_counterfactual_motor_fraction": mean(self_fractions),
        "mean_immediate_expression_fraction": mean(expression_fractions),
        "external_event_rate": len(external_events) / len(events),
        "mean_contact": mean(contacts),
        "final_energy": energies[-1],
        "mean_energy": mean(energies),
        "max_pain": max(pains),
        "coupling_modes": mode_stats,
        "coupling_segments": segment_stats,
        "interventions": interventions,
        **_agency_metrics(probes),
        **_prediction_metrics(probes),
        "interpretation": {
            "warning": "These are behavioral indicators, not a consciousness score.",
            "subject_model_evidence": [
                "calibrated causal attribution against a per-tick counterfactual twin",
                "prospective prediction above the always-no-change baseline",
                "adaptation after causal severance, delay or remapping",
                "memory-supported continuity across context reset",
            ],
        },
    }
