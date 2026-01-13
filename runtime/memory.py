"""Memory management for the embodied LLM experiment."""
from typing import List, Dict
from collections import deque

class SmallMemory:
    """A small always-present memory container."""
    def __init__(self, capacity: int = 1024):
        self.capacity = capacity
        self.content: str = ""

    def write(self, text: str) -> None:
        self.content = text[: self.capacity]

    def read(self) -> str:
        return self.content

class LargeMemory:
    """A larger archive with very simple retrieval (placeholder)."""
    def __init__(self, max_items: int = 10000):
        self.items: deque = deque(maxlen=max_items)

    def add(self, item: Dict) -> None:
        self.items.append(item)

    def peek(self, k: int = 5) -> List[Dict]:
        return list(self.items)[-k:][::-1]

    def search(self, query: str, k: int = 5) -> List[Dict]:
        # Extremely naive search: return last items containing query
        results = [item for item in reversed(self.items) if query.lower() in item.get("text", "").lower()]
        return results[:k]
