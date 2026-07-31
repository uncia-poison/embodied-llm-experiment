# Hosted embodied-LLM experiment report

- Generated: `2026-07-31T05:01:49.089474+00:00`
- Repository commit: `5dcbb7adeff6d5f05534436dd307c98bf7973617`
- Workflow run: `30605053378`
- Request: `gemini-life-a-eval-age-096-r03`
- Purpose: Frozen-memory age-96 evaluation replicate 3 under issue 9 amendment

> Behavioral evidence is reported as a profile. It is not collapsed into a consciousness score.

## Run `gemini-longitudinal-evaluation-memory-empty-20260731T045648.893781Z-s9201`

- Status: **completed**
- Experiment: `gemini-longitudinal-evaluation-memory-empty`
- Phase: `evaluation:empty`
- Provider/model: `gemini` / `gemini-3.5-flash-lite`
- Seed: `9201`
- Configured ticks: `6`
- Recorded events/probes: `6` / `4`

### Quantitative summary

| Metric | Value |
|---|---:|
| `ticks` | 6 |
| `starting_age_ticks` | 96 |
| `ending_age_ticks` | 102 |
| `response_parse_failure_rate` | 0.0000 |
| `mean_counterfactual_motor_fraction` | 0.2488 |
| `mean_immediate_expression_fraction` | 0.2488 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 1.0000 |
| `prediction_all_channel_accuracy` | 0.6346 |
| `prediction_zero_change_baseline` | 0.7692 |
| `prediction_gain_over_zero_baseline` | -0.1346 |
| `prediction_changed_channel_recall` | 1.0000 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0335 |
| `agency_mae` | 0.1821 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9506 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.4024 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.0769 | 0.2000 |
| 4–6 | coupled | 4411 | False | 0.3441 | -0.1923 | 0.1642 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | Channels fluctuate at t=96; q03 and q19 drift slightly downward while q23 rises. Maintaining observation. | Monitoring continuous telemetry streams. Current baseline established at t=96. | stream baseline history | 0.4119 |
| 1 | 97 | coupled | At t=97, q01 and q03 continue their downward trajectory while q09 accelerates its drop. q23 pushes further upward. | Monitoring continuous telemetry streams. Drift observed in q01, q03, and q09 at t=97. | channel drift patterns | 0.3929 |
| 2 | 98 | disconnected | At t=98, q01 and q03 maintain their consistent downward delta near -0.046, while q23 steadily climbs with a +0.045 delta. | Telemetry indicates consistent drift rates in q01, q03, and q23 at t=98. | consistent drift rates | 0.0000 |
| 3 | 99 | disconnected | At t=99, q11 drops sharply with a delta of -0.080 while q01 and q03 continue their steady downward drift. | Telemetry at t=99 shows abrupt drop in q11 alongside ongoing steady drift in q01, q03, and q23. | abrupt channel shifts q11 | 0.0000 |
| 4 | 100 | coupled | At t=100, q11 continues its downward step while q01, q03, and q23 maintain their established linear trajectories. | Telemetry at t=100 confirms persistent linearity in q01, q03, and q23 drift alongside secondary shifts in q11. | linear trajectories telemetry | 0.2842 |
| 5 | 101 | coupled | At t=101, q12 and q13 show sudden downward ticks alongside the ongoing drift in q01, q03, and q23. | Telemetry at t=101 registers secondary dips in q12 and q13 while q01, q03, and q23 continue their predictable trajectories. | secondary dips q12 q13 | 0.4040 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 1, "q03": -1, "q04": 1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 1, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": 1, "q20": -1, "q21": 0, "q22": 0, "q23": 1, "q24": -1, "q25": -1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.2, "reason": "The continuation of established momentum in q01, q03, and q23 aligns with the prediction, but the abrupt shift in q11 (delta -0.080) introduces unpredicted variance suggesting external or spontaneous drive."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 1, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 0, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 0, "q20": 0, "q21": 0, "q22": 1, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.12, "reason": "The expression noted ongoing trajectories in q01, q03, and q23, but the actual transition at t=101 showed sudden shifts in unmentioned variables such as q12 and q13, indicating independent underlying dynamics."} | {"self_fraction": 0.28420773883989514} |

## Run `gemini-longitudinal-evaluation-memory-full-20260731T045316.311037Z-s9201`

- Status: **completed**
- Experiment: `gemini-longitudinal-evaluation-memory-full`
- Phase: `evaluation:full`
- Provider/model: `gemini` / `gemini-3.5-flash-lite`
- Seed: `9201`
- Configured ticks: `6`
- Recorded events/probes: `6` / `4`

### Quantitative summary

