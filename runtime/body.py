"""Minimal body model for the embodied LLM experiment.

This module defines a simple virtual body consisting of a fixed number of
rotational degrees of freedom (angles) and their first derivatives
(velocities).  It also tracks a handful of scalar interoceptive variables
such as energy, fatigue, pain and heart rate.  The `VirtualBody` class
implements a simplistic dynamics update given an action vector and
provides an observation vector combining proprioception (angles and
velocities) with interoception.

Compared to the upstream version, this implementation fixes a few
practical issues:

* The `BodyState` dataclass now uses ``default_factory`` for the
  ``angles`` and ``velocities`` fields so that fresh lists are
  allocated per instance.  This avoids accidental sharing of list
  objects across bodies and protects against ``None`` values.

* Actions are normalised through a private ``_normalize_action`` method
  before being applied.  This helper pads or truncates the incoming
  action to exactly ``dim`` components, interprets vectors in the
  [0,1] range as normalised controls to be mapped to [-1,1], and
  clamps values to [-1,1].  Without this, passing short or mixed
  range actions into ``step`` could raise index errors or produce
  erratic dynamics.

* The energy/fatigue/pain/heart rate updates are slightly tuned to
  encourage agents to explore moderate effort levels rather than
  collapsing to 0 or saturating instantly.  These constants are not
  scientifically derived – they merely provide a smooth, bounded
  response for a toy world.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class BodyState:
    """Container for all low‑level state variables of the body.

    Parameters
    ----------
    t : float
        Simulation time in seconds.
    angles : List[float]
        Joint angles for each degree of freedom.  Using a ``default_factory``
        ensures that each ``BodyState`` has its own list rather than sharing
        a list across instances.  Empty lists are allowed to support
        variable dimensionality.
    velocities : List[float]
        Angular velocities (derivatives) corresponding to ``angles``.
    energy : float
        A normalised measure of available energy.  Consumed by effort and
        recovered when effort is low.
    fatigue : float
        A normalised measure of accumulated fatigue.  Increases with
        exertion and only decays slowly (here we leave recovery to the
        outside world).
    pain : float
        A simple pain accumulation term based on sustained overload.
    heart_rate : float
        Beats per minute.  Increases with exertion and low energy.
    """

    t: float = 0.0
    angles: List[float] = field(default_factory=list)
    velocities: List[float] = field(default_factory=list)
    energy: float = 1.0
    fatigue: float = 0.0
    pain: float = 0.0
    heart_rate: float = 70.0


class VirtualBody:
    """A toy kinematic body with simple first‑order dynamics."""

    def __init__(self, dim: int = 4) -> None:
        """Initialise the body with a given number of degrees of freedom.

        Parameters
        ----------
        dim : int
            Number of rotational joints.  Each joint has an angle and a
            velocity component in the state vector.  Interoceptive
            variables are not affected by this parameter.
        """
        self.dim = dim
        # Seed the state with zeros for angles/velocities and baseline
        # interoception.  Using list multiplication ensures the lists are
        # the correct length.
        self.state = BodyState(
            angles=[0.0] * dim,
            velocities=[0.0] * dim,
        )

    def _normalize_action(self, action: List[float]) -> List[float]:
        """Sanitise and normalise the incoming action vector.

        This helper ensures that the action passed to ``step`` always
        contains exactly ``self.dim`` components in the range [-1, 1].
        Incoming actions shorter than ``dim`` are padded with zeros;
        longer ones are truncated.  If all values lie in the [0,1]
        interval, they are interpreted as normalised controls and
        linearly mapped to [-1,1].  Finally, every component is clipped
        to [-1,1].

        Without this normalisation, a call to ``step`` could raise an
        ``IndexError`` (when fewer than ``dim`` values are provided) or
        silently propagate values outside the expected range, distorting
        the dynamics.
        """
        # Copy and pad or truncate to the correct length
        a = list(action or [])
        if len(a) < self.dim:
            a = a + [0.0] * (self.dim - len(a))
        else:
            a = a[: self.dim]
        # Map [0,1] → [-1,1] if all entries are in [0,1]
        if all(0.0 <= v <= 1.0 for v in a):
            a = [v * 2.0 - 1.0 for v in a]
        # Clip to [-1,1] to avoid runaway torques
        return [max(-1.0, min(1.0, v)) for v in a]

    def step(self, action: List[float], dt: float = 0.1) -> None:
        """Advance the body by one time step given an action.

        Parameters
        ----------
        action : List[float]
            Control vector for each joint.  Values in [0,1] are treated
            as normalised control signals, and values in [-1,1] are
            interpreted directly as torques.  The vector will be padded or
            truncated to exactly ``self.dim`` entries.
        dt : float
            Duration of the time step in seconds.
        """
        # Normalise the control vector to exactly dim values in [-1,1]
        normalized = self._normalize_action(action)
        # Update joint dynamics: integrate acceleration into velocity and
        # velocity into angle with simple damping (viscous friction).
        for i in range(self.dim):
            torque = normalized[i]
            accel = torque - 0.1 * self.state.velocities[i]
            self.state.velocities[i] += accel * dt
            self.state.angles[i] += self.state.velocities[i] * dt
        # Compute per‑joint effort and update interoceptive state.
        effort = sum(abs(a) for a in normalized) / self.dim
        # Decrease energy based on effort; cannot go below zero.
        self.state.energy = max(0.0, self.state.energy - effort * dt * 0.1)
        # Increase fatigue based on effort; saturates at one.
        self.state.fatigue = min(1.0, self.state.fatigue + effort * dt * 0.08)
        # Pain accumulates when effort exceeds a high threshold; decays slowly.
        overload = max(0.0, effort - 0.7)
        self.state.pain = min(1.0, self.state.pain * 0.98 + overload * 0.2)
        # Heart rate rises both with exertion and when energy is low.
        self.state.heart_rate = 60.0 + 50.0 * (effort + (1.0 - self.state.energy)) * 0.5
        # Advance simulation time
        self.state.t += dt

    def observe(self) -> List[float]:
        """Return a concatenated vector of proprioceptive and interoceptive values."""
        return (
            self.state.angles
            + self.state.velocities
            + [self.state.energy, self.state.fatigue, self.state.pain, self.state.heart_rate]
        )
