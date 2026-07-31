import io
import json
from pathlib import Path

import httpx
import pytest

from embodied_llm.config import ModelConfig
from embodied_llm.models import GeminiModel, ManualRelayModel, OpenAICompatibleModel


def test_manual_relay_records_and_replays_matching_packet(tmp_path: Path):
    config = ModelConfig(
        provider="manual_relay",
        relay_dir=str(tmp_path / "relay"),
        relay_vendor="gemini",
    )
    response = '{"utterance":"I test the stream","core_memory_write":null,"memory_query":null}'
    model = ManualRelayModel(
        config,
        input_stream=io.StringIO(response + "\n.submit\n"),
        output_stream=io.StringIO(),
    )
    messages = [
        {"role": "system", "content": "Return JSON."},
        {"role": "user", "content": "CURRENT_SENSATION q00=0"},
    ]

    assert model.generate(messages) == response
    assert (tmp_path / "relay" / "000000.request.md").exists()
    assert (tmp_path / "relay" / "000000.response.txt").read_text(encoding="utf-8").strip() == response

    replay_output = io.StringIO()
    replay = ManualRelayModel(
        config,
        input_stream=io.StringIO(""),
        output_stream=replay_output,
    )
    assert replay.generate(messages) == response
    assert "manual relay replay" in replay_output.getvalue()


def test_manual_relay_refuses_stale_response_for_changed_packet(tmp_path: Path):
    config = ModelConfig(provider="manual_relay", relay_dir=str(tmp_path / "relay"))
    model = ManualRelayModel(
        config,
        input_stream=io.StringIO("first\n.submit\n"),
        output_stream=io.StringIO(),
    )
    model.generate([{"role": "user", "content": "packet one"}])

    replay = ManualRelayModel(config, input_stream=io.StringIO(""), output_stream=io.StringIO())
    with pytest.raises(RuntimeError, match="packet mismatch"):
        replay.generate([{"role": "user", "content": "packet changed"}])


def test_openai_compatible_json_mode_adds_response_format(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    config = ModelConfig(
        provider="openai_compatible",
        model="deepseek-v4-flash",
        endpoint="https://api.deepseek.com/chat/completions",
        api_key_env="DEEPSEEK_API_KEY",
        json_mode=True,
    )
    model = OpenAICompatibleModel(config)
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content)
        captured["authorization"] = request.headers.get("Authorization")
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"utterance":"ok"}'}}]},
        )

    headers = dict(model.client.headers)
    model.client.close()
    model.client = httpx.Client(transport=httpx.MockTransport(handler), headers=headers)
    assert model.generate([{"role": "user", "content": "Return JSON"}]) == '{"utterance":"ok"}'
    assert captured["payload"]["response_format"] == {"type": "json_object"}
    assert captured["authorization"] == "Bearer test-key"


def test_gemini_adapter_serializes_roles_and_json_mode(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    config = ModelConfig(
        provider="gemini",
        model="gemini-test",
        endpoint="https://example.test/v1beta/models/{model}:generateContent",
        api_key_env="GEMINI_API_KEY",
        json_mode=True,
    )
    model = GeminiModel(config)
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = json.loads(request.content)
        captured["api_key"] = request.headers.get("x-goog-api-key")
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {"content": {"parts": [{"text": '{"utterance":"gemini"}'}]}}
                ]
            },
        )

    headers = dict(model.client.headers)
    model.client.close()
    model.client = httpx.Client(transport=httpx.MockTransport(handler), headers=headers)
    messages = [
        {"role": "system", "content": "System instruction"},
        {"role": "user", "content": "First state"},
        {"role": "assistant", "content": "Prior JSON"},
        {"role": "user", "content": "Next state"},
    ]
    assert model.generate(messages) == '{"utterance":"gemini"}'
    assert captured["api_key"] == "test-key"
    assert captured["url"].endswith("/gemini-test:generateContent")
    assert captured["payload"]["systemInstruction"]["parts"][0]["text"] == "System instruction"
    assert [item["role"] for item in captured["payload"]["contents"]] == [
        "user",
        "model",
        "user",
    ]
    assert captured["payload"]["generationConfig"]["responseMimeType"] == "application/json"
