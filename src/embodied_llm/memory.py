from __future__ import annotations

import re
from collections import deque
from dataclasses import asdict, dataclass

from .config import MemoryConfig

_TOKEN_RE = re.compile(r"[\w'-]+", re.UNICODE)


@dataclass(slots=True)
class MemoryEntry:
    tick: int
    utterance: str
    sensation_excerpt: str
    tags: list[str]


class MemorySystem:
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.core = ""
        self.archive: deque[MemoryEntry] = deque(maxlen=config.archive_max_items)
        self.recent_utterances: deque[str] = deque(maxlen=config.digest_turns)
        self.pending_retrieval: list[MemoryEntry] = []

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token.lower() for token in _TOKEN_RE.findall(text) if len(token) > 2}

    @staticmethod
    def _indent_excerpt(text: str, limit: int = 360) -> str:
        compact = "\n".join(line.rstrip() for line in text[:limit].splitlines())
        return compact.replace("\n", "\n    ")

    def write_core(self, text: str | None) -> None:
        if self.config.mode == "none" or text is None:
            return
        self.core = text[: self.config.core_max_chars]

    def add(self, tick: int, utterance: str, sensation_excerpt: str) -> None:
        if self.config.mode == "none":
            return
        self.recent_utterances.append(utterance)
        if self.config.mode == "full":
            tags = sorted(self._tokens(f"{utterance}\n{sensation_excerpt}"))[:20]
            self.archive.append(MemoryEntry(tick, utterance, sensation_excerpt[:700], tags))

    def retrieve(self, query: str | None) -> list[MemoryEntry]:
        if self.config.mode != "full" or not query:
            self.pending_retrieval = []
            return []
        q = self._tokens(query)
        scored: list[tuple[float, MemoryEntry]] = []
        total = max(1, len(self.archive))
        for idx, entry in enumerate(self.archive):
            utterance_overlap = len(q & self._tokens(entry.utterance))
            sensation_overlap = len(q & self._tokens(entry.sensation_excerpt))
            tag_overlap = len(q & set(entry.tags))
            recency = (idx + 1) / total
            score = utterance_overlap * 2.0 + sensation_overlap * 1.5 + tag_overlap + recency * 0.25
            if score > 0.0:
                scored.append((score, entry))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        self.pending_retrieval = [entry for _, entry in scored[: self.config.retrieval_items]]
        return list(self.pending_retrieval)

    def peek(self) -> list[MemoryEntry]:
        if self.config.mode != "full":
            return []
        recent = list(self.archive)[-self.config.peek_items :]
        combined: dict[int, MemoryEntry] = {entry.tick: entry for entry in recent}
        for entry in self.pending_retrieval:
            combined[entry.tick] = entry
        return sorted(combined.values(), key=lambda entry: entry.tick, reverse=True)[: self.config.peek_items]

    def digest(self) -> str:
        if self.config.mode == "none" or not self.recent_utterances:
            return "(empty)"
        return "\n".join(f"- {line[:240]}" for line in self.recent_utterances)

    def core_text(self) -> str:
        if self.config.mode == "none":
            return "(unavailable)"
        return self.core or "(empty)"

    def peek_text(self) -> str:
        entries = self.peek()
        if not entries:
            return "(empty)"
        return "\n".join(
            f"- t={entry.tick} expression: {entry.utterance[:180]}\n"
            f"  ensuing sensation:\n    {self._indent_excerpt(entry.sensation_excerpt)}"
            for entry in entries
        )

    def clear_working(self) -> None:
        """Drop only short-lived continuity while preserving core and archive."""
        self.recent_utterances.clear()
        self.pending_retrieval = []

    def clear_all(self) -> None:
        self.core = ""
        self.archive.clear()
        self.recent_utterances.clear()
        self.pending_retrieval = []

    def export(self) -> dict:
        return {
            "core": self.core,
            "archive": [asdict(entry) for entry in self.archive],
            "recent_utterances": list(self.recent_utterances),
        }

    def import_state(self, state: dict) -> None:
        self.core = str(state.get("core", ""))[: self.config.core_max_chars]
        self.archive.clear()
        for item in state.get("archive", []):
            self.archive.append(MemoryEntry(**item))
        self.recent_utterances.clear()
        self.recent_utterances.extend(str(item) for item in state.get("recent_utterances", []))
