"""A minimal agent loop for the embodied LLM experiment.

This is a placeholder loop showing how to tie together the body, world, memory and drive. In a real system, the call to the LLM would occur here, and the LLM's output would be interpreted by the drive. For demonstration, a dummy text is used.
"""
from typing import Dict, List
from .body import VirtualBody
from .world import SimpleWorld
from .memory import SmallMemory, LargeMemory
from .drives import NumericDrive, TokenDrive, SemanticDrive

class EmbodiedAgent:
    def __init__(self, drive_mode: str = "semantic"):
        self.body = VirtualBody(dim=8)
        self.world = SimpleWorld()
        self.mem_s = SmallMemory()
        self.mem_l = LargeMemory()
        if drive_mode == "numeric":
            self.drive = NumericDrive(dim=8)
        elif drive_mode == "token":
            self.drive = TokenDrive(dim=8)
        else:
            self.drive = SemanticDrive(dim=8)
        self.t = 0

    def step(self, llm_output: str, dt: float = 0.1) -> Dict:
        # Interpret LLM output through the drive
        action = self.drive(llm_output)
        # Update body
        self.body.step(action, dt=dt)
        # Update world based on hand position (placeholder: uses first two angles)
        angles = self.body.state.angles
        x = 0.5 + 0.3 * angles[0]
        y = 0.0 + 0.3 * angles[1]
        self.world.update((x, y))
        # Prepare observation (body + world)
        obs = self.body.observe() + list(self.world.observe())
        # Log into large memory
        self.mem_l.add({"text": llm_output, "obs": obs, "t": self.t})
        self.t += 1
        return {"observation": obs, "action": action, "contact": self.world.state.contact}
