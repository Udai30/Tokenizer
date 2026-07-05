"""Shared tokenizer interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Any


class Tokenizer(ABC):
    """Abstract base class for all tokenizer implementations."""

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {}
        self.inv_vocab: dict[int, str] = {}
        self.special_tokens: dict[str, int] = {}

    @abstractmethod
    def train(self, corpus: list[str], vocab_size: int, **kwargs: Any) -> None:
        """Train the tokenizer on a corpus."""

    @abstractmethod
    def encode(self, text: str) -> list[int]:
        """Convert text into token ids."""

    @abstractmethod
    def decode(self, ids: list[int]) -> str:
        """Convert token ids back into text."""

    def get_vocab(self) -> dict[str, int]:
        """Return a copy of the vocabulary mapping."""
        return dict(self.vocab)

    def save(self, path: str | Path) -> None:
        """Save tokenizer state to JSON."""
        payload = {
            "class": self.__class__.__name__,
            "vocab": self.vocab,
            "special_tokens": self.special_tokens,
        }
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path):
        """Load tokenizer state from JSON."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        obj = cls()
        obj.vocab = {str(token): int(idx) for token, idx in payload["vocab"].items()}
        obj.inv_vocab = {idx: token for token, idx in obj.vocab.items()}
        obj.special_tokens = {
            str(token): int(idx) for token, idx in payload.get("special_tokens", {}).items()
        }
        return obj
