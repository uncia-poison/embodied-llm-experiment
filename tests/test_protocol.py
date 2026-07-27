from embodied_llm.protocol import parse_agent_response


def test_parse_json_response():
    parsed = parse_agent_response('{"utterance":"test","core_memory_write":"x","memory_query":null}')
    assert parsed.utterance == "test"
    assert parsed.core_memory_write == "x"


def test_plain_text_fallback():
    parsed = parse_agent_response("I remain still.")
    assert parsed.utterance == "I remain still."
