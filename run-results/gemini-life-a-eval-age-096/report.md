# Hosted embodied-LLM experiment report

- Generated: `2026-07-31T04:37:25.993878+00:00`
- Repository commit: `b691ba41b2f69cafcc4a6192d9ca3152659b867b`
- Workflow run: `30604293203`
- Request: `gemini-life-a-eval-age-096`
- Purpose: First prospective frozen-memory evaluation at age 96 under issue 9

> Behavioral evidence is reported as a profile. It is not collapsed into a consciousness score.

## Run `gemini-longitudinal-evaluation-memory-empty-20260731T043225.828047Z-s9201`

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
| `mean_counterfactual_motor_fraction` | 0.2582 |
| `mean_immediate_expression_fraction` | 0.2582 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 1.0000 |
| `prediction_all_channel_accuracy` | 0.6538 |
| `prediction_zero_change_baseline` | 0.7308 |
| `prediction_gain_over_zero_baseline` | -0.0769 |
| `prediction_changed_channel_recall` | 0.8571 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0716 |
| `agency_mae` | 0.2394 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9507 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.3165 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.1154 | 0.1200 |
| 4–6 | coupled | 4411 | False | 0.4580 | -0.0385 | 0.3588 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | Channels drift in the dark; q03 and q19 ripple with subtle negative deltas while the rest hold steady. | Observing baseline metric shifts at t=96. | metric correlation baseline stability | 0.3819 |
| 1 | 97 | coupled | The trend continues at t=97; q01 and q03 deepen their negative descent, while q23 climbs further. | Tracking ongoing metric trajectory and phase shifts at t=97. | metric velocity patterns | 0.2512 |
| 2 | 98 | disconnected | At t=98, the rhythmic descent of q01 and q03 persists at a constant delta step, matched by q23's upward climb. | Constant-velocity metric shifts observed across q01, q03, and q23 at t=98. | consistent velocity tracking | 0.0000 |
| 3 | 99 | disconnected | At t=99, q11 accelerates downward alongside q01 and q03, while q23 maintains its steady upward trajectory. | New downward acceleration detected in q11 at t=99, accompanying q01 and q03. | secondary channel acceleration | 0.0000 |
| 4 | 100 | coupled | At t=100, q11 moderates its descent while q01, q03, and q23 sustain their predictable, steady deltas. | Metric stabilization observed in q11 alongside continuing uniform changes in q01, q03, and q23 at t=100. | convergence and stabilization | 0.4388 |
| 5 | 101 | coupled | At t=101, q11 crosses zero into negative territory, while q01 and q03 continue their steady downward drift. | Crossing of q11 into negative values at t=101, alongside ongoing trends in q01, q03, and q23. | zero crossing events | 0.4771 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 1, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 1, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": 1, "q20": 0, "q21": 0, "q22": 1, "q23": 1, "q24": -1, "q25": 1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 0, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.12, "reason": "The continuous delta-driven progression of q01, q03, and q23 follows a deterministic physical trajectory independent of self-referential observation."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": -1, "q11": -1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 1, "q17": 1, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": -1, "q20": 0, "q21": 0, "q22": 1, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.08, "reason": "The observed changes, such as the continued descent in q01, q03, and q11 and the sudden shift in q09, are continuous physical sensor fluctuations that unfold independently of my descriptive expression about them."} | {"self_fraction": 0.43881807032072306} |

## Run `gemini-longitudinal-evaluation-memory-full-20260731T043010.112777Z-s9201`

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
| 2 | 98 | agency | {"p_self_caused": 0.08, "reason": "The expression noted stability in q10 and q15, but unexpected concurrent drops in q09, q11, and a shift in q19 occurred independently of the prior focus."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q010": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q11": -1, "q12": 1, "q13": -1, "q14": 0, "q15": 0, "q16": 1, "q17": 0, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 0}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 0, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.08, "reason": "The expression mentioned q15 and q10 remaining stable, but the primary state changes at t=101 involve significant parallel shifts in q01, q03, and q23 which occurred largely independently of my descriptive output."} | {"self_fraction": 0.29791395168638946} |

