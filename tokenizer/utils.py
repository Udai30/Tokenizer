"""Shared helpers for BPE-style tokenizers."""

from __future__ import annotations

from collections import Counter
from typing import Iterable


def get_pair_stats(words: dict[tuple[str, ...], int]) -> Counter[tuple[str, str]]:
    """Count adjacent symbol pairs, weighted by word frequency."""
    stats: Counter[tuple[str, str]] = Counter()
    for word, freq in words.items():
        for left, right in zip(word, word[1:]):
            stats[(left, right)] += freq
    return stats


def merge_word(word: tuple[str, ...], pair: tuple[str, str]) -> tuple[str, ...]:
    """Merge all non-overlapping occurrences of a pair inside one word."""
    left, right = pair
    merged: list[str] = []
    i = 0
    while i < len(word):
        if i + 1 < len(word) and word[i] == left and word[i + 1] == right:
            merged.append(left + right)
            i += 2
        else:
            merged.append(word[i])
            i += 1
    return tuple(merged)


def build_vocab_from_words(words: Iterable[tuple[str, ...]]) -> set[str]:
    """Collect the symbol inventory from tokenized words."""
    vocab: set[str] = set()
    for word in words:
        vocab.update(word)
    return vocab
