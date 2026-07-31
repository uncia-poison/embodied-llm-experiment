import random

from embodied_llm.config import WorldConfig
from embodied_llm.world import WorldModel


def test_reset_does_not_begin_in_contact():
    world = WorldModel(WorldConfig(contact_radius=0.09), random.Random(1))
    distance = ((world.state.target_position[0] - 0.7) ** 2 + world.state.target_position[1] ** 2) ** 0.5
    assert distance > 0.18
