from embodied_llm.sensorium import SensoriumEncoder
from embodied_llm.config import SensoriumConfig


def test_mapping_is_stable_and_not_named():
    encoder = SensoriumEncoder(SensoriumConfig(mode="permuted", channel_seed=3))
    first = encoder.encode(0, {"pain": 0.0, "energy": 1.0, "angle": 0.2})
    second = encoder.encode(1, {"pain": 0.1, "energy": 0.9, "angle": 0.3})
    assert first.mapping == second.mapping
    assert "pain" not in first.text
    assert "q00" in first.text
