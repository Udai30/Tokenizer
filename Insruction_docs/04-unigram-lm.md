# 04 — Unigram Language Model (SentencePiece style)

## 1. What it is & why it matters
The conceptually different one. Unigram (Kudo 2018; used by SentencePiece, ALBERT, T5, XLNet, mBART)
treats tokenization as a **probabilistic model**: every token has a probability, a word's segmentation
probability is the product of its tokens' probabilities, and the best segmentation is the most probable
one. Training **starts big and prunes down** using EM. This is the hardest of the four — build it last
among the algorithms; it cements your understanding.

## 2. Internals you'll learn
- **EM (Expectation-Maximization)** for estimating token probabilities.
- **Viterbi** dynamic programming for max-probability segmentation.
- **Log-space arithmetic** to avoid underflow.
- Loss-based **vocabulary pruning**.

## 3. Algorithm, step by step

### 3.1 Seed the vocabulary
Build a large candidate set (e.g. 1M → keep top ~100k by frequency): all single characters (mandatory,
to guarantee any string is segmentable) **plus** frequent substrings/n-grams from the corpus (enumerate
substrings up to length L, or use suffix-array frequencies). Initialize each token's probability by its
frequency (normalized).

### 3.2 Viterbi segmentation (the encode primitive, also used in training)
Given token log-probs, find the segmentation of a word maximizing total log-prob:
```python
def viterbi(word, logp, max_len):
    N = len(word)
    best = [-inf]*(N+1); best[0] = 0.0
    back = [-1]*(N+1)
    for i in range(1, N+1):
        for j in range(max(0, i-max_len), i):
            tok = word[j:i]
            if tok in logp and best[j] + logp[tok] > best[i]:
                best[i] = best[j] + logp[tok]; back[i] = j
    # reconstruct
    toks, i = [], N
    while i > 0:
        j = back[i]; toks.append(word[j:i]); i = j
    return toks[::-1]
```

### 3.3 EM training loop
Repeat for a few iterations:
- **E-step**: for each word, compute expected counts of each token. Either (a) Viterbi (hard EM — count
  only tokens in the best path) or (b) forward-backward (soft EM — marginal probabilities over all
  segmentations). Start with Viterbi/hard EM for simplicity.
- **M-step**: re-estimate each token's probability = its expected count / total expected count.

### 3.4 Pruning to target vocab size
After EM converges, **shrink the vocab**:
1. Compute the corpus log-likelihood (loss).
2. For each candidate token (never single chars), estimate the **loss increase if removed** (recompute the
   word's best segmentation without it).
3. Remove the bottom X% (smallest loss increase) tokens.
4. Re-run EM; repeat shrink→EM until `vocab_size` is reached.

### 3.5 Encoding / decoding
- **Encode**: run Viterbi with the final log-probs. (SentencePiece can also sample segmentations —
  *subword regularization* — a great stretch goal.)
- **Decode**: concatenate tokens; SentencePiece replaces a special space marker `▁` (U+2581) with `' '`.

## 4. Implementation plan
`unigram.py: Unigram(Tokenizer)`:
1. `_seed_vocab(corpus)` — char set + frequent substrings (cap candidate count).
2. `_viterbi(word)` and `_word_logprob(word)` helpers (log-space).
3. `_em_step(words)` → updated probabilities.
4. `_prune(words, keep_fraction)` → remove low-loss tokens, keep all single chars.
5. `train` orchestrates seed → EM → prune loop down to target size.
6. Use `▁` space marker (SentencePiece convention) so detokenization is unambiguous.

## 5. Edge cases & gotchas
- **Numerical underflow** → always work in **log-space**; guard `log(0)`.
- **Never prune single characters** — they guarantee every string remains segmentable (no dead ends in Viterbi).
- **Unsegmentable words** if a char is missing from vocab → fall back to a byte/char or `<unk>`.
- **Compute cost**: candidate enumeration explodes; cap candidates and `max_len`, sample the corpus for EM if needed.
- **EM iterations**: 2–5 is usually enough per shrink round; more is rarely worth it.

## 6. Test plan
- **Reference parity**: train `sentencepiece` (model_type=unigram) on the same corpus; compare vocab
  overlap and segmentations on held-out sentences (won't be identical — seeds/heuristics differ — but
  should be close; report overlap %).
- **Viterbi correctness**: tiny hand-built vocab with known probabilities → assert the DP picks the math-correct segmentation.
- **Monotonic likelihood**: assert corpus log-likelihood is non-decreasing across EM steps within a round.
- **Round-trip** on normalized text.

## 7. Metrics to evaluate against
- Compression/fertility vs. BPE & WordPiece at equal vocab size.
- Corpus log-likelihood / per-token loss (Unigram's native objective) — plot it dropping over EM.
- Vocab overlap % with `sentencepiece`.
- (Stretch) effect of subword-regularization sampling on downstream robustness.

## 8. Datasets to use
- WikiText-2 for reported numbers; Tiny Shakespeare for fast EM-iteration debugging; multilingual sample
  to show Unigram's typically strong cross-lingual fertility.

## 9. Portfolio presentation
- A plot of **log-likelihood vs. EM iteration** and **vocab size vs. loss during pruning** — these
  visually prove you implemented the probabilistic machinery, not just merges.
- Show multiple plausible segmentations of one word with their probabilities (Viterbi vs. sampled).
- Resume bullet: *"Implemented the Unigram LM tokenizer from scratch — EM probability estimation, Viterbi
  decoding, and loss-based vocabulary pruning; benchmarked against Google SentencePiece."*

## 10. Stretch goals
- **Subword regularization**: sample segmentations from the lattice instead of taking the Viterbi best.
- Soft EM via forward–backward instead of hard/Viterbi EM; compare resulting vocabs.
