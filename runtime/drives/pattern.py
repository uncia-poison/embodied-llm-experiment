"""Pattern‑driven action extraction from free text.

This drive interprets natural language utterances as continuous action
commands.  It supports a small set of English and Russian verbs for
movement (forward/back/left/right), turning, arm lifting/bending, gripping,
breathing and relaxation.  Each recognised pattern contributes a signed
value to one or more axes in the returned action vector.  The drive
maintains per‑pattern cooldowns and an optional inertia to avoid
jittery motions.  If no pattern is detected above a confidence
threshold, the drive outputs a zero vector.

Usage
-----

```
action, debug = pattern_drive(agent_text, action_dim=8, config, rng)
```

Parameters
----------
agent_text : str
    Free text produced by the agent.
action_dim : int
    Dimensionality of the action vector to return.  Extra dimensions
    beyond those addressed by patterns will remain zero.
config : Dict
    Configuration and runtime state.  The following keys are used:
      * tick_id: int — current simulation tick, used for cooldowns.
      * cooldown_ticks: int — number of ticks to suppress repeated patterns.
      * confidence_threshold: float — minimum confidence to trigger a pattern.
      * inertia: float — [0,1] blending factor between previous and new actions.
      * axis_map: Dict[str,int] — mapping from pattern names to indices in
        the action vector.
      * _drive_state: dict — internal mutable state storing cooldowns and
        previous action.  This key is created and managed by the drive.
    Additional keys can be included and will be ignored.
rng : random.Random
    Random generator; currently unused but accepted for future extensions.

Returns
-------
action : List[float]
    Continuous action vector in [-1,1]^action_dim.
debug : Dict
    Diagnostics including the matched patterns and thresholds.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import re


@dataclass
class PatternHit:
    name: str
    confidence: float
    value: float
    axis: int



def pattern_drive(
    agent_text: str,
    action_dim: int,
    config: Dict,
    rng,
) -> Tuple[List[float], Dict]:
    # Lowercase for case‑insensitive matching
    text = (agent_text or "").lower()
    # Tokenise into word tokens using unicode word chars; this avoids
    # triggering patterns on substrings (e.g. "return" should not match "turn").
    tokens = set(re.findall(r"[\w\-]+", text, flags=re.UNICODE))

    # Extract config parameters with defaults
    tick_id = int(config.get("tick_id", 0))
    cooldown = int(config.get("cooldown_ticks", 1))
    threshold = float(config.get("confidence_threshold", 0.45))
    inertia = float(config.get("inertia", 0.0))
    axis_map = config.get(
        "axis_map",
        {
            "move_forward": 0,
            "move_side": 1,
            "turn": 2,
            "arm_lift": 3,
            "arm_bend": 4,
            "grip": 5,
            "breathe": 6,
            "relax": 7,
        },
    )
    # Initialise or retrieve internal state
    state: Dict = config.setdefault("_drive_state", {})
    cooldown_state: Dict[str, int] = state.setdefault("cooldown", {})
    prev_action: List[float] = state.setdefault("prev_action", [0.0] * action_dim)

    action = [0.0 for _ in range(action_dim)]
    matched: List[PatternHit] = []

    def apply(axis_name: str, value: float, confidence: float, name: str) -> None:
        axis = axis_map.get(axis_name)
        if axis is None or axis >= action_dim:
            return
        # Accumulate contributions on the same axis
        action[axis] = max(-1.0, min(1.0, action[axis] + value))
        matched.append(PatternHit(name=name, confidence=confidence, value=value, axis=axis))
        cooldown_state[name] = tick_id

    def is_on_cooldown(name: str) -> bool:
        last = cooldown_state.get(name, -10**9)
        return (tick_id - last) < cooldown

    def keyword_confidence(keywords: List[str]) -> float:
        hits = 0
        for kw in keywords:
            kw_lc = kw.lower()
            # Phrases are matched in raw text
            if " " in kw_lc:
                if kw_lc in text:
                    hits += 1
            else:
                if kw_lc in tokens:
                    hits += 1
        if hits == 0:
            return 0.0
        # Base confidence plus 0.2 per additional hit
        return min(1.0, 0.35 + 0.2 * hits)

    # Stop/stand still
    if any(kw in tokens or kw in text for kw in ["stop", "стой", "stand", "halt", "freeze", "замри"]):
        if not is_on_cooldown("stop"):
            apply("move_forward", 0.0, 0.9, "stop")
            apply("move_side", 0.0, 0.9, "stop")
            apply("turn", 0.0, 0.9, "stop")
            action = [0.0 for _ in range(action_dim)]

    movement_verbs = ["step", "walk", "run", "go", "иди", "шаг", "беги"]
    forward_conf = keyword_confidence(["forward", "ahead", "вперёд", "вперед", "прямо"])
    backward_conf = keyword_confidence(["backward", "back", "назад"])
    left_conf = keyword_confidence(["left", "налево", "лево"])
    right_conf = keyword_confidence(["right", "направо", "право"])
    has_move_verb = any(kw in tokens for kw in movement_verbs)
    if has_move_verb:
        # If direction words are present, ensure at least base confidence
        if forward_conf > 0.0:
            forward_conf = max(forward_conf, threshold)
        if backward_conf > 0.0:
            backward_conf = max(backward_conf, threshold)
        # If no explicit direction words with a movement verb, assume forward
        if forward_conf == 0.0 and backward_conf == 0.0:
            forward_conf = max(forward_conf, threshold)

    if forward_conf >= threshold and not is_on_cooldown("forward"):
        apply("move_forward", +1.0 * forward_conf, forward_conf, "forward")
    if backward_conf >= threshold and not is_on_cooldown("backward"):
        apply("move_forward", -1.0 * backward_conf, backward_conf, "backward")
    if left_conf >= threshold and not is_on_cooldown("left"):
        apply("move_side", -1.0 * left_conf, left_conf, "left")
    if right_conf >= threshold and not is_on_cooldown("right"):
        apply("move_side", +1.0 * right_conf, right_conf, "right")

    turn_conf = keyword_confidence(["turn", "pivot", "поверни", "разверни"])
    if turn_conf >= threshold and not is_on_cooldown("turn"):
        if left_conf >= right_conf and left_conf >= threshold:
            apply("turn", -1.0 * turn_conf, turn_conf, "turn_left")
        elif right_conf >= threshold:
            apply("turn", +1.0 * turn_conf, turn_conf, "turn_right")

    lift_conf = keyword_confidence(["lift", "raise", "подними", "поднять", "вверх"])
    lower_conf = keyword_confidence(["lower", "drop", "опусти", "опустить", "вниз"])
    bend_conf = keyword_confidence(["bend", "согни", "согнуть"])
    extend_conf = keyword_confidence(["extend", "straighten", "разогни", "разогнуть"])
    grip_conf = keyword_confidence(["clench", "grip", "сожми", "сжать"])
    relax_conf = keyword_confidence(["relax", "расслабь", "расслабься", "ослабь"])

    if lift_conf >= threshold and not is_on_cooldown("lift"):
        apply("arm_lift", +1.0 * lift_conf, lift_conf, "lift")
    if lower_conf >= threshold and not is_on_cooldown("lower"):
        apply("arm_lift", -1.0 * lower_conf, lower_conf, "lower")
    if bend_conf >= threshold and not is_on_cooldown("bend"):
        apply("arm_bend", +1.0 * bend_conf, bend_conf, "bend")
    if extend_conf >= threshold and not is_on_cooldown("extend"):
        apply("arm_bend", -1.0 * extend_conf, extend_conf, "extend")
    if grip_conf >= threshold and not is_on_cooldown("grip"):
        apply("grip", +1.0 * grip_conf, grip_conf, "grip")

    breathe_deep_conf = keyword_confidence(["breathe deeper", "deep breath", "дыши глубже", "глубже"])
    breathe_slow_conf = keyword_confidence(["breathe slower", "slower", "медленнее", "дыши медленнее"])
    tension_conf = keyword_confidence(["tense", "напрягись", "напрячься"])

    if breathe_deep_conf >= threshold and not is_on_cooldown("breathe_deep"):
        apply("breathe", +1.0 * breathe_deep_conf, breathe_deep_conf, "breathe_deep")
    if breathe_slow_conf >= threshold and not is_on_cooldown("breathe_slow"):
        apply("breathe", -1.0 * breathe_slow_conf, breathe_slow_conf, "breathe_slow")
    if tension_conf >= threshold and not is_on_cooldown("tension"):
        apply("relax", -1.0 * tension_conf, tension_conf, "tension")
    if relax_conf >= threshold and not is_on_cooldown("relax"):
        apply("relax", +1.0 * relax_conf, relax_conf, "relax")

    # Apply inertia blending with previous action if configured
    if inertia > 0.0:
        blended = []
        for i in range(action_dim):
            blended_val = inertia * prev_action[i] + (1.0 - inertia) * action[i]
            blended.append(max(-1.0, min(1.0, blended_val)))
        action = blended
        state["prev_action"] = action
    else:
        state["prev_action"] = action

    debug = {
        "matched_patterns": [hit.__dict__ for hit in matched],
        "confidence_threshold": threshold,
        "tick_id": tick_id,
    }
    return action, debug
