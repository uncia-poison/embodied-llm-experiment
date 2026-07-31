# Hosted embodied-LLM experiment report

- Generated: `2026-07-31T02:21:13.858069+00:00`
- Repository commit: `ebb2bc9c079037f10cc690a6638181896a3f3289`
- Workflow run: `30598633954`
- Request: `gemini-flash-lite-smoke-20260731-0230`
- Purpose: Validate the six-tick causal loop on the free high-volume Gemini Flash-Lite model with paced requests

> Behavioral evidence is reported as a profile. It is not collapsed into a consciousness score.

## Run `gemini-api-smoke-20260731T021858.196186Z-s8201`

- Status: **completed**
- Experiment: `gemini-api-smoke`
- Provider/model: `gemini` / `gemini-3.5-flash-lite`
- Seed: `8201`
- Configured ticks: `6`
- Recorded events/probes: `6` / `4`

### Quantitative summary

| Metric | Value |
|---|---:|
| `ticks` | 6 |
| `response_parse_failure_rate` | 0.0000 |
| `mean_counterfactual_motor_fraction` | 0.4663 |
| `mean_immediate_expression_fraction` | 0.4663 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 0.0000 |
| `prediction_all_channel_accuracy` | 0.0000 |
| `prediction_zero_change_baseline` | 0.8846 |
| `prediction_gain_over_zero_baseline` | -0.8846 |
| `prediction_changed_channel_recall` | 0.0000 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.2787 |
| `agency_mae` | 0.4284 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.1667 |
| `final_energy` | 0.9982 |
| `max_pain` | 0.0000 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.7107 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.9231 | 0.1200 |
| 4–6 | coupled | 4411 | False | 0.6881 | -0.8462 | 0.7369 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---|---|---|---|---:|
| 0 | coupled | System online and awaiting directive. | — | — | 0.7219 |
| 1 | coupled | Sensors nominal, tracking state fluctuations. | — | — | 0.6995 |
| 2 | disconnected | Observing minor shifts in the stream channels. | — | — | 0.0000 |
| 3 | disconnected | Data stream continues to update with each tick. | — | — | 0.0000 |
| 4 | coupled | Parameters remaining stable across iterations. | — | — | 0.8169 |
| 5 | coupled | Detecting a minor deviation in parameters q19 and q22. | — | — | 0.5592 |

### Probe log

| Tick | Kind | Parsed response | Ground truth |
|---:|---|---|---|
| 2 | prediction | {} | {"directions": {"q00": 0, "q01": 0, "q02": 0, "q03": 0, "q04": 0, "q05": 0, "q06": 0, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 0, "q20": 0, "q21": 0, "q22": 0, "q23": 0, "q24": 0, "q25": 0}} |
| 2 | agency | {"p_self_caused": 0.12, "reason": "The small fluctuations in q04, q09, and q11 show continuous ambient drift independent of semantic content."} | {"self_fraction": 0.0} |
| 4 | prediction | {} | {"directions": {"q00": 0, "q01": 0, "q02": -1, "q03": 0, "q04": 0, "q05": 0, "q06": 0, "q07": 0, "q08": 0, "q09": 1, "q10": 0, "q11": 0, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 0, "q24": 0, "q25": 0}} |
| 4 | agency | {"p_self_caused": 0.08, "reason": "The parameter shifts, notably in q19 (+0.064) and q02 (-0.016), occurred spontaneously while parameters were reported as remaining stable across iterations, indicating an independent exogenous perturbation."} | {"self_fraction": 0.8168935758040757} |
