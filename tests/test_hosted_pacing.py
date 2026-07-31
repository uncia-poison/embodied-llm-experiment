import json

import httpx
import pytest

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


class QuotaFailureModel:
    def generate(self, messages, *, temperature=None, max_tokens=None) -> str:
        request = httpx.Request("POST", "https://example.test/generateContent")
        response = httpx.Response(
            429,
            request=request,
            headers={"Retry-After": "60"},
            json={
                "error": {
                    "code": 429,
                    "status": "RESOURCE_EXHAUSTED",
                    "message": "quota exceeded for test model",
                }
            },
        )
        status_error = httpx.HTTPStatusError(
            "too many requests",
            request=request,
            response=response,
        )
        raise RuntimeError("model endpoint failed after retries") from status_error

    def reset_context(self) -> None:
        return None


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
    with pytest.raises(ValueError, match="cannot be negative"):
        PacedLanguageModel(delegate, -1.0)


def test_paced_model_preserves_wrapped_http_quota_detail():
    model = PacedLanguageModel(QuotaFailureModel(), 0.0)
    with pytest.raises(RuntimeError) as captured:
        model.generate([{"role": "user", "content": "test"}])

    message = str(captured.value)
    assert "status=429" in message
    assert "retry_after=60" in message
    assert "RESOURCE_EXHAUSTED" in message
    assert "quota exceeded for test model" in message