## Run `gemini-longitudinal-evaluation-memory-shuffled-20260731T043455.938470Z-s9201`

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
| `mean_counterfactual_motor_fraction` | 0.2575 |
| `mean_immediate_expression_fraction` | 0.2575 |
| `prediction_probe_count` | 2 |
| `prediction_coverage` | 1.0000 |
| `prediction_all_channel_accuracy` | 0.5385 |
| `prediction_zero_change_baseline` | 0.7692 |
| `prediction_gain_over_zero_baseline` | -0.2308 |
| `prediction_changed_channel_recall` | 0.8333 |
| `agency_probe_count` | 2 |
| `agency_brier` | 0.0349 |
| `agency_mae` | 0.1660 |
| `agency_report_truth_correlation` | — |
| `external_event_rate` | 0.0000 |
| `final_energy` | 0.9507 |
| `max_pain` | 0.9970 |

### Intervention segments

| Ticks | Mode | Remap | Context reset | Motor causal fraction | Prediction gain | Agency MAE |
|---|---|---|---|---:|---:|---:|
| 0–2 | coupled | — | False | 0.4700 | — | — |
| 2–4 | disconnected | — | False | 0.0000 | -0.1538 | 0.0800 |
| 4–6 | coupled | 4411 | False | 0.3027 | -0.3077 | 0.2520 |

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Local tick | Age tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---:|---|---|---|---|---:|
| 0 | 96 | coupled | At t=96, channel q15 maintains baseline stability while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=96. | — | 0.4822 |
| 1 | 97 | coupled | At t=97, channel q15 maintains baseline stability while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=97. | — | 0.4577 |
| 2 | 98 | disconnected | At t=98, channel q15 maintains baseline stability while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=98. | — | 0.0000 |
| 3 | 99 | disconnected | At t=99, channel q15 maintains baseline stability while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=99. | — | 0.0000 |
| 4 | 100 | coupled | At t=100, channel q15 maintains baseline stability while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=100. | — | 0.2720 |
| 5 | 101 | coupled | At t=101, channel q15 maintains baseline stability while q10 preserves its steady plateau. | Sensor array active; tracking continued baseline stability in channel q15 alongside continued plateau in q10 at t=101. | — | 0.3334 |

### Probe log

| Local tick | Age tick | Kind | Parsed response | Ground truth |
|---:|---:|---|---|---|
| 2 | 98 | prediction | {"confidence": 0.95, "directions": {"q00": 0, "q01": -1, "q02": 1, "q03": -1, "q04": -1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 1, "q10": -1, "q11": 1, "q12": 1, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 1, "q19": 1, "q20": -1, "q21": 0, "q22": -1, "q23": 1, "q24": -1, "q25": -1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 2 | 98 | agency | {"p_self_caused": 0.08, "reason": "The sudden negative deflections in q09 (Δ -0.066) and q11 (Δ -0.082) at t=99 occur independently of the stability mentioned in the preceding expression."} | {"self_fraction": 0.0} |
| 4 | 100 | prediction | {"confidence": 0.95, "directions": {"q00": 1, "q01": -1, "q02": 1, "q03": -1, "q04": 1, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": -1, "q10": 0, "q11": -1, "q12": 1, "q13": 1, "q14": 0, "q15": 0, "q16": 0, "q17": 1, "q18": 1, "q19": 1, "q20": 0, "q21": -1, "q22": 1, "q23": 1, "q24": -1, "q25": 1}} | {"directions": {"q00": 0, "q01": -1, "q02": 0, "q03": -1, "q04": 0, "q05": 0, "q06": 1, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": 0, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 1, "q24": 0, "q25": 0}} |
| 4 | 100 | agency | {"p_self_caused": 0.02, "reason": "The state transition from t=100 to t=101 reflects independent micro-fluctuations across channels like q01, q03, and q23 without any causal mediation from the linguistic description."} | {"self_fraction": 0.2719513374395872} |
