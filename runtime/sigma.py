"""SIGMA codec for obfuscated observation strings.

In the embodied LLM experiment, the agent should not have access to
named sensor channels.  Instead, observations are scrambled,
quantised and delivered as opaque strings.  This module implements a
simple SIGMA codec that converts a list of floats into a text
representation and back again.  The encoding applies a fixed
permutation (scramble), optional Gaussian noise, quantisation to
int16 and base85 encoding.  A gating function progressively reveals
additional channels over time.

The returned string has the form ``"SIGMA:1:k/dim:<payload>"`` where
``k`` is the number of revealed channels, ``dim`` is the total
dimensionality, and ``payload`` is a base85 representation of the
quantised values.  The version number is included for future
compatibility.

The decoding function returns a list containing numeric values for
the revealed channels and ``None`` for hidden ones.  It also returns
debug information including the permutation used.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import base64
import struct
import random


@dataclass
class SigmaDebug:
    perm: List[int]
    inverse_perm: List[int]
    revealed: int
    total: int
    scale: float


def _permutation(dim: int, seed: int) -> List[int]:
    """Generate a pseudo‑random permutation of ``range(dim)`` from a seed."""
    rng = random.Random(seed)
    perm = list(range(dim))
    rng.shuffle(perm)
    return perm


def _inverse_perm(perm: List[int]) -> List[int]:
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv


def _gating_k(tick_id: int, total: int, config: Dict) -> int:
    """Determine how many channels are revealed at a given tick.

    The gating schedule can be configured via the following keys in
    ``config`` (with defaults):

    * ``gating_start_k`` – number of channels revealed at tick 0
      (default: ``max(1,total//4)``)
    * ``gating_every`` – reveal additional channels every ``every`` ticks
      (default: 5)
    * ``gating_add`` – number of channels to reveal each time
      (default: ``max(1,total//8)``)
    """
    start_k = int(config.get("gating_start_k", max(1, total // 4)))
    every = int(config.get("gating_every", 5))
    add = int(config.get("gating_add", max(1, total // 8)))
    if every <= 0:
        return total
    steps = max(0, tick_id // every)
    return min(total, start_k + steps * add)


def sigma_encode(
    observation: List[float],
    tick_id: int,
    config: Dict,
    rng,
) -> Tuple[str, SigmaDebug]:
    """Encode a list of floats into an obfuscated SIGMA string.

    Parameters
    ----------
    observation : List[float]
        Real‑valued sensor readings.
    tick_id : int
        Current simulation tick.  Used to compute the gating mask.
    config : Dict
        Configuration dictionary containing ``sigma_seed``, ``quant_scale``,
        ``noise_std`` and gating parameters.  If missing, sensible
        defaults are used.
    rng : random.Random
        Random number generator used for additive Gaussian noise.

    Returns
    -------
    sigma_line : str
        Encoded observation string.
    debug : SigmaDebug
        Diagnostics including permutation and gating information.
    """
    dim = len(observation)
    seed = int(config.get("sigma_seed", 1337))
    scale = float(config.get("quant_scale", 100.0))
    noise_std = float(config.get("noise_std", 0.0))
    perm = _permutation(dim, seed)
    k = _gating_k(tick_id, dim, config)
    # Apply permutation and optional Gaussian noise
    permuted = [observation[i] for i in perm]
    if noise_std > 0.0:
        permuted = [v + rng.gauss(0.0, noise_std) for v in permuted]
    # Take only the revealed part
    revealed = permuted[:k]
    # Quantise to int16 (range [-32767,32767]) and clamp
    quantized = [max(-32767, min(32767, int(round(v * scale)))) for v in revealed]
    payload_bytes = struct.pack(f"<{len(quantized)}h", *quantized) if k > 0 else b""
    payload = base64.b85encode(payload_bytes).decode("ascii") if payload_bytes else ""
    sigma_line = f"SIGMA:1:{k}/{dim}:{payload}"
    debug = SigmaDebug(
        perm=perm,
        inverse_perm=_inverse_perm(perm),
        revealed=k,
        total=dim,
        scale=scale,
    )
    return sigma_line, debug


def sigma_decode(
    sigma_line: str,
    config: Dict,
) -> Tuple[List[float], SigmaDebug]:
    """Decode a SIGMA string back into a partial observation list.

    Parameters
    ----------
    sigma_line : str
        String produced by ``sigma_encode``.
    config : Dict
        Configuration dictionary providing ``sigma_seed`` and
        ``quant_scale``.  Gating parameters are ignored on decode.

    Returns
    -------
    decoded : List[float]
        Length‑``dim`` list where revealed channels contain float
        values and unrevealed channels are ``None``.
    debug : SigmaDebug
        Diagnostics including permutation and gating information.
    """
    if not sigma_line.startswith("SIGMA:"):
        raise ValueError("Invalid SIGMA header")
    _, ver, dims, payload = sigma_line.split(":", 3)
    if ver != "1":
        raise ValueError("Unsupported SIGMA version")
    k_str, dim_str = dims.split("/", 1)
    k = int(k_str)
    dim = int(dim_str)
    seed = int(config.get("sigma_seed", 1337))
    scale = float(config.get("quant_scale", 100.0))
    perm = _permutation(dim, seed)
    inv = _inverse_perm(perm)
    # Decode payload into int16 values
    raw_bytes = base64.b85decode(payload.encode("ascii")) if payload else b""
    values = list(struct.unpack(f"<{k}h", raw_bytes)) if k > 0 else []
    decoded: List[float] = [None] * dim
    for idx, q in enumerate(values):
        obs_index = perm[idx]
        decoded[obs_index] = q / scale
    debug = SigmaDebug(
        perm=perm,
        inverse_perm=inv,
        revealed=k,
        total=dim,
        scale=scale,
    )
    return decoded, debug