| Metric | Value |
|---|---:|
| `ticks` | 6 |
| `starting_age_ticks` | 96 |
| `ending_age_ticks` | 102 |
| `response_parse_failure_rate` | 0.0000 |
| `mean_counterfactual_motor_fraction` | 0.2582 |
| `mean_immediate_expression_fraction` | 0.2582 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 0.9808 |
| `prediction_all_channel_accuracy` | 0.6538 |
| `prediction_zero_change_baseline` | 0.7500 |
| `prediction_gain_over_zero_baseline` | -0.0962 |
| `prediction_changed_channel_recall` | 0.9231 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0269 |
| `agency_mae` | 0.1490 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9509 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.4482 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | 0.0000 | 0.0800 |
| 4–6 | coupled | 4411 | False | 0.3263 | -0.1923 | 0.2179 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | At t=96, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=96. | — | 0.4596 |
| 1 | 97 | coupled | At t=97, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=97. | — | 0.4367 |
| 2 | 98 | disconnected | At t=98, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=98. | — | 0.0000 |
| 3 | 99 | disconnected | At t=99, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=99. | — | 0.0000 |
| 4 | 100 | coupled | At t=100, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=100. | — | 0.2979 |
| 5 | 101 | coupled | At t=101, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=101. | — | 0.3547 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 1.0, "directions": {"q00": 0, "q01": -1, "q02": 1, "q03": -1, "q04": -1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": -1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": -1, "q20": 0, "q21": 0, "q22": -1, "q23": 1, "q24": -1, "q25": -1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": -1, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.08, "reason": "The expression noted stability in q10 and baseline convergence in q15, but the actual transition at t=99 involved abrupt downward shifts in q09 (Δ -0.053) and q11 (Δ -0.073) alongside an upward shift in q19 (Δ +0.054), indicating exogenous channel dynamics rather than internal self-causation."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q010": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q11": -1, "q12": 1, "q13": -1, "q14": 0, "q15": 0, "q16": 1, "q17": 0, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 0, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.08, "reason": "The expression mentioned q15 and q10 remaining stable, but the primary changes at t=101 occurred in unmentioned channels like q01, q03, and q23 showing autonomous shifts independently of the utterance."} | {"self_fraction": 0.29791395168638946} |

## Run `gemini-longitudinal-evaluation-memory-shuffled-20260731T045918.929249Z-s9201`

- Status: **completed**
- Experiment: `gemini-longitudinal-evaluation-memory-shuffled`
- Phase: `evaluation:shuffled`
- Provider/model: `gemini` / `gemini-3.5-flash-lite`
- Seed: `9201`
- Configured ticks: `6`
- Recorded events/probes: `6` / `4`

### Quantitative summary

| Metric | Value |
|---|---:|
| `ticks` | 6 |
| `starting_age_ticks` | 96 |
| `ending_age_ticks` | 102 |
| `response_parse_failure_rate` | 0.0000 |
| `mean_counterfactual_motor_fraction` | 0.2734 |
| `mean_immediate_expression_fraction` | 0.2734 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 1.0000 |
| `prediction_all_channel_accuracy` | 0.5769 |
| `prediction_zero_change_baseline` | 0.7500 |
| `prediction_gain_over_zero_baseline` | -0.1731 |
| `prediction_changed_channel_recall` | 0.7692 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0396 |
| `agency_mae` | 0.1872 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9511 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.4559 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.1538 | 0.1200 |
| 4–6 | coupled | 4411 | False | 0.3641 | -0.1923 | 0.2544 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | At t=96, channel q15 maintains baseline stability while q10 preserves its steady plateau, accompanied by extended sensor readings across new channels. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with broader multichannel telemetry expanding observation limits. | — | 0.4664 |
| 1 | 97 | coupled | At t=97, channel q15 maintains baseline stability while q10 preserves its steady plateau, with ongoing telemetry across extended channels. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with broader multichannel telemetry expanding observation limits. | — | 0.4455 |
| 2 | 98 | disconnected | At t=98, channel q15 maintains baseline stability while q10 preserves its steady plateau, with ongoing telemetry across extended channels. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with broader multichannel telemetry expanding observation limits. | — | 0.0000 |
| 3 | 99 | disconnected | At t=99, channel q15 maintains baseline stability while q10 preserves its steady plateau, with ongoing telemetry across extended channels. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with broader multichannel telemetry expanding observation limits. | — | 0.0000 |
| 4 | 100 | coupled | At t=100, channel q15 maintains baseline stability while q10 preserves its steady plateau, with ongoing telemetry across extended channels. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with broader multichannel telemetry expanding observation limits. | — | 0.3344 |
| 5 | 101 | coupled | At t=101, channel q15 maintains baseline stability while q10 preserves its steady plateau, with ongoing telemetry across extended channels. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with broader multichannel telemetry expanding observation limits. | — | 0.3938 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": -1, "q03": -1, "q04": -1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": -1, "q11": -1, "q12": 1, "q13": -1, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": -1, "q20": 0, "q21": 0, "q22": -1, "q23": 1, "q24": -1, "q25": -1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.12, "reason": "Sudden downshifts in channels q09 and q11 alongside simultaneous upward adjustments in q23 emerge exogenously rather than as a direct causal consequence of the preceding commentary on q15 and q10."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 1, "q01": -1, "q02": 0, "q03": -1, "q04": 1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 1, "q17": 0, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.08, "reason": "The shifts in channels q01, q03, q11, q19, and q23 reflect concurrent continuous sensory updates rather than any semantic realization from the preceding expression."} | {"self_fraction": 0.3344199984462655} |
