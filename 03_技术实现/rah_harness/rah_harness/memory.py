from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", value.lower())


@dataclass(frozen=True)
class MemoryItem:
    text: str
    score: float = 0.0


class BM25Memory:
    def __init__(self, capacity: int = 50, top_k: int = 3) -> None:
        self.capacity = capacity
        self.top_k = top_k
        self._items: list[str] = []

    def add(self, text: str) -> None:
        if text in self._items:
            self._items.remove(text)
        self._items.append(text)
        del self._items[:-self.capacity]

    def retrieve(self, query: str) -> list[MemoryItem]:
        query_terms = _tokens(query)
        if not query_terms or not self._items:
            return []
        docs = [_tokens(item) for item in self._items]
        doc_count = len(docs)
        average_length = sum(map(len, docs)) / doc_count
        scored: list[MemoryItem] = []
        for text, doc in zip(self._items, docs):
            counts = Counter(doc)
            score = 0.0
            for term in query_terms:
                df = sum(term in candidate for candidate in docs)
                if not df:
                    continue
                idf = math.log(1 + (doc_count - df + 0.5) / (df + 0.5))
                frequency = counts[term]
                score += idf * frequency * 2.5 / (frequency + 1.5 * (0.25 + 0.75 * len(doc) / average_length))
            if score:
                scored.append(MemoryItem(text, score))
        return sorted(scored, key=lambda item: (-item.score, item.text))[:self.top_k]

