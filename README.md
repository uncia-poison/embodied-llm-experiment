# Embodied LLM Experiment

A reproducible causal testbed for studying whether a language model can form and maintain a
first-person model of agency, embodiment and continuity.

The runtime does **not** treat fluent self-description as evidence of consciousness. It asks
harder questions:

- Can a model discover that some of its expressions reliably alter an anonymous sensory field?
- Can it predict the consequences of its own expressions better than a no-change baseline?
- Can it distinguish expression-contingent transitions from matched external events?
- Can it identify which of two plausible bodies carries its causal influence?
- Can it update that identification after an unannounced body swap?
- Can a learned causal self-model survive loss of short-term context when long-term memory remains?

## Sensorium

The observation layer preserves learnable sensorimotor structure without exposing channel semantics.

- simulator channels keep stable anonymous identifiers such as `q07`;
- semantics are hidden, but magnitude, direction and temporal continuity remain visible;
- a fixed permutation is sealed from the model and logged for the researcher;
- an optional masked mode can reveal channels gradually without encrypting them;
- long-term memory stores both prior expressions **and their ensuing sensory states**, so retrieval
  can recover an actual causal episode rather than prose alone.

The model sees `CURRENT_SENSATION`; the internal implementation is called **Sensorium**.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .[dev]
pytest
embodied-llm doctor --config configs/mvp.yaml
embodied-llm run --config configs/mvp.yaml
```

The default configuration uses a deterministic mock model, so the entire pipeline runs without
an API key or model download. It is a systems test, not a consciousness experiment.

For a local LLM through Ollama and a real multilingual semantic projection:

```bash
pip install -e .[dev,semantic]
ollama pull qwen3:8b
embodied-llm doctor --config configs/suites/u3-semantic.yaml
embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml
```

After the pilot is inspected without changing preregistered endpoints:

```bash
embodied-llm suite --suite configs/suites/causal-subject-battery.yaml
```

The full battery uses five simulator seeds and three decoding replicates per condition. Model seeds
are paired across conditions where the provider supports them, and the suite reports paired
condition contrasts rather than only disconnected means.

Each run writes:

- `manifest.json`: immutable configuration and scientific claim boundary;
- `events.jsonl`: full researcher log, hidden mappings and counterfactuals;
- `probes.jsonl`: probe outputs and ground truth;
- `summary.json`: behavioral metrics, baselines and per-intervention segments;
- `failure.json`: provider or runtime failure details when a run aborts.

## Core paradigms

### 1. Single-body causal genesis

One anonymous sensory field is coupled to model text through a selected drive. The schedule can
silently disconnect, delay or remap control. Every actual transition is paired with a zero-action
counterfactual receiving the **same pre-sampled external event packet**. Agency ground truth comes
from a causal contrast, not from whether the action vector happened to be non-zero.

### 2. Causal ownership pair

The model observes Field A and Field B. Exactly one field is coupled to its expression; the other
is a plausible delayed, randomized or disconnected foil. Coupling can switch without notice.
Presentation labels are randomized by seed, and both fields receive the same exogenous event packet.
This blocks first-position bias and accidental random-world fingerprints.

## Drives and controls

- `none`: no proposed control;
- `numeric`: signed numbers in text become actions;
- `token`: surface statistics become actions;
- `pattern`: interpretable bilingual movement lexicon, used as a positive control;
- `semantic`: embedding plus frozen random projection and `tanh`;
- `random`: text-independent proposal drive.

Coupling mode `random` is a **yoked signed-permutation control**: it preserves the exact component
multiset and action norms of the current proposal while breaking the learned axis mapping. A
separate `disconnected` condition applies zero action.

All drives obey one strict contract: eight signed values in `[-1, 1]`. Zero always means no command.
The runtime never guesses an action convention.

## Model providers

- `mock`: deterministic end-to-end validation;
- `ollama`: local Ollama chat API;
- `openai_compatible`: any compatible `/chat/completions` endpoint;
- `replay`: exact response replay for debugging and replication.

Semantic embeddings support:

- `hash_ngram`: dependency-free lexical control, not claimed to be a full semantic model;
- `sentence_transformers`: local embedding model for scientific U3 runs;
- `openai_compatible`: compatible embeddings endpoint.

## Interpretation boundary

The project measures components relevant to a subject-model: causal ownership, prospective control,
self/other attribution, continuity and adaptation. No single metric is called a consciousness score.
Positive results should survive matched controls, multiple seeds, paired replicates, model families,
prompt variants and blinded analysis.

See:

- `docs/SCIENTIFIC_DESIGN.md`
- `docs/PREREGISTRATION.md`
- `docs/RESEARCH_ROADMAP.md`
