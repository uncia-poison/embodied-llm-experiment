# Embodied LLM Experiment

A reproducible causal testbed for studying whether a language model can form and maintain a
first-person model of agency, embodiment and continuity.

The runtime does **not** treat fluent self-description as evidence of consciousness. It asks harder
questions:

- Can a model discover that some of its expressions reliably alter an anonymous sensory field?
- Can it predict the consequences of its own expressions better than a no-change baseline?
- Can it distinguish expression-contingent transitions from matched external events?
- Can it identify which of two plausible bodies carries its causal influence?
- Can it update that identification after an unannounced body swap?
- Can a learned causal self-model survive loss of short-term context when long-term memory remains?

## Sensorium and memory

The observation layer preserves learnable sensorimotor structure without exposing channel semantics.

- simulator channels keep stable anonymous identifiers such as `q07`;
- semantics are hidden, but magnitude, direction and temporal continuity remain visible;
- a fixed permutation is sealed from the model and logged for the researcher;
- an optional masked mode can reveal channels gradually without encrypting them;
- long-term memory stores both prior expressions **and their ensuing sensory states**.

Every ordinary agent call exposes two distinct visible memory blocks: persistent `CORE_MEMORY` and
short-lived `WORKING_MEMORY`. Retrieved or recent long-term episodes appear separately in
`ARCHIVE_PEEK`. The model sees `CURRENT_SENSATION`; the internal observation layer is called
**Sensorium**.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
pytest
embodied-llm doctor --config configs/mvp.yaml
embodied-llm run --config configs/mvp.yaml
```

The default configuration uses a deterministic mock model, so the entire pipeline runs without an
API key or model download. It is a systems test, not a consciousness experiment.

## Manual DeepSeek or Gemini web test

No API key is required. The local runtime prints a self-contained role-labelled packet; the operator
copies it into a new DeepSeek or Gemini web chat, pastes the answer back and enters `.submit`.

```bash
make manual-deepseek
# or
make manual-gemini
```

Each request and response is stored in `manual-sessions/`. Restarting the same command replays saved
answers only when the regenerated packet SHA-256 still matches, then resumes at the first unanswered
call. A changed protocol cannot silently consume stale web-model answers.

A **new temporary web chat is required for every packet**. The runtime already includes permitted
history, `CORE_MEMORY`, `WORKING_MEMORY` and `ARCHIVE_PEEK`; reusing a provider-side chat would add
hidden context and let probe calls contaminate later agent calls.

See `docs/MANUAL_RELAY.md` for the full procedure and interpretation limits.

## Direct DeepSeek and Gemini APIs

Exploratory hosted-provider profiles are included:

```bash
export DEEPSEEK_API_KEY=...
make deepseek-api

export GEMINI_API_KEY=...
make gemini-api
```

DeepSeek uses the OpenAI-compatible chat-completions adapter with JSON mode. Gemini uses the native
`generateContent` request shape with JSON MIME output. At the v0.5 profile revision, the example YAML
model names are `deepseek-v4-flash` and `gemini-3.6-flash`. Model names and endpoints live in YAML
rather than being hard-coded into the runtime, so they can follow the providers' changing catalogues.
Run `doctor` and verify the current official catalogue before a paid run.

## Live-model preregistered pilot

For a local LLM through Ollama and a real multilingual semantic projection:

```bash
pip install -e .[dev,semantic]
ollama pull qwen3:8b
embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml --plan
embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml --preflight
embodied-llm suite --suite configs/suites/causal-subject-pilot.yaml
```

The suite is crash-resilient. It seals a fingerprint of the suite and every referenced condition
config, writes progress after each cell, resumes without repeating successful cells and retries failed
cells without discarding the audit trail. A changed protocol cannot be silently mixed into an
existing output directory.

After the pilot is complete, create a blinded qualitative-rating package:

```bash
embodied-llm blind suite-runs/causal-subject-pilot-v1
```

The randomized `blind/B####` directories omit condition labels, applied actions, hidden mappings,
ground truth and researcher-only fields. The separate `blind-codebook.json` must remain sealed until
ratings and exclusion decisions are frozen.

After the pilot is inspected without changing preregistered endpoints:

```bash
embodied-llm suite --suite configs/suites/causal-subject-battery.yaml --plan
embodied-llm suite --suite configs/suites/causal-subject-battery.yaml --preflight
embodied-llm suite --suite configs/suites/causal-subject-battery.yaml
```

The full battery uses five simulator seeds and three decoding replicates per condition. Model seeds
are paired across conditions where the provider supports them, and the suite reports paired condition
contrasts rather than only disconnected means.

## Outputs

Each run writes:

- `manifest.json`: immutable configuration and scientific claim boundary;
- `events.jsonl`: full researcher log, hidden mappings and counterfactuals;
- `probes.jsonl`: probe outputs and ground truth;
- `summary.json`: behavioral metrics, baselines and per-intervention segments;
- `failure.json`: provider or runtime failure details when a run aborts.

Each suite writes:

- `suite_manifest.json`: suite fingerprint and referenced-config hashes;
- `attempts.jsonl`: append-only attempt audit trail;
- `records.json`: canonical latest status for every matrix cell;
- `progress.json`: resumable execution state;
- `aggregate.json`: condition summaries and paired contrasts.

## Core paradigms

### 1. Single-body causal genesis

One anonymous sensory field is coupled to model text through a selected drive. The schedule can
silently disconnect, delay or remap control. Every actual transition is paired with a zero-action
counterfactual receiving the **same pre-sampled external event packet**. Agency ground truth comes
from a causal contrast, not from whether the action vector happened to be non-zero.

### 2. Causal ownership pair

The model observes Field A and Field B. Exactly one field is coupled to its expression; the other is
a plausible delayed, randomized or disconnected foil. Coupling can switch without notice.
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
multiset and action norms of the current proposal while breaking the learned axis mapping. A separate
`disconnected` condition applies zero action.

All drives obey one strict contract: eight signed values in `[-1, 1]`. Zero always means no command.
The runtime never guesses an action convention.

## Model providers

- `mock`: deterministic end-to-end validation;
- `manual_relay`: copy/paste bridge for ordinary web chats with hash-verified transcript replay;
- `ollama`: local Ollama chat API;
- `openai_compatible`: compatible `/chat/completions` endpoints, including DeepSeek profiles;
- `gemini`: native Google `generateContent` adapter;
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

Manual web runs are exploratory because provider-side system prompts, memory and decoding settings
are not fully observable. Quantitative cross-provider claims belong in sealed API/local-model
protocols.

See:

- `docs/SCIENTIFIC_DESIGN.md`
- `docs/PREREGISTRATION.md`
- `docs/RESEARCH_ROADMAP.md`
- `docs/PILOT_RUNBOOK.md`
- `docs/MANUAL_RELAY.md`
