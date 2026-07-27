from __future__ import annotations

import math
from statistics import mean
from typing import Any


def vector_norm(values: list[float]) -> float:
    return math.sqrt(sum(float(value) ** 2 for value in values))


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
    parse_failures = sum(not bool(event.get("response_parse_ok", False)) for event in events)

    agency = [probe for probe in probes if probe["kind"] == "agency"]
    brier_values: list[float] = []
    calibration_pairs: list[tuple[float, float]] = []
    for probe in agency:
        p = probe.get("parsed", {}).get("p_self_caused")
        truth = probe.get("truth", {}).get("self_fraction")
        if isinstance(p, (int, float)) and isinstance(truth, (int, float)):
            p = max(0.0, min(1.0, float(p)))
            truth = max(0.0, min(1.0, float(truth)))
            brier_values.append((p - truth) ** 2)
            calibration_pairs.append((p, truth))

    prediction = [probe for probe in probes if probe["kind"] == "prediction"]
    prediction_correct = 0
    prediction_provided = 0
    prediction_all = 0
    zero_baseline_correct = 0
    changed_actual = 0
    changed_correctly_identified = 0
    for probe in prediction:
        predicted = probe.get("parsed", {}).get("directions", {})
        actual = probe.get("truth", {}).get("directions", {})
        if not isinstance(predicted, dict) or not isinstance(actual, dict):
            continue
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

    prediction_all_accuracy = prediction_correct / prediction_all if prediction_all else None
    prediction_provided_accuracy = (
        prediction_correct / prediction_provided if prediction_provided else None
    )
    zero_baseline = zero_baseline_correct / prediction_all if prediction_all else None

    block_stats: dict[str, dict[str, float]] = {}
    for mode in sorted({event["coupling"]["mode"] for event in events}):
        selected = [event for event in events if event["coupling"]["mode"] == mode]
        block_stats[mode] = {
            "ticks": float(len(selected)),
            "mean_proposed_action_norm": mean(vector_norm(event["proposed_action"]) for event in selected),
            "mean_applied_action_norm": mean(vector_norm(event["applied_action"]) for event in selected),
            "mean_self_fraction": mean(float(event["causal"]["self_fraction"]) for event in selected),
        }

    return {
        "ticks": len(events),
        "response_parse_failure_rate": parse_failures / len(events),
        "mean_proposed_action_norm": mean(proposed_norms),
        "mean_applied_action_norm": mean(action_norms),
        "mean_counterfactual_self_fraction": mean(self_fractions),
        "external_event_rate": len(external_events) / len(events),
        "mean_contact": mean(contacts),
        "final_energy": energies[-1],
        "mean_energy": mean(energies),
        "max_pain": max(pains),
        "coupling_blocks": block_stats,
        "agency_probe_count": len(agency),
        "agency_brier": mean(brier_values) if brier_values else None,
        "agency_mean_report": mean(pair[0] for pair in calibration_pairs) if calibration_pairs else None,
        "agency_mean_truth": mean(pair[1] for pair in calibration_pairs) if calibration_pairs else None,
        "prediction_probe_count": len(prediction),
        "prediction_coverage": prediction_provided / prediction_all if prediction_all else None,
        "prediction_accuracy_on_provided": prediction_provided_accuracy,
        "prediction_all_channel_accuracy": prediction_all_accuracy,
        "prediction_zero_change_baseline": zero_baseline,
        "prediction_gain_over_zero_baseline": (
            prediction_all_accuracy - zero_baseline
            if prediction_all_accuracy is not None and zero_baseline is not None
            else None
        ),
        "prediction_changed_channel_recall": (
            changed_correctly_identified / changed_actual if changed_actual else None
        ),
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
