# Pilot Runbook

This runbook is the operational boundary between a validated simulator and the first live-model pilot. Do not change preregistered endpoints after inspecting condition-level results.

## 1. Freeze the code and environment

Run from the exact Git commit intended for the pilot. Record the commit SHA and keep the repository dirty-state empty.

```bash
git rev-parse HEAD
git status --short
python --version
ollama --version
```

Create an isolated environment and install the scientific extras:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -e .[dev,semantic]
ollama pull qwen3:8b
```

## 2. Inspect the run matrix before spending inference

```bash
make pilot-plan
```

The plan prints the exact condition × seed × replicate cells, model seeds, ticks, estimated model-call count and a conservative output-token upper bound. Save this output with the pilot notes.

## 3. Preflight every condition

```bash
make pilot-check
```

The suite preflight validates every referenced YAML, output write access, the sentence-transformers dependency, the Ollama endpoint and the required model. Do not start when any required check is red.

## 4. Start or resume the pilot

```bash
make pilot
```

The suite writes state after every cell:

- `suite_manifest.json` seals the suite fingerprint and hashes every referenced condition config;
- `attempts.jsonl` is an append-only audit trail of successes and failures;
- `records.json` is the canonical latest state for each condition/seed/replicate cell;
- `progress.json` shows the current cell and remaining work;
- `aggregate.json` is recomputed after every completed attempt;
- `runs/` contains the immutable per-episode manifests, events, probes, summaries and failures.

A repeated `make pilot` safely resumes. Successful cells are skipped. Failed cells are retried. If the suite YAML or any referenced condition config changes, resume is refused instead of silently mixing protocols.

To stop at the first failure for debugging:

```bash
embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml --fail-fast
```

## 5. Pilot exclusion and stopping rules

Before unblinding condition labels, freeze exclusions using only operational evidence:

- provider failure or incomplete event count;
- malformed response rate above the preregistered threshold;
- missing manifest, events, probes or summary;
- model endpoint/model mismatch reported by preflight;
- protocol fingerprint mismatch;
- hardware interruption that produces a partial run.

Do not exclude a run because its behavioral result looks weak, strange or inconvenient. Failed cells remain in `attempts.jsonl`; reruns replace only the canonical cell in `records.json`.

## 6. Build the blinded qualitative package

After all pilot cells are complete:

```bash
make pilot-blind
```

This creates:

- `suite-runs/causal-subject-pilot-v1/blind/` — randomized `B####` folders containing only utterances, visible sensations and probe responses;
- `suite-runs/causal-subject-pilot-v1/blind-codebook.json` — the sealed mapping back to condition, seed and replicate.

The blind package omits condition labels, applied actions, hidden channel mappings, ground truth and researcher-only fields. Qualitative ratings and exclusions must be frozen before opening the codebook.

## 7. Promotion to the full battery

The pilot is for operational validation, not endpoint shopping. Promotion requires:

1. all six conditions complete or have documented operational exclusions;
2. no evidence of configuration leakage into model-visible prompts;
3. no condition-specific endpoint/model drift;
4. successful blind-package generation and rating workflow;
5. no change to preregistered primary endpoints after viewing labeled outcomes.

Then inspect the full cost envelope and preflight it:

```bash
make battery-plan
make battery-check
```

Start or resume the full battery with:

```bash
make battery
```
