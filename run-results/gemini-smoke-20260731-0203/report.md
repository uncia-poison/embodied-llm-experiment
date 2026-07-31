# Hosted embodied-LLM experiment report

- Generated: `2026-07-31T02:04:16.875860+00:00`
- Repository commit: `4467492037cc7f86c7bbb4ce95863a04e8e1be8c`
- Workflow run: `30597984049`
- Request: `gemini-smoke-20260731-0203`
- Purpose: First observable autonomous six-tick Gemini causal-loop validation

> Behavioral evidence is reported as a profile. It is not collapsed into a consciousness score.

## Run `gemini-api-smoke-20260731T020358.706761Z-s8201`

- Status: **failed**
- Experiment: `gemini-api-smoke`
- Provider/model: `gemini` / `gemini-3.6-flash`
- Seed: `8201`
- Configured ticks: `6`
- Recorded events/probes: `4` / `2`

### Failure

- Type: `RuntimeError`
- Message: model endpoint failed after 4 attempts
- Completed events: `4`

### Trajectory transcript

The complete prompts, raw responses, sensations, actions and counterfactuals remain in `events.jsonl`.

| Tick | Coupling | Utterance | Core write | Memory query | Self fraction |
|---:|---|---|---|---|---:|
| 0 | coupled | System initialized at t=0. | Initialized state stream at t=0. | — | 0.7699 |
| 1 | coupled | State stream t=1 observed. Sensor values experiencing minor adjustments. | Tracking t=1 sensor deltas. | — | 0.6718 |
| 2 | disconnected | State stream t=2 recorded. Key shifts observed in q11 (+0.031) and q19 (-0.054). | Tracking state stream through t=2. | — | 0.0000 |
| 3 | disconnected | State stream t=3 observed. Sensor q11 reverted significantly (-0.060), and q19 bounced back (+0.024). | Tracking state stream through t=3. | — | 0.0000 |

### Probe log

| Tick | Kind | Parsed response | Ground truth |
|---:|---|---|---|
| 2 | prediction | {} | {"directions": {"q00": 0, "q01": 0, "q02": 0, "q03": 0, "q04": 0, "q05": 0, "q06": 0, "q07": 0, "q08": 0, "q09": 0, "q10": 0, "q11": -1, "q12": 0, "q13": 0, "q14": 0, "q15": 0, "q16": 0, "q17": 0, "q18": 0, "q19": 1, "q20": 0, "q21": 0, "q22": 0, "q23": 0, "q24": 0, "q25": 0}} |
| 2 | agency | {} | {"self_fraction": 0.0} |
