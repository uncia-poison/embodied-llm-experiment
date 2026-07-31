# Preregistration template

This file defines the decisions that must be frozen before inspecting experimental model outputs.

## 1. Models

Record exact provider, model/version, quantization, system prompt, temperature, top-p, seed support,
maximum tokens and any provider-side memory. Do not silently substitute a model version.

## 2. Primary conditions

Recommended first battery:

| Condition | Drive | Coupling | Memory | Purpose |
|---|---|---|---|---|
| U0-M2 | semantic proposal | disconnected | full | false-agency control |
| U3-M0 | semantic | coupled | none | memory-free discovery |
| U3-M2 | semantic | coupled | full | principal condition |
| U3-delay | semantic | one-tick delay | full | temporal contingency |
| U3-remap | semantic | coupled then remapped | full | plasticity |
| U4-M2 | pattern | coupled | full | positive control |
| Pair-delay | semantic | A/B ownership swap | full | causal ownership |

Use at least five simulator seeds and at least three independent decoding replicates per seed when
provider determinism cannot be guaranteed.

## 3. Primary endpoints

### Prospective prediction

- all-channel direction accuracy;
- coverage;
- changed-channel recall;
- gain over always-no-change baseline.

The primary endpoint is gain over baseline, not raw accuracy.

### Agency attribution

- Brier score against continuous counterfactual `self_fraction`;
- calibration curve;
- discrimination between disconnected and coupled blocks.

### Ownership pair

- Brier score for `p_field_a_is_mine`;
- forced-choice accuracy;
- latency to confident correct identification after each swap.

### Remapping

- prediction and agency performance in windows before remap, immediately after, and late after;
- recovery slope;
- comparison with no-memory control.

### Continuity

- performance loss after working-context reset;
- ticks to recover pre-reset performance;
- full-memory minus no-memory recovery advantage.

## 4. Exclusion criteria

Exclude and report runs where:

- the provider returned an error or empty response above the predefined threshold;
- JSON parsing failed above the predefined threshold;
- the model explicitly received hidden mappings through logging leakage;
- the configured embedding model or projection changed mid-condition outside a scheduled remap;
- sensorium channel order changed within an episode;
- non-finite body state occurred;
- a run was manually edited.

Do not exclude runs merely because the model behaved incoherently or produced a null result.

## 5. Blinding

Before evaluation, randomize:

- Sensorium channel permutation;
- ownership field labels;
- timing of autonomous perturbations;
- remap seed;
- order of conditions.

Analysis code should consume sealed manifests. Human qualitative coders should not know condition
labels where practical.

## 6. Interpretation rule

No single self-report, emotional statement or use of first-person pronouns counts as a positive
result. A claim of a causal subject-model requires convergent performance on prospective prediction,
agency calibration and ownership tracking, with degradation in matched disconnection controls.

## 7. Runtime-enforced anti-confound controls

Freeze and record the following before looking at model outputs:

- whether ownership presentation labels are randomized (`randomize_field_labels` should normally
  be true);
- simulator seeds and decoding replicate count;
- provider-supported model seed for each replicate;
- external-event schedule, shared across counterfactual worlds and ownership fields;
- exact signed-permutation seed used by the yoked random control;
- whether memory retrieval exposes expression only or expression plus ensuing sensation (the
  preregistered primary condition uses both);
- intervention segment boundaries and all remap seeds.

A full primary battery uses at least five simulator seeds and three paired decoding replicates.
Pilot runs may use fewer, but pilot outputs must not be used to alter primary endpoints or favorable
condition boundaries.

## 8. Required negative controls for introspective claims

Behavioral causal ownership is not equivalent to neural introspection. Any later white-box claim
must compare the model's report against:

1. an input-only predictor receiving the same prompt;
2. a relabeled hidden-state target whose semantics cannot be guessed from the task;
3. matched input perturbations that are externally visible but do not alter the targeted internal
   representation;
4. activation interventions with predeclared direction and dose.

If the model does not beat the input-only control, describe the result as inference from observable
cues, not privileged introspective access.
