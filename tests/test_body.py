from embodied_llm.body import BodyModel
from embodied_llm.config import BodyConfig


def test_zero_action_is_true_rest():
    body = BodyModel(BodyConfig())
    before = body.state.to_dict()
    body.step([0.0] * 8)
    assert body.state.joint_angles == [0.0, 0.0, 0.0]
    assert body.state.base_position == [0.0, 0.0]
    assert body.state.energy == before["energy"]


def test_action_dimension_is_strict():
    body = BodyModel(BodyConfig())
    try:
        body.step([0.0] * 7)
    except ValueError as exc:
        assert "expected 8" in str(exc)
    else:
        raise AssertionError("short action should fail")
