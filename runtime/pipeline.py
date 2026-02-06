"""End‑to‑end simulation step for the embodied LLM experiment.

This module ties together the individual subsystems into a single step
function.  Given the agent's textual output, it invokes the drive
(here ``pattern_drive``), updates the body dynamics, updates the world
state based on the body's joint angles, encodes an observation using
the SIGMA codec, and collects diagnostics.  The caller is expected
to maintain the ``BodyState`` and ``WorldState`` objects between
calls to persist the agent's embodiment.

The structure mirrors the experiment design document: agent text →
drive → body/world dynamics → observation → sigma encoding.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .body import VirtualBody, BodyState
from .world import SimpleWorld, WorldState
from .drives.pattern import pattern_drive
from .sigma import sigma_encode


@dataclass
class StepLog:
    tick_id: int
    raw_observation: List[float]
    sigma_line: str
    action: List[float]
    matched_patterns: List[Dict]
    gating_k: int
    body_summary: Dict


def step(
    agent_text: str,
    body_state: BodyState,
    world_state: WorldState,
    config: Dict,
    rng,
) -> Tuple[BodyState, WorldState, str, StepLog]:
    """Run one full simulation step.

    Parameters
    ----------
    agent_text : str
        The textual output from the agent at this tick.
    body_state : BodyState
        The current state of the body; will be modified in place.
    world_state : WorldState
        The current state of the world; will be modified in place.
    config : Dict
        Configuration and runtime parameters.  Keys such as
        ``tick_id``, ``dt``, ``action_dim`` and SIGMA gating parameters are
        consumed here and should be updated by the caller as needed.
    rng : random.Random
        Random generator used for SIGMA noise and future extensions.

    Returns
    -------
    body_state : BodyState
        Updated body state.
    world_state : WorldState
        Updated world state.
    sigma_line : str
        Encoded observation provided to the agent.
    log_record : StepLog
        Diagnostics for logging and offline analysis.
    """
    tick_id = int(config.get("tick_id", 0))
    dt = float(config.get("dt", 0.1))
    # Determine the dimensionality of the action vector; default to the length of angles
    action_dim = int(config.get("action_dim", len(body_state.angles or [])))

    # Compute the drive output based on the agent's text
    action, drive_debug = pattern_drive(agent_text, action_dim, config, rng)

    # Create transient body/world objects to use existing methods; assign provided state
    body = VirtualBody(dim=action_dim)
    body.state = body_state
    body.step(action, dt=dt)

    world = SimpleWorld()
    world.state = world_state

    # Map the first two joint angles to a 2D hand position; this is a toy
    # mapping to allow the body to interact with the world.
    angles = body.state.angles or [0.0, 0.0]
    # Simple linear mapping with bias; in a real experiment, this would
    # reflect the kinematics of an arm or end effector
    x = 0.5 + 0.3 * (angles[0] if len(angles) > 0 else 0.0)
    y = 0.0 + 0.3 * (angles[1] if len(angles) > 1 else 0.0)
    world.update((x, y))

    # Compose observation as body proprioception + world exteroception
    observation = body.observe() + list(world.observe())
    sigma_line, sigma_debug = sigma_encode(observation, tick_id, config, rng)

    log_record = StepLog(
        tick_id=tick_id,
        raw_observation=observation,
        sigma_line=sigma_line,
        action=action,
        matched_patterns=drive_debug.get("matched_patterns", []),
        gating_k=sigma_debug.revealed,
        body_summary={
            "energy": body.state.energy,
            "fatigue": body.state.fatigue,
            "pain": body.state.pain,
            "heart_rate": body.state.heart_rate,
        },
    )

    # Increment tick for next call
    config["tick_id"] = tick_id + 1
    return body.state, world.state, sigma_line, log_record
