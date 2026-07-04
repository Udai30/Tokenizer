# 03 — WordPiece (BERT style)

## 1. What it is & why it matters
WordPiece (Schuster & Nakajima 2012; used by BERT, DistilBERT, Electra) is **merge-based like BPE** but
picks merges by **likelihood gain** rather than raw frequency, and **encodes by greedy longest-match**
using a `##` prefix for word-internal pieces. Small delta from guide 01 — build BPE first.

## 2. Internals you'll learn
- The likelihood-gain scoring function and why it differs from frequency.
- The `##` continuation-prefix convention and what it encodes (word-start vs. word-internal).
- **Greedy longest-match-first (maximum matching)** encoding and its failure mode (`<unk>`).

## 3. Algorithm, step by step

### 3.1 Training
Same loop as BPE, but the "best pair" score is:
```
score(a, b) = freq(ab) / (freq(a) * freq(b))
```
This favors pairs that occur together *more than chance* — i.e. genuinely informative subwords, not just
common ones. Steps:
1. Pre-tokenize into words; split each word into characters where **non-initial characters get `##`**:
   `"word"` → `['w', '##o', '##r', '##d']`.
2. Count symbol and adjacent-pair frequencies.
3. Pick the pair maximizing `score(a,b)`; merge it (`'##o' + '##r' -> '##or'`).
4. Repeat to target vocab size.

### 3.2 Encoding — greedy longest match
For each word, from the left, find the **longest prefix that is in the vocab**; emit it; the remainder is
prefixed with `##` and the process repeats. If no prefix matches, the **whole word** → `[UNK]`.
```python
def encode_word(word, vocab):
    tokens, start = [], 0
    while start < len(word):
        end = len(word)
        cur = None
        while start < end:
            sub = word[start:end]
            piece = sub if start == 0 else "##" + sub
            if piece in vocab:
                cur = piece; break
            end -= 1
        if cur is None:
            return ["[UNK]"]          # whole word fails -> single UNK
        tokens.append(cur); start = end
    return tokens
```

### 3.3 Decoding
Join tokens, dropping `##` (it means "no space before"); insert spaces between word-initial pieces.

## 4. Implementation plan
`wordpiece.py: WordPiece(Tokenizer)`:
1. `_split_word_with_marks(word)` → char list with `##`.
2. `train`: reuse pair-counting, swap the scoring function to likelihood gain.
3. `encode`: greedy longest-match per word (above).
4. `decode`: strip `##`, rejoin.
5. Add special tokens `[UNK] [CLS] [SEP] [PAD] [MASK]` to match BERT's vocab conventions.

## 5. Edge cases & gotchas
- **Whole-word `[UNK]`**: WordPiece does NOT do partial unknowns — one bad char kills the whole word.
  This is why people pair it with strong normalization. Test this behavior explicitly.
- **Normalization**: BERT lowercases, strips accents, splits on punctuation/CJK *before* WordPiece. Decide
  whether you replicate `bert-base-uncased` normalization (recommended) — note round-trip is then only
  exact on normalized text.
- **`##` on the first piece** must never appear; word-internal pieces always carry it.

## 6. Test plan
- **Reference parity**: load `bert-base-uncased` vocab; tokenize sentences with your encoder and assert
  identical output to HuggingFace `BertTokenizer` (a strong, concrete correctness check).
- **UNK behavior**: feed a word with a never-seen character; assert single `[UNK]`.
- **Round-trip on normalized text**.

## 7. Metrics to evaluate against
- Fertility & compression vs. BPE on the same corpus/vocab size.
- `[UNK]` rate (WordPiece's weakness vs. byte-level) — quantify it on multilingual text.
- Exact-match rate against `BertTokenizer` on a held-out set.

## 8. Datasets to use
- WikiText-2 (English). Add a multilingual sample to surface the `[UNK]` rate contrast with byte-level BPE.

## 9. Portfolio presentation
- A clear diagram: same word tokenized by BPE vs. WordPiece, highlighting `##` and the scoring difference.
- A table: "% sentences tokenized identically to `bert-base-uncased`" (aim high — proves correctness).
- Resume bullet: *"Implemented WordPiece (likelihood-gain merges, `##` greedy longest-match decoding);
  reproduced `bert-base-uncased` tokenization with >99% exact match on held-out text."*

## 10. Stretch goals
- Implement the full BERT normalization pipeline (NFD, lowercase, accent strip, CJK spacing).
- Compare likelihood-gain vs. frequency scoring: do the learned vocabs actually differ, and how?
