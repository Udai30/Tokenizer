# 07 — Multilingual & Morphology Analysis

## 1. What it is & why it matters
A focused *study* (not a new tokenizer) using your tokenizers to quantify how tokenization treats different
languages — the "**non-English token tax**," morphology handling, and fairness/cost implications. This is a
strong differentiator: it shows you can do **analysis and communicate findings**, not just code.

## 2. Internals you'll learn
- How fertility varies with script and morphology (agglutinative vs. analytic languages).
- Why multilingual LLMs cost more per "meaning" in some languages.
- How vocab composition skews toward the training-data language.

## 3. Analyses, step by step
1. **Fertility by language**: tokenize parallel sentences (same meaning, many languages) and compute
   tokens-per-sentence. Parallel corpora (FLORES-200, Tatoeba) make this an apples-to-apples comparison.
2. **The token tax**: ratio of tokens(language X) / tokens(English) for the same content. Report a ranked table.
3. **Morphology respect**: for agglutinative languages (Turkish, Finnish), check whether subword boundaries
   fall on real morpheme boundaries (use a small annotated sample or a morphological analyzer for ground truth).
4. **Vocab bias**: what fraction of a tokenizer trained on mostly-English text is usable for, say, Chinese?
5. **Algorithm comparison**: do byte-level BPE / Unigram reduce the tax vs. WordPiece? (Hypothesis: yes.)

## 4. Implementation plan
- Reuse the benchmark `metrics.py` (fertility, compression) but **group by language**.
- `analysis/multilingual.py`: load parallel corpus → per-language tokenization → DataFrame → plots.
- Train tokenizers in two regimes: **English-only** vs. **balanced multilingual** corpus, and compare.

## 5. Edge cases & gotchas
- **Word definition breaks down** for languages without spaces (Chinese, Japanese, Thai) — use char counts
  or a segmenter, and be explicit about the metric you use.
- **Unicode normalization** (NFC/NFKC) affects results — fix one scheme and state it.
- Avoid overclaiming on morphology without ground-truth boundaries.

## 6. Test plan
- Sanity: parallel sentences with identical meaning should have comparable *information*, so large fertility
  gaps are the finding, not a bug — but verify counts on a hand-checked pair.
- Re-run with a different parallel corpus to confirm trends are stable.

## 7. Metrics to evaluate against
- Fertility per language; token-tax ratio vs. English; OOV/unk rate per language; morpheme-boundary precision (where ground truth exists).

## 8. Datasets to use
- **FLORES-200** or **Tatoeba** (parallel, many languages). Pick ~8 languages spanning families: English,
  Spanish, German, Turkish, Finnish, Arabic, Chinese, Japanese.

## 9. Portfolio presentation
- A headline bar chart: "**Tokens needed to say the same thing**" across languages — visually striking and
  immediately understandable.
- A short write-up: "English-trained tokenizers charge non-English users up to N× more tokens for identical
  content; byte-level/Unigram narrow but don't eliminate the gap."
- Resume bullet: *"Analyzed cross-lingual tokenization fairness across 8 languages using FLORES-200,
  quantifying the 'non-English token tax' and comparing BPE/WordPiece/Unigram on fertility and OOV."*

## 10. Stretch goals
- Tie tax to **API cost**: dollars-per-translated-paragraph by language.
- Train a balanced multilingual tokenizer and show the tax shrinking.
