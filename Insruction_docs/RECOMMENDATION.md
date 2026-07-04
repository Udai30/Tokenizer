# RECOMMENDATION — What to Showcase & In What Order

## TL;DR
Build a **single cohesive repo** called something like `minbpe-lab` / `tokenizers-from-scratch` that
contains all four algorithms, but **lead your portfolio with the Byte-Level BPE tokenizer (guide 02)
wrapped in the Visualizer (05) and Benchmark suite (06)**.

> **Headline you're aiming for:** *"I built a GPT-style (byte-level BPE) tokenizer from scratch, visualized
> how it learns, and benchmarked it against OpenAI's `tiktoken` and HuggingFace."*

This is the version recruiters and hiring managers immediately understand and respect, because:
- "GPT-2 tokenizer from scratch" maps directly to real LLM infrastructure they know.
- It proves you understand what happens *before* the model — a part most candidates hand-wave.
- The visualizer gives them something to **click and play with** (huge for getting noticed).
- The benchmarks prove you can **measure and reason**, not just implement.

## Why byte-level BPE over the others as the *showcase*
| Algorithm | Recruiter recognition | "Wow" factor | Effort to polish |
|-----------|----------------------|--------------|------------------|
| **Byte-level BPE** | ★★★ (GPT-2/3/4, tiktoken) | ★★★ (zero OOV, any input) | medium |
| BPE (char) | ★★ | ★ | low |
| WordPiece | ★★ (BERT) | ★ | low |
| Unigram | ★ (niche awareness) | ★★ (most "academic") | high |

Unigram is the most intellectually impressive to *peers*, but byte-level BPE is the most legible to
*recruiters*. Build Unigram for your own understanding and to round out the repo — mention it — but put
byte-level BPE front and center.

## Recommended build sequence (each step sets up the next)
1. **Shared skeleton + `base.py`** (guide 00) — the interface everything reuses. *(~half day)*
2. **01 — Character BPE** — simplest correct merge algorithm; learn merges here. *(2–3 days)*
3. **02 — Byte-Level BPE** — upgrade 01 to bytes + regex pre-tokenization. **Your showcase core.** *(2–3 days)*
4. **03 — WordPiece** — small delta from BPE (scoring + `##`); validate against `bert-base-uncased`. *(1–2 days)*
5. **04 — Unigram LM** — the hard, different one (EM + Viterbi + pruning); completes your understanding. *(4–6 days)*
6. **06 — Benchmark suite** — compare all four; produces the charts that sell the repo. *(2–3 days)*
7. **05 — Visualizer** — wrap it in an interactive, deployed demo (the clickable hook). *(2–3 days)*
8. **Pick ONE differentiator** based on the roles you target:
   - Targeting **LLM / infra / applied-ML** roles → **09 Tiny-LM pipeline** (shows end-to-end impact).
   - Targeting **research / data-science** roles → **07 Multilingual analysis** (shows analysis + communication).
   - Targeting **code-AI / dev-tools** roles → **08 Domain (code) tokenizer**.

Total: ~3–4 weeks of part-time work for a genuinely standout repo. Steps 1–3 alone (about a week) already
give you a resume-worthy project if you're time-constrained.

## Minimum viable portfolio (if short on time)
Do **00 → 01 → 02 → 06(light) → 05(light)**. That's ~10–12 days and still produces:
"Built a GPT-style byte-level BPE tokenizer from scratch with benchmarks vs. tiktoken and a live demo."

## How to present the repo (README layout)
1. **Top:** one-line pitch + the **visualizer GIF** + live demo link (HF Spaces / Streamlit Cloud).
2. **What & why:** 2–3 sentences; which real models use each algorithm.
3. **Results table + 2–3 charts** (from guide 06): compression, fertility-by-language, throughput vs tiktoken.
4. **Architecture:** the shared `base.py` interface + the four implementations (link the `docs/` guides).
5. **Validation:** "matches `bert-base-uncased` >99%, lossless round-trip on arbitrary Unicode, vocab
   overlap with sentencepiece" — concrete correctness claims.
6. **What I learned:** a short, honest paragraph on trade-offs you measured.

## Ready-to-paste resume bullets (pick 1–2)
- *"Implemented BPE, byte-level BPE (GPT-2 style), WordPiece, and Unigram LM tokenizers from scratch in
  Python; validated against `tiktoken`, HuggingFace `tokenizers`, and SentencePiece."*
- *"Built a GPT-2-style byte-level BPE tokenizer (byte→unicode mapping, regex pre-tokenization, rank-based
  encoder) achieving lossless round-trip on arbitrary Unicode; benchmarked token counts vs. OpenAI `tiktoken`."*
- *"Created a deployed, interactive tokenizer playground and a reproducible benchmark suite comparing four
  subword algorithms on compression, fertility, OOV, and speed across English, code, and multilingual corpora."*

## Talking points for interviews
- Why GPT uses byte-level BPE (no OOV, language-agnostic) vs. BERT's WordPiece (`[UNK]` on unseen chars).
- Frequency (BPE) vs. likelihood-gain (WordPiece) vs. probabilistic EM/Viterbi (Unigram) — the real differences.
- The "non-English token tax" and its cost/fairness implications (if you did guide 07).
- Why perplexity isn't comparable across vocabularies and why you used bits-per-character (if you did guide 09).
