"""Simple pre-tokenization helpers."""

from __future__ import annotations


def whitespace_split(text: str) -> list[str]:
    """Split text on whitespace while preserving basic word order."""
    return text.split()
