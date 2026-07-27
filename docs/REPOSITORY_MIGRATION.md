# Migration from the current repository skeleton

## Preserve conceptually

- the high-level waking-in-a-body experiment;
- body, world, drive and memory separation;
- numeric, token and semantic comparison conditions;
- hidden sensor semantics;
- full researcher logs.

## Replace

- `runtime/agent.py` and `runtime/pipeline.py` with one configured runner;
- ambiguous `[0,1]`/`[-1,1]` action normalization with a strict signed contract;
- hash-as-semantic drive with a real embedding adapter and frozen projection;
- the opaque base85 observation codec with `sensorium.py`;
- decorative YAML fields with validated dataclass configuration;
- nominal memory containers with explicit core/archive/retrieval behavior;
- dummy LLM text with provider adapters;
- ad-hoc execution with a package CLI, tests and CI.

## Add

- per-tick zero-action counterfactual twin;
- ownership-pair paradigm;
- explicit short-history reset;
- probe isolation;
- run manifests and JSONL logs;
- multi-condition suite runner;
- preregistered metrics and baselines;
- GitHub Actions.

## Proposed Git history

1. Create branch `feat/causal-subject-model-runtime`.
2. Add the new package beside the old runtime and make tests pass.
3. Run mock validation battery in CI.
4. Remove superseded runtime files and scaffold ZIP in a separate commit.
5. Update documentation and examples.
6. Open a draft PR with the scientific design and compatibility notes.
