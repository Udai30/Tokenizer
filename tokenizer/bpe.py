"""Character-level Byte Pair Encoding."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .base import Tokenizer
from .pretokenize import whitespace_split
from .utils import build_vocab_from_words, get_pair_stats, merge_word


class BPE(Tokenizer):
    """A simple, deterministic character-level BPE tokenizer."""

    def __init__(self) -> None:
        super().__init__()
        self.merges: list[tuple[str, str]] = []
        self.merge_ranks: dict[tuple[str, str], int] = {}
        self.end_of_word = "</w>"
        self.unknown_token = "<unk>"

    def train(self, corpus: list[str], vocab_size: int, **kwargs: Any) -> None:
        """Learn merges from a corpus of strings."""
        words: dict[tuple[str, ...], int] = Counter()
        for line in corpus:
            for word in whitespace_split(line):
                if word:
                    words[tuple(word) + (self.end_of_word,)] += 1

        vocab = build_vocab_from_words(words)
        vocab.add(self.unknown_token)

        self.merges = []
        while len(vocab) < vocab_size:
            pair_stats = get_pair_stats(words)
            if not pair_stats:
                break

            best_pair = max(pair_stats, key=lambda pair: (pair_stats[pair], pair))
            self.merges.append(best_pair)
            vocab.add(best_pair[0] + best_pair[1])
            words = {merge_word(word, best_pair): freq for word, freq in words.items()}

        self.merge_ranks = {pair: rank for rank, pair in enumerate(self.merges)}
        self.vocab = {token: idx for idx, token in enumerate(sorted(vocab))}
        self.inv_vocab = {idx: token for token, idx in self.vocab.items()}
        self.special_tokens = {self.unknown_token: self.vocab[self.unknown_token]}

    def _apply_merges(self, symbols: tuple[str, ...]) -> tuple[str, ...]:
        """Replay learned merges in rank order."""
        current = symbols
        for pair in self.merges:
            current = merge_word(current, pair)
        return current

    def _tokenize_word(self, word: str) -> list[str]:
        """Split a single word into BPE symbols."""
        symbols = tuple(word) + (self.end_of_word,)
        return list(self._apply_merges(symbols))

    def encode(self, text: str) -> list[int]:
        """Convert text to token ids."""
        ids: list[int] = []
        unk_id = self.special_tokens.get(self.unknown_token)
        for word in whitespace_split(text):
            for token in self._tokenize_word(word):
                token_id = self.vocab.get(token, unk_id)
                if token_id is None:
                    raise ValueError(f"Tokenizer is missing token '{token}' and no <unk> is defined.")
                ids.append(token_id)
        return ids

    def decode(self, ids: list[int]) -> str:
        """Reconstruct text from token ids."""
        pieces: list[str] = []
        current_word: list[str] = []
        for idx in ids:
            token = self.inv_vocab[idx]
            if token == self.unknown_token:
                if current_word:
                    pieces.append("".join(current_word))
                    current_word = []
                pieces.append(self.unknown_token)
                continue
            current_word.append(token)
            if token.endswith(self.end_of_word):
                pieces.append("".join(current_word).replace(self.end_of_word, ""))
                current_word = []

        if current_word:
            pieces.append("".join(current_word).replace(self.end_of_word, ""))

        return " ".join(piece for piece in pieces if piece)
