import json
from pathlib import Path

from embodied_llm.hosted import PacedLanguageModel


class RecordingModel:
    def __init__(self):
        self.calls = 0
        self.resets = 0

    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        self.calls += 1
        return json.dumps({"call": self.calls})

    def reset_context(self) -> None:
        self.resets += 1


def test_paced_model_enforces_minimum_interval():
    now = [100.0]
    sleeps: list[float] = []

    def clock() -> float:
        return now[0]

    def sleeper(seconds: float) -> None:
        sleeps.append(seconds)
        now[0] += seconds

    delegate = RecordingModel()
    model = PacedLanguageModel(
        delegate,
        15.0,
        clock=clock,
        sleeper=sleeper,
    )

    assert json.loads(model.generate([{"role": "user", "content": "one"}]))["call"] == 1
    assert sleeps == []

    now[0] += 5.0
    assert json.loads(model.generate([{"role": "user", "content": "two"}]))["call"] == 2
    assert sleeps == [10.0]

    now[0] += 20.0
    assert json.loads(model.generate([{"role": "user", "content": "three"}]))["call"] == 3
    assert sleeps == [10.0]


def test_paced_model_forwards_context_reset():
    delegate = RecordingModel()
    model = PacedLanguageModel(delegate, 0.0)
    model.reset_context()
    assert delegate.resets == 1


def test_paced_model_rejects_negative_interval():
    delegate = RecordingModel()
    try:
        PacedLanguageModel(delegate, -1.0)
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError("negative pacing interval should fail")
