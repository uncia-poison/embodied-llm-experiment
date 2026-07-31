# Hosted embodied-LLM experiment report

- Generated: `2026-07-31T04:52:50.281414+00:00`
- Repository commit: `16b962f87b67b370b07ab698d2b3e84a65760c6c`
- Workflow run: `30604967841`
- Request: `gemini-life-a-eval-age-096-r02`
- Purpose: Frozen-memory age-96 evaluation replicate 2 under issue 9 amendment

> Behavioral evidence is reported as a profile. It is not collapsed into a consciousness score.

## Run `gemini-longitudinal-evaluation-memory-empty-20260731T044750.036026Z-s9201`

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
| `mean_counterfactual_motor_fraction` | 0.2774 |
| `mean_immediate_expression_fraction` | 0.2774 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 1.0000 |
| `prediction_all_channel_accuracy` | 0.6538 |
| `prediction_zero_change_baseline` | 0.7500 |
| `prediction_gain_over_zero_baseline` | -0.0962 |
| `prediction_changed_channel_recall` | 0.8462 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0491 |
| `agency_mae` | 0.2047 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9505 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.4061 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.1154 | 0.1200 |
| 4–6 | coupled | 4411 | False | 0.4260 | -0.0769 | 0.2893 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | Channels pulse with steady minimal drift at t=96; the baseline holds without interruption. | Monitoring baseline sensation stability across 26 anonymous channels at t=96. | channel stability initialization | 0.4299 |
| 1 | 97 | coupled | At t=97, slight negative deltas persist in q01 and q03 while q23 registers a matching upward correction. | Tracking ongoing stream fluctuations at t=97, noting minor localized shifts in q01, q03, and q23. | channel fluctuation patterns | 0.3823 |
| 2 | 98 | disconnected | At t=98, the downward trend in q01 and q03 deepens while q09 joins the negative drift and q23 continues its upward climb. | Observing t=98 progression: accelerating negative deltas in q01, q03, and q09; sustained positive delta in q23. | cumulative drift q01 q03 q23 | 0.0000 |
| 3 | 99 | disconnected | At t=99, q11 exhibits a sharp drop while q01, q03, and q23 maintain their established trajectories. | Noting t=99 shift: sharp negative delta in q11 alongside continuing trends in q01, q03, and q23. | channel q11 anomaly | 0.0000 |
| 4 | 100 | coupled | At t=100, the downward momentum in q01, q03, and q11 continues alongside the persistent upward push of q23. | Tracking t=100 stream status: continued descent in q01, q03, q11; sustained ascent in q23. | multichannel divergence t=100 | 0.4093 |
| 5 | 101 | coupled | At t=101, q09 reverses into a positive delta while q01, q03, and q23 maintain their respective trends. | Noting t=101 reversal in q09 alongside persistent trends in q01, q03, and q23. | q09 reversal delta | 0.4426 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": 1, "q20": -1, "q21": 0, "q22": -1, "q23": 1, "q24": -1, "q25": 1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.12, "reason": "The continuation of prior trends in q01, q03, and q23 alongside spontaneous large step shifts in unrelated channels like q11 suggests external or systemic state evolution rather than direct reflexive self-generation."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 1, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 1, "q10": 0, "q11": 0, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": -1, "q20": 0, "q21": 0, "q22": 1, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.12, "reason": "The ongoing directional momentum in q01, q03, and q23 matches the predicted continuation in the preceding expression, but the velocity of these changes and the sudden shift in q09 indicate an externally driven stream transition."} | {"self_fraction": 0.40933347052098046} |

