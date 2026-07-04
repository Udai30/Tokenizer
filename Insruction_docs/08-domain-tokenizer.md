# 08 — Domain-Specialized Tokenizer

## 1. What it is & why it matters
Train a tokenizer specialized for a **non-prose domain** (source code is the most recruiter-relevant; DNA,
protein, SMILES, or logs are options) and demonstrate it **beats a general-purpose tokenizer on
compression** for that domain. Shows you understand that tokenization is domain-dependent and that
pre-tokenization rules matter. Reuses your BPE/byte-BPE core.

## 2. Internals you'll learn
- How **pre-tokenization rules** (not just the merge algorithm) shape vocab quality.
- Why general tokenizers waste tokens on domain text (e.g. indentation, identifiers).
- Designing domain-aware splitting.

## 3. Steps (using source code as the worked example)
1. **Pick a domain corpus** (e.g. Python files from CodeSearchNet / a Stack slice).
2. **Design domain pre-tokenization**: keep indentation runs as single tokens, split on camelCase /
   snake_case boundaries, treat operators/punctuation sensibly, preserve common keywords.
3. **Train byte-level BPE** on it (byte-level handles any code/unicode safely).
4. **Compare** against a general English-trained tokenizer (and `tiktoken`) on **held-out code**:
   compression ratio, fertility, and how many tokens a typical function costs.
5. Inspect the learned vocab — you should see tokens like `    ` (4-space indent), `def `, `self.`,
   `return`, `()`, `import` — concrete evidence of specialization.

## 4. Implementation plan
- `pretokenize.py`: add `code_split(text)` (regex for identifiers, indentation, operators, strings).
- Reuse `byte_bpe.py`; just swap the pre-tokenizer.
- `analysis/domain.py`: compression comparison general vs. specialized on held-out domain text.

## 5. Edge cases & gotchas
- **Indentation/whitespace** is semantically meaningful in code — don't collapse it.
- **Strings and comments** contain natural language — your code tokenizer still needs to handle prose inside them (byte-level helps).
- For DNA/SMILES, the alphabet is tiny — vocab size and metrics behave differently; note that.

## 6. Test plan
- Round-trip on held-out code files (byte-level → must be exact, including indentation).
- Assert specialized tokenizer's compression on held-out code **>** general tokenizer's.

## 7. Metrics to evaluate against
- Compression ratio & fertility on held-out domain text: specialized vs. general vs. `tiktoken`.
- Tokens-per-function (a concrete, relatable unit).
- Qualitative: top-N learned tokens (show the domain-specific ones).

## 8. Datasets to use
- **CodeSearchNet** (Python/Java/JS) or a small **The Stack** slice. Optional: **ChEMBL SMILES** or a
  **genome FASTA** sample for a non-code variant.

## 9. Portfolio presentation
- A before/after: a real function tokenized by `tiktoken` vs. your code tokenizer, with token counts.
- Bar chart: compression on held-out code (general vs. specialized vs. tiktoken).
- Resume bullet: *"Trained a domain-specialized byte-level BPE tokenizer for source code with custom
  pre-tokenization; achieved ~X% better compression than a general-purpose tokenizer on held-out code."*

## 10. Stretch goals
- Multi-language code tokenizer; compare per-language compression.
- Show downstream impact: shorter sequences → more code fits in a fixed context window.
