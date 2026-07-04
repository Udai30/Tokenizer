# 09 — Tokenizer → Tiny Language Model (Capstone)

## 1. What it is & why it matters
The capstone that **closes the loop**: plug your from-scratch tokenizer into a small language model and
measure how the **tokenizer choice affects training and generation**. This answers the "so what?" question
— it shows you understand *why* tokenization matters downstream, not just how it works. Most impressive
when done after the algorithms + benchmark suite.

## 2. Internals you'll learn
- How sequence length (driven by the tokenizer) affects model compute and context.
- End-to-end pipeline: text → tokenizer → ids → model → loss → generation → decode.
- Comparing tokenizers by **downstream perplexity**, the metric that ultimately matters.

## 3. Steps
1. **Pick a tiny model**: a minimal char/subword **Transformer** (nanoGPT-scale, ~1–10M params) or even a
   smoothed **n-gram** model if you want to avoid a training loop. Transformer is the stronger portfolio choice.
2. **Tokenize** a small corpus (Tiny Shakespeare or WikiText-2) with each tokenizer → id sequences.
3. **Train** the same model architecture separately on each tokenization (same steps, same hyperparams).
4. **Evaluate**: held-out **perplexity** (careful: perplexity isn't directly comparable across different
   vocabularies — normalize by **bits-per-character** instead, which *is* comparable). Also compare sample
   generation quality qualitatively.
5. **Report**: which tokenizer let the tiny model learn fastest / generate best, and why (shorter sequences,
   better-aligned units).

## 4. Implementation plan
- Reuse your tokenizers' `encode`/`decode`.
- `lm/model.py`: small Transformer (embedding, a few attention blocks, LM head) — or import nanoGPT-style code.
- `lm/train.py`: standard training loop (cross-entropy, AdamW), log loss.
- `lm/eval.py`: compute **bits-per-character** = `(avg cross-entropy in nats / ln2) × (tokens / chars)` so
  results are comparable across vocabs; plus a `generate()` for samples.

## 5. Edge cases & gotchas
- **Perplexity is NOT comparable across vocabularies** — always convert to bits-per-character (or
  bits-per-byte) for fair comparison. This is the single most common mistake; calling it out shows rigor.
- Keep **architecture and training budget identical** across tokenizers, or the comparison is meaningless.
- Tiny models + small data → high variance; average over a couple of seeds.

## 6. Test plan
- Sanity: model overfits a tiny batch (loss → ~0) — confirms the training loop is wired correctly.
- Assert id sequences round-trip through the tokenizer before training.

## 7. Metrics to evaluate against
- **Bits-per-character** on held-out text (primary, comparable across tokenizers).
- Training loss curves (same steps) per tokenizer.
- Average sequence length per tokenizer (explains compute differences).
- Qualitative generation samples.

## 8. Datasets to use
- **Tiny Shakespeare** (fast, fits a tiny model) for the main experiment; WikiText-2 if you have compute.

## 9. Portfolio presentation
- A single chart: **bits-per-character vs. training step**, one line per tokenizer — the money plot.
- Side-by-side generated samples under each tokenizer.
- Resume bullet: *"Built an end-to-end pipeline feeding from-scratch tokenizers into a small Transformer
  LM; measured downstream impact via bits-per-character, showing how tokenizer choice affects sequence
  length and language-model quality."*

## 10. Stretch goals
- Add subword-regularization (from guide 04) and test whether sampled segmentations improve robustness.
- Scale to a slightly larger model and report the compute saved by a better-compressing tokenizer.