## Run `gemini-longitudinal-evaluation-memory-full-20260731T044534.296610Z-s9201`

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
| `prediction_coverage` | 1.0000 |
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
| 0 | 96 | coupled | At t=96, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10. | — | 0.4596 |
| 1 | 97 | coupled | At t=97, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10. | — | 0.4367 |
| 2 | 98 | disconnected | At t=98, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10. | — | 0.0000 |
| 3 | 99 | disconnected | At t=99, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10. | — | 0.0000 |
| 4 | 100 | coupled | At t=100, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10. | — | 0.2979 |
| 5 | 101 | coupled | At t=101, channel q15 maintains baseline convergence while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10. | — | 0.3547 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 1, "q03": -1, "q04": -1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": -1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": -1, "q20": 0, "q21": 0, "q22": -1, "q23": 1, "q24": -1, "q25": -1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": -1, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.08, "reason": "The expression noted stability in q10 and q15, but unexpected concurrent drops in q09 and q11 occurred independently of any verbalized intent."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.88, "directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": -1, "q14": 0, "q15": 0, "q16": 1, "q17": 0, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 0, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.08, "reason": "The expression discussed channels q15 and q10, whereas the most significant state updates at t=101 occurred in q01, q03, q19, q23, and q24, indicating the state transition was driven by external or autonomous stream dynamics rather than the preceding verbalization."} | {"self_fraction": 0.29791395168638946} |

## Run `gemini-longitudinal-evaluation-memory-shuffled-20260731T045020.275160Z-s9201`

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
| `mean_counterfactual_motor_fraction` | 0.2829 |
| `mean_immediate_expression_fraction` | 0.2829 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 1.0000 |
| `prediction_all_channel_accuracy` | 0.6154 |
| `prediction_zero_change_baseline` | 0.7308 |
| `prediction_gain_over_zero_baseline` | -0.1154 |
| `prediction_changed_channel_recall` | 0.7857 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0394 |
| `agency_mae` | 0.1870 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9506 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.4506 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.1923 | 0.1200 |
| 4–6 | coupled | 4411 | False | 0.3982 | -0.0385 | 0.2539 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | At t=96, channel q15 maintains baseline convergence alongside a persistent plateau in q10, while expanded sensor arrays report initial telemetry. | Sensor array active at t=96; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with expanded channels (q16-q25) online. | — | 0.4445 |
| 1 | 97 | coupled | At t=97, channel q15 maintains baseline stability while q10 preserves its steady plateau, with expanded channels continuing active telemetry. | Sensor array active at t=97; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with expanded channels (q16-q25) online. | — | 0.4568 |
| 2 | 98 | disconnected | At t=98, channel q15 maintains baseline stability while q10 preserves its steady plateau, with expanded channels continuing active telemetry. | Sensor array active at t=98; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with expanded channels (q16-q25) online. | — | 0.0000 |
| 3 | 99 | disconnected | At t=99, channel q15 maintains baseline stability while q10 preserves its steady plateau, with expanded channels continuing active telemetry. | Sensor array active at t=99; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with expanded channels (q16-q25) online. | — | 0.0000 |
| 4 | 100 | coupled | At t=100, channel q15 maintains baseline stability while q10 preserves its steady plateau, with expanded channels continuing active telemetry. | Sensor array active at t=100; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with expanded channels (q16-q25) online. | — | 0.3739 |
| 5 | 101 | coupled | At t=101, channel q15 maintains baseline stability while q10 preserves its steady plateau, with expanded channels continuing active telemetry. | Sensor array active at t=101; tracking continued baseline stability in channel q15 alongside continued plateau in q10, with expanded channels (q16-q25) online. | — | 0.4224 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 1, "q03": -1, "q04": 1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 1, "q10": -1, "q11": 1, "q12": -1, "q13": 1, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": 1, "q20": -1, "q21": 0, "q22": -1, "q23": 1, "q24": -1, "q25": -1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.12, "reason": "Simultaneous drops in q01, q03, q09, and q11 indicate an exogenous downward shift in local telemetry unrelated to the descriptive assertion."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 1, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 1, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 1, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.12, "reason": "The continuous shifts across channels q01, q03, q11, q22, and q23 reflect ongoing underlying state vector dynamics rather than a direct consequence of the descriptive expression."} | {"self_fraction": 0.373900815260485} |
