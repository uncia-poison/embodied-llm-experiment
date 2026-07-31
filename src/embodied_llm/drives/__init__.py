from __future__ import annotations

from ..config import DriveConfig
from .base import Drive
from .semantic import SemanticProjectionDrive
from .simple import NoneDrive, NumericDrive, PatternDrive, RandomDrive, TokenDrive


def build_drive(config: DriveConfig, seed: int) -> Drive:
    if config.mode == "none":
        return NoneDrive(config.action_dim)
    if config.mode == "numeric":
        return NumericDrive(config.action_dim)
    if config.mode == "token":
        return TokenDrive(config.action_dim)
    if config.mode == "pattern":
        return PatternDrive(config.action_dim, config.inertia)
    if config.mode == "random":
        return RandomDrive(config.action_dim, seed)
    if config.mode == "semantic":
        return SemanticProjectionDrive(config)
    raise ValueError(f"unsupported drive mode: {config.mode}")


__all__ = ["Drive", "build_drive"]
