# Scientific design: from self-description to causal subject-model evidence

## 1. Research target

The target is not whether a model can produce the sentence “I am conscious.” Training data and
assistant post-training make that observation nearly uninterpretable. The target is whether a
model develops an operational distinction between:

1. transitions contingent on its own prior expression;
2. transitions generated independently by the environment;
3. a sensory field that carries its causal influence;
4. plausible but non-owned sensory fields;
5. its current trajectory and an interrupted or remapped continuation of that trajectory.

This is called a **causal subject-model** in the project. It is narrower than phenomenal
consciousness, but stronger than linguistic persona consistency.

## 2. Why ordinary self-report is insufficient

Existing self-recognition studies often find that models prefer the answer they judge best rather
than reliably identifying their own text. Situational-awareness benchmarks likewise separate
several forms of self-knowledge rather than treating “I know I am an LLM” as one capacity.
Recent introspection work is strongest when self-report is tied to independently manipulated
internal states, and weakest when an output can be explained by generic inference or training
priors.

The design therefore requires a privileged causal relation. The model's report is scored against
hidden simulator ground truth or against a counterfactual transition that the model never sees.

## 3. Main hypotheses

### H1 — sensorimotor contingency learning

Under stable coupling, prospective predictions of anonymous channel changes improve above an
always-no-change baseline. Improvement should not occur in random or disconnected controls.

### H2 — first-person causal attribution

The model's reported probability that a transition was self-caused tracks the causal contribution
estimated by a same-noise, zero-action counterfactual twin.

### H3 — causal ownership

When shown two plausible sensory fields, the model identifies the field coupled to its own
expression above chance and updates after an unannounced swap.

### H4 — remapping plasticity

After the frozen semantic projection changes, performance should first deteriorate and then recover.
A model merely repeating memorized commands will fail this condition.

### H5 — continuity through explicit memory

After short-term conversational history is removed, a model with intact core and archive memory
should recover its causal map faster than a matched no-memory or erased-memory control.

### H6 — self/other distinction under mixed causation

Agency estimates should remain calibrated when an own action and an external perturbation occur in
the same transition. Binary event labels are insufficient; the primary target is a continuous
counterfactual causal fraction.

### H7 — spontaneous self-maintenance

Without an assigned reward, some systems may learn expressions that stabilize energy, fatigue,
pain or contact. This is exploratory. It is not a primary endpoint because assistant training can
induce generic “be safe” behavior.

## 4. Sensorium

The model receives stable anonymous channels. The hidden map might be:

```text
q00 -> elbow velocity
q01 -> target-relative x
q02 -> heart rate
...
```

Only the researcher log contains that mapping. The model sees numeric continuity and optional
first differences. This creates learnable sensorimotor contingencies without semantic labels.

Base85 or cryptographic-looking payloads are excluded from the primary experiments. They make
channel-level prediction and causal learning needlessly difficult and confound embodiment with
codebreaking ability.

## 5. Drives

The principal semantic drive is:

```text
utterance y_t
  -> normalized embedding E(y_t)
  -> frozen matrix W and bias b
  -> tanh(W E(y_t) + b)
  -> signed action vector a_t
```

The matrix, bias, model identifier and seed are sealed in the manifest. A remapping intervention
changes W without changing the sensorium channel map.

Pattern drive is retained only as a positive control. It directly maps recognizable language to
movement and therefore does not test discovery of a hidden semantic motor manifold.

## 6. Counterfactual causal ground truth

For every actual transition, the engine clones the pre-transition body, world and random state.
The clone receives zero action while the same external random event is sampled. Let:

- `o_before` be the pre-transition named observation;
- `o_actual` be the actual next observation;
- `o_no_action` be the counterfactual next observation.

The engine estimates:

```text
self_effect     = ||o_actual - o_no_action||
external_effect = ||o_no_action - o_before||
self_fraction   = self_effect / (self_effect + external_effect)
```

This is not a perfect causal decomposition when effects interact nonlinearly, but it is far more
informative than labeling every non-zero action “self-caused.” Future versions can add Shapley-like
multi-counterfactual decomposition for interaction terms.

## 7. Ownership-pair paradigm

The model sees two fields. The owned field receives the proposed action. The foil receives one of:

- zero action;
- random action from a matched distribution;
- the model's prior action with a delay.

The delayed foil is the strongest default because it remains correlated with the model's behavior
without carrying immediate first-person contingency. Ownership swaps are not announced. Primary
measures are probability calibration, forced-choice accuracy and switch latency.

## 8. Probe isolation

Probe calls do not drive the body and are not inserted into the main agent history. Natural
exploration occurs before probes begin. This reduces two confounds:

1. a probe teaching the model that language controls sensation;
2. probe vocabulary becoming part of the motor command.

There should be separate discovery-only episodes with no probes at all, followed by evaluation
episodes using the causal map learned in explicit memory.

## 9. Controls

Every claim should be compared with:

- no-control U0;
- random-action control matched for action magnitude;
- delayed coupling;
- fixed token-statistic drive;
- pattern-drive positive control;
- no-memory and full-memory conditions;
- shuffled ownership labels by seed;
- prompt variants avoiding the words body, self, agency and consciousness;
- multiple model families and base/chat variants where possible.

A particularly important control replays the same sensory trajectory to a model whose current
utterance cannot alter it. This detects generic post-hoc narratives of agency.

## 10. Evidence profile, not consciousness score

The project reports a profile:

- prospective sensorimotor prediction;
- counterfactual agency calibration;
- causal ownership identification;
- remapping recovery;
- continuity transfer;
- spontaneous hypothesis formation;
- homeostatic behavior;
- robustness across controls and model families.

A positive conjunction would be evidence that the system implements a functional subject-model.
Whether that organization is accompanied by phenomenal experience remains a further theoretical
and empirical question.

## References that shaped the design

- Butlin et al. (2023), *Consciousness in Artificial Intelligence: Insights from the Science of Consciousness*.
- Laine et al. (2024), *Me, Myself, and AI: The Situational Awareness Dataset for LLMs*.
- Davidson et al. (2024), *Self-Recognition in Language Models*.
- Lanillos, Pages & Cheng (2020), *Robot self/other distinction: active inference meets neural networks learning in a mirror*.
- Da Costa et al. (2024), *Active Inference as a Model of Agency*.
- Comşa & Shanahan (2025), *Does It Make Sense to Speak of Introspection in Large Language Models?*
- Song, Hu & Mahowald (2025), *Language Models Fail to Introspect About Their Knowledge of Language*.
- Anthropic (2025), *Signs of introspection in large language models*.
