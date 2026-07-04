# 01 — Byte-Pair Encoding (Character-Level BPE)

## 1. What it is & why it matters
BPE (Sennrich et al., 2016) is the foundational subword algorithm. It starts from individual characters
and **repeatedly merges the most frequent adjacent pair** into a new symbol until it reaches a target
vocab size. Used by GPT-1, early NMT systems, and (in byte form) every modern GPT.
**Build this first** — byte-level BPE and WordPiece are small deltas on top of it.

## 2. Internals you'll learn
- Greedy frequency-driven vocabulary construction.
- Why merge **order matters** and must be saved.
- The split between **training** (learn merges) and **encoding** (replay merges).
- Pre-tokenization and word boundary handling.

## 3. Algorithm, step by step

### 3.1 Training
1. **Pre-tokenize** the corpus into words (split on whitespace). Append an end-of-word marker so the
   tokenizer can tell `est` inside a word from `est` at the end. Classic choice: `</w>`.
   - Represent each word as a tuple of symbols: `"low"` → `('l','o','w','</w>')`.
2. Build a **word-frequency dict**: `{('l','o','w','</w>'): 5, ...}`.
3. Repeat until `len(vocab) == vocab_size` (or no pairs left):
   - **Count pairs**: for every word and its count, tally adjacent symbol pairs weighted by word count.
     ```
     pairs[(s_i, s_{i+1})] += word_freq
     ```
   - **Pick the best pair** = the one with the highest count (break ties deterministically, e.g. by the
     pair's lexicographic order, so runs are reproducible).
   - **Record the merge**: append `(a, b)` to an ordered `merges` list; add `ab` to the vocab.
   - **Apply the merge** to every word: replace adjacent `a,b` with `ab`.
4. Output: `vocab` (symbol→id) and ordered `merges` list.

Pseudo-code:
```python
def train(corpus, vocab_size):
    words = Counter(tuple(w) + ('</w>',) for line in corpus for w in line.split())
    vocab = set(ch for w in words for ch in w)
    merges = []
    while len(vocab) < vocab_size:
        pairs = Counter()
        for word, freq in words.items():
            for a, b in zip(word, word[1:]):
                pairs[(a, b)] += freq
        if not pairs: break
        best = max(pairs, key=lambda p: (pairs[p], p))  # freq, then deterministic tie-break
        merges.append(best)
        vocab.add(best[0] + best[1])
        words = {merge_word(w, best): f for w, f in words.items()}
    return vocab, merges
```
`merge_word` walks the symbol tuple and joins occurrences of the chosen pair.

### 3.2 Encoding
Apply the learned merges **in the order they were learned** to each pre-tokenized word:
1. Split the word into characters + `</w>`.
2. For each merge rule in order, replace all occurrences of that pair.
3. Map resulting symbols to ids (unknown chars → `<unk>` or byte fallback).

> Optimization: instead of looping all merges every time, give each merge a **rank** and repeatedly apply
> the lowest-rank applicable pair present in the current word (this is what real BPE encoders do).

### 3.3 Decoding
Concatenate the token strings, replace `</w>` with a space, strip the trailing one.

## 4. Implementation plan
Files/functions, in build order:
1. `pretokenize.py: whitespace_split(text) -> list[str]`
2. `utils.py: get_pair_stats(words)`, `merge_word(word, pair)`
3. `bpe.py: BPE(Tokenizer)` with `train`, `_tokenize_word`, `encode`, `decode`, `save`, `load`
4. `save` format (JSON): `{"vocab": {...}, "merges": [["l","o"], ...], "config": {...}}`

Data structures: `Counter` for word/pair frequencies; ordered `list` for merges; dict for vocab.

## 5. Edge cases & gotchas
- **Ties** between equally frequent pairs → make tie-breaking deterministic or your output won't be reproducible.
- **Single-character words** and empty strings.
- **Unknown characters at encode time** (not seen in training) → `<unk>` or fall back to byte-level (see guide 02).
- **`</w>` leaking** into output on decode — strip it correctly.
- **Performance**: naive retraining recomputes all pair stats each iteration (O(merges × corpus)). Fine for
  intermediate scope; note the incremental-update optimization as a stretch goal.

## 6. Test plan
- **Round-trip**: `decode(encode(s)) == s` for normalized text across `stress.txt`.
- **Known fixture**: the canonical paper example — corpus `{"low":5,"lower":2,"newest":6,"widest":3}`,
  assert the first merges are `('e','s')`, `('es','t')`, `('est','</w>')`, ... (verify against the paper).
- **Determinism**: train twice, assert identical merges.
- **Reference check**: train HF `tokenizers` BPE on the same corpus; compare merge lists / vocab overlap.

## 7. Metrics to evaluate against
- Compression ratio (chars/token) and fertility (tokens/word) vs. vocab size.
- Vocab overlap % with HF BPE on the same corpus.
- Train time vs. vocab size (show the O(n) blow-up, motivates byte-level + optimizations).

## 8. Datasets to use
- **Tiny Shakespeare** for dev, **WikiText-2** for the reported numbers.

## 9. Portfolio presentation
- README section: a GIF/animation of merges forming (`th`, `the`, `ing`...) on Shakespeare.
- A chart: vocab size (1k→32k) vs. average tokens per sentence.
- Resume bullet: *"Implemented Byte-Pair Encoding from scratch in Python; validated merge rules against
  HuggingFace `tokenizers` and analyzed compression vs. vocab-size trade-offs on WikiText-2."*

## 10. Stretch goals
- Incremental pair-count updates (only recompute pairs affected by the last merge) for big speedups.
- Add `dropout` BPE (randomly skip merges at encode time — regularization trick).
