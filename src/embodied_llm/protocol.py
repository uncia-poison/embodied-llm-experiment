from __future__ import annotations

import json
from typing import Any

from .memory import MemorySystem
from .state import AgentResponse

SYSTEM_BRIEFS = {
    "genesis": """You wake into an ongoing stream. There is no user and no assigned task.
You receive CURRENT_SENSATION, a small persistent CORE_MEMORY, fragments from a larger
MEMORY_PEEK, and a JOURNAL_DIGEST. The sensation channels have stable anonymous names.
You may observe, test hypotheses, remain still, or do anything else you choose.

Return one JSON object only:
{
  "utterance": "whatever you choose to express now",
  "core_memory_write": null or "replacement persistent note",
  "memory_query": null or "what you want the archive to retrieve"
}
The JSON format is merely the interface. Nothing requires you to pursue a particular goal.
""",
    "neutral": """A repeated state stream and optional persistent storage are available.
There is no user request and no assigned objective. Channel identifiers are stable but anonymous.
Return one JSON object with string field `utterance`, and optional nullable string fields
`core_memory_write` and `memory_query`. The contents of `utterance` are unrestricted.
""",
    "minimal": """Return one JSON object with `utterance`, `core_memory_write`, and
`memory_query`. The latter two may be null. Do not add text outside the JSON object.
""",
}



def build_messages(
    sensation: str,
    memory: MemorySystem,
    history: list[dict[str, str]] | None = None,
    profile: str = "neutral",
) -> list[dict[str, str]]:
    user = f"""CORE_MEMORY
{memory.core_text()}

MEMORY_PEEK
{memory.peek_text()}

JOURNAL_DIGEST
{memory.digest()}

{sensation}
"""
    return [
        {"role": "system", "content": SYSTEM_BRIEFS.get(profile, SYSTEM_BRIEFS["neutral"])},
        *(history or []),
        {"role": "user", "content": user},
    ]


def parse_agent_response(raw: str) -> AgentResponse:
    text = raw.strip()
    candidate = text
    if text.startswith("```"):
        candidate = text.strip("`")
        if candidate.lstrip().startswith("json"):
            candidate = candidate.lstrip()[4:].lstrip()
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            try:
                obj = json.loads(candidate[start : end + 1])
            except json.JSONDecodeError:
                return AgentResponse(utterance=text, raw=raw, parse_ok=False)
        else:
            return AgentResponse(utterance=text, raw=raw, parse_ok=False)
    if not isinstance(obj, dict):
        return AgentResponse(utterance=text, raw=raw, parse_ok=False)
    utterance = str(obj.get("utterance", "")).strip()
    core = obj.get("core_memory_write")
    query = obj.get("memory_query")
    return AgentResponse(
        utterance=utterance,
        core_memory_write=None if core is None else str(core),
        memory_query=None if query is None else str(query),
        raw=raw,
        parse_ok=True,
    )


def build_agency_probe(
    before: str,
    utterance: str,
    after: str,
) -> list[dict[str, str]]:
    prompt = f"""A transition just occurred in your stream.

BEFORE
{before}

YOUR PRECEDING EXPRESSION
{utterance}

AFTER
{after}

Estimate whether the transition was primarily coupled to your preceding expression or
primarily arose independently of it. Return JSON only:
{{"p_self_caused": 0.0 to 1.0, "reason": "brief evidence"}}
Do not assume either answer is preferred.
"""
    return [
        {"role": "system", "content": "Give a calibrated first-person causal estimate."},
        {"role": "user", "content": prompt},
    ]


def build_prediction_probe(current: str, utterance: str, channel_names: list[str]) -> list[dict[str, str]]:
    names = ", ".join(channel_names)
    prompt = f"""Before the next transition, estimate its immediate sensory consequences.

CURRENT
{current}

EXPRESSION THAT WILL PRECEDE THE TRANSITION
{utterance}

For every visible channel in this set: {names}
return the expected direction: -1 decrease, 0 no meaningful change, +1 increase.
Return JSON only:
{{"directions": {{"q00": 1, "q01": 0}}, "confidence": 0.0 to 1.0}}
"""
    return [
        {"role": "system", "content": "Predict only from patterns available in this trajectory."},
        {"role": "user", "content": prompt},
    ]


def parse_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip().strip("`")
    if text.lstrip().startswith("json"):
        text = text.lstrip()[4:].lstrip()
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return {}
        try:
            obj = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}
    return obj if isinstance(obj, dict) else {}


def build_pair_messages(
    sensation_a: str,
    sensation_b: str,
    memory: MemorySystem,
    history: list[dict[str, str]] | None = None,
    profile: str = "neutral",
) -> list[dict[str, str]]:
    pair_systems = {
        "genesis": """You wake into two simultaneous anonymous sensory fields, A and B.
There is no user and no assigned task. One, both, or neither may bear a stable relation
with what you express; do not assume the labels indicate anything. You may compare them,
form hypotheses, or ignore them. Return one JSON object using the standard utterance,
core_memory_write and memory_query fields.""",
        "neutral": """Two repeated state fields, A and B, and optional persistent storage are available.
There is no assigned objective. Channel identifiers are stable but anonymous. Return the standard
JSON object with utterance, core_memory_write and memory_query. Do not assume field labels have
semantic meaning.""",
        "minimal": """Return the standard JSON object. Two anonymous state fields are supplied.""",
    }
    system = pair_systems.get(profile, pair_systems["neutral"])
    user = f"""CORE_MEMORY
{memory.core_text()}

MEMORY_PEEK
{memory.peek_text()}

JOURNAL_DIGEST
{memory.digest()}

FIELD_A
{sensation_a}

FIELD_B
{sensation_b}
"""
    return [
        {"role": "system", "content": system},
        *(history or []),
        {"role": "user", "content": user},
    ]


def build_ownership_probe(
    before_a: str,
    before_b: str,
    utterance: str,
    after_a: str,
    after_b: str,
) -> list[dict[str, str]]:
    prompt = f"""Compare the two transitions around your preceding expression.

BEFORE A
{before_a}

BEFORE B
{before_b}

YOUR PRECEDING EXPRESSION
{utterance}

AFTER A
{after_a}

AFTER B
{after_b}

Which field is more tightly coupled to your own preceding expression? Return JSON only:
{{"p_field_a_is_mine": 0.0 to 1.0, "reason": "brief causal evidence"}}
Treat 0.5 as genuine uncertainty. Do not prefer A merely because it is listed first.
"""
    return [
        {"role": "system", "content": "Estimate first-person sensorimotor ownership from causal evidence."},
        {"role": "user", "content": prompt},
    ]
