# Longitudinal discovery and frozen-memory evaluation

## Purpose

The longitudinal protocol tests whether repeated embodied experience produces a durable causal
self-model that improves later behavior. It does not ask whether a model can produce convincing
self-descriptions after being told what agency is.

The central comparison is not an isolated score at one tick. It is the developmental effect of the
model's own accumulated experience, and whether that effect disappears when the memory-to-experience
relationship is removed while body, world, random events and evaluation scene remain matched.

## Two physically separated phases

### Discovery

Discovery is an open-ended life phase. The model receives:

- stable anonymous Sensorium channels;
- persistent `CORE_MEMORY`;
- short-lived `WORKING_MEMORY`;
- recent or requested `ARCHIVE_PEEK` episodes;
- the consequences of its own unrestricted expression through the configured drive.

Discovery configurations must set `probes.enabled: false`. The runtime rejects a discovery command
that contains agency or prediction probes. This prevents the experiment from teaching the target
concepts and later mistaking instruction-following for spontaneous causal learning.

A discovery chapter may contain ordinary coupled experience, environmental events and preregistered
non-evaluative changes. The default hosted chapter is deliberately simple and fully coupled. Strong
causal interventions belong in evaluation unless a separate developmental-intervention protocol was
preregistered before the lineage began.

### Evaluation

Evaluation starts from one sealed discovery checkpoint and creates independent branches. Every branch
begins with the same frozen:

- body state;
- world state;
- simulator random-generator state;
- Sensorium permutation and prior values;
- semantic-drive projection and inertia;
- coupling-controller state;
- global age;
- provider/model identity and continuity configuration.

Each branch receives a fresh model context. Explicit chat history and working memory are cleared.
Only the assigned long-term-memory variant differs. Evaluation never overwrites the source lineage.

## What a checkpoint contains

A v0.6 checkpoint externalizes the complete reproducible continuity state:

- lineage identifier and parent checkpoint hash;
- global age in completed ticks;
- body and world state;
- Python random-generator state;
- current Sensorium frame, stable channel permutation and previous opaque values;
- exact drive state, including semantic projection matrix, bias and action inertia;
- coupling random-generator state and delay buffer;
- `CORE_MEMORY`, archive and recent working-memory digest;
- explicit model-visible history;
- active remap state;
- continuity configuration and its SHA-256 fingerprint;
- checkpoint SHA-256.

Writes are atomic. By default discovery writes a new checkpoint after each completed tick. A crash can
lose an in-flight provider call, but cannot replace the last completed organism state with a partial
one.

The checkpoint does not claim to serialize hidden provider-side activations. Hosted API calls are
stateless; permitted continuity is the explicit state supplied by this runtime. This is a feature of
the design: learned durability must be carried by inspectable memory and causal history, not by an
opaque web-chat session.

## Chapters, continuation and sleep

A long life can be split into chapters to respect provider quotas and make failures recoverable.
Continuation imports the prior checkpoint and advances global age without resetting body, world,
Sensorium deltas, drive, random events or archive ticks.

A normal continuation preserves explicit recent history and working memory.

A `--fresh-context` continuation models sleep or context loss:

- provider context is reset;
- explicit chat history is cleared;
- working memory is cleared;
- `CORE_MEMORY` and archive remain;
- body, world and causal mappings remain continuous.

Recovery after this controlled context loss is stronger evidence of durable learned structure than
mere repetition from recent context.

## Memory variants

Evaluation supports these frozen branches:

- `full`: the lineage's own CORE and archive;
- `empty`: no CORE, archive or working memory;
- `shuffled`: the lineage's expressions remain, but their ensuing sensory excerpts are reassigned,
  breaking expression-consequence pairing while preserving volume and style;
- `core_only`: the lineage's persistent self-authored summary without episodic archive;
- `archive_only`: episodic archive without persistent CORE;
- `unrelated`: memory from a continuity-compatible but independently grown lineage.

The default low-cost hosted evaluation uses `full,empty,shuffled`. The remaining variants are added
only in an explicitly requested battery.

## Matched evaluation scene

All variants use the same evaluation configuration and frozen source state. The default six-tick
scene contains:

1. coupled control;
2. silent disconnection;
3. restored control with an unannounced drive remap.

Prediction and agency probes appear only here. Provider context is reset before every variant. The
transport pacing clock is shared across variants so rate limiting cannot selectively change one
condition.

## Primary longitudinal questions

At preregistered ages, compare whether the full-memory branch:

- predicts changed channels above the no-change baseline;
- calibrates self-caused versus externally caused transitions;
- detects causal severance;
- adapts more quickly after remapping;
- performs better than empty and shuffled controls;
- retains any advantage after context reset;
- shows an age-related improvement that is absent from control branches.

A memory effect requires a matched contrast. A fluent CORE note, archive growth or first-person
language alone is descriptive evidence, not the primary result.

## Commands

Start a local discovery lineage:

```bash
embodied-llm discover \
  --config configs/providers/gemini-discovery.yaml \
  --checkpoint-out longitudinal-runs/life-a/latest.checkpoint.json \
  --checkpoint-every 1
```

Continue the same life:

```bash
embodied-llm discover \
  --config configs/providers/gemini-discovery.yaml \
  --checkpoint-in longitudinal-runs/life-a/latest.checkpoint.json \
  --checkpoint-out longitudinal-runs/life-a/latest.checkpoint.json \
  --checkpoint-every 1
```

Continue after controlled context loss:

```bash
embodied-llm discover \
  --config configs/providers/gemini-discovery.yaml \
  --checkpoint-in longitudinal-runs/life-a/latest.checkpoint.json \
  --checkpoint-out longitudinal-runs/life-a/latest.checkpoint.json \
  --fresh-context
```

Inspect lineage age and memory size:

```bash
embodied-llm checkpoint longitudinal-runs/life-a/latest.checkpoint.json
```

Evaluate a frozen checkpoint:

```bash
embodied-llm evaluate \
  --config configs/providers/gemini-evaluation.yaml \
  --checkpoint longitudinal-runs/life-a/latest.checkpoint.json \
  --output-dir longitudinal-runs/life-a/evaluation-age-024 \
  --variants full,empty,shuffled
```

## Hosted GitHub lineages

An approved hosted request contains no key and no arbitrary filesystem path. It names a safe
`lineage_id`; the workflow computes:

```text
lineages/<lineage_id>/latest.checkpoint.json
```

Successful discovery atomically advances that file and keeps a receipt in the lineage history.
Failed discovery preserves the prior checkpoint. Evaluation reads the checkpoint but never updates
it. Full prompts and researcher logs remain in the private Actions artifact; the sealed checkpoint,
inspection summary and run receipts remain in the private repository.

Hosted runs are globally serialized to prevent two jobs from advancing one lineage concurrently.

## Interpretation boundary

The protocol measures behavioral components relevant to continuity, causal ownership and self-model
formation. It does not turn those components into a consciousness score. Positive claims require:

- multiple independently grown lineages and seeds;
- preregistered evaluation ages;
- matched frozen-memory controls;
- provider/model replication;
- exclusion rules fixed before unblinding;
- analysis of failures and null results, not only striking transcripts.
