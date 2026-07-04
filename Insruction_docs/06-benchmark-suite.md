# 06 — Benchmark & Comparison Suite

## 1. What it is & why it matters
A reproducible harness that trains your from-scratch tokenizers, runs them (and reference libraries) over
multiple corpora and vocab sizes, and emits **tables + charts**. This is what converts "I implemented some
algorithms" into "I measured and understand the trade-offs" — the difference between a student project and
an engineer's project. Build after you have ≥2–3 tokenizers.

## 2. Internals you'll learn
- Defining tokenization metrics precisely and computing them correctly.
- Fair benchmarking (same corpus, same vocab size, warm-up, repeated timing).
- Turning raw numbers into a narrative with plots.

## 3. Metrics, defined precisely
- **Compression ratio** = `total_chars / total_tokens` (higher = better).
- **Fertility** = `total_tokens / total_words` (lower = more word-aligned).
- **OOV / unk rate** = `% tokens that are <unk>/[UNK]` (byte-level → 0).
- **Vocab utilization** = `% of vocab actually used` on a held-out corpus.
- **Encode throughput** = tokens/sec (median of N runs after a warm-up run).
- **Train time** = wall-clock to reach target vocab size.
- **Reference agreement** = vocab overlap % and segmentation exact-match % vs. HF/`sentencepiece`/`tiktoken`.
- **Round-trip fidelity** = `% inputs where decode(encode(x)) == x`.

## 4. Implementation plan
```
benchmarks/
  metrics.py     # pure functions: compression(), fertility(), oov_rate(), agreement(), ...
  run.py         # loops tokenizers × corpora × vocab_sizes -> results.csv
  plots.py       # reads results.csv -> charts (matplotlib)
  references.py  # thin wrappers around HF tokenizers / sentencepiece / tiktoken
```
- `run.py`: for each `(tokenizer, corpus, vocab_size)` → train (or load), evaluate on a **held-out split**,
  append a row to `results.csv` (columns: tokenizer, corpus, vocab_size, metric values).
- Use a **fixed train/test split** and a fixed seed so results are reproducible.
- Time encoding with `time.perf_counter`, discard the first run, report the median of ≥5.

## 5. Edge cases & gotchas
- **Train vs. test leakage**: always measure metrics on held-out text, never on the training corpus.
- **Pure-Python is slow** — your encoders will lose throughput to Rust-backed `tokenizers`/`tiktoken`.
  Report it honestly and frame it as "algorithmic parity, not optimized for speed."
- **Word counting** for fertility must use a consistent definition across tokenizers (whitespace split).
- **Vocab-size apples-to-apples**: compare all tokenizers at the *same* vocab size.

## 6. Test plan
- Unit-test each metric on a tiny hand-computed example (e.g. known char/token counts).
- Assert byte-level OOV rate is exactly 0; assert round-trip fidelity is 100% for byte-level.

## 7. Metrics to evaluate against
(This project *is* the metrics — see §3. The deliverable is the table + charts.)

## 8. Datasets to use
- **WikiText-2** (English prose), **a code sample** (CodeSearchNet/The Stack slice), **a multilingual sample**
  (Tatoeba/FLORES). Run each tokenizer at vocab sizes {1k, 4k, 8k, 16k, 32k}.

## 9. Portfolio presentation
- A **results table** in the README (tokenizer × metric) and 2–3 key charts:
  1. vocab size vs. compression ratio (all tokenizers).
  2. fertility by language (bar chart) — sets up guide 07.
  3. encode throughput vs. reference libs (log scale).
- A short "**What I learned**" paragraph interpreting the trade-offs (e.g. "Unigram gave the best
  compression at 16k; byte-level BPE was the only one with zero OOV on multilingual text").
- Resume bullet: *"Built a reproducible benchmark suite comparing BPE/WordPiece/Unigram/byte-level BPE on
  compression, fertility, OOV, and speed across English, code, and multilingual corpora; validated against
  HuggingFace and SentencePiece."*

## 10. Stretch goals
- Auto-generate the README results table from `results.csv` (no manual copy-paste).
- Add a statistical note (confidence intervals over timing runs).
