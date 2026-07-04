# 05 — Tokenizer Visualizer / Playground

## 1. What it is & why it matters
An interactive web app (Streamlit or Gradio) that makes your tokenizers **tangible**: paste text, see how
each algorithm segments it, and replay how BPE/WordPiece built their vocabularies merge-by-merge. This is
the **clickable thing** that turns a code repo into a portfolio piece recruiters actually engage with.
Build it after you have ≥2 working tokenizers (BPE + byte-level BPE is enough to start).

## 2. Internals you'll learn (and reinforce)
- Instrumenting your training loop to emit a **merge history** (intermediate state, not just final vocab).
- Mapping tokens → colored spans for visualization.
- Clean separation between the tokenizer library (logic) and the app (presentation).

## 3. Features, step by step
1. **Live segmentation**: input box → show the same text tokenized by BPE / byte-BPE / WordPiece / Unigram,
   each token as a colored chip with its **id** and (for byte-level) the visible `Ġ` space markers.
2. **Stats panel**: token count, char/token compression, fertility, and `<unk>`/`[UNK]` count per tokenizer.
3. **Merge replay** (the wow feature): a slider over training steps; at step *k* show the vocab and how a
   sample word is segmented after *k* merges. Animate `t`,`h`→`th`→`the`.
4. **Side-by-side compare**: highlight where two tokenizers disagree on boundaries.
5. **Vocab explorer**: search the learned vocab, sort by frequency/length, see the longest tokens.

## 4. Implementation plan
- Instrument training to optionally return/save a **trace**: list of `(merge, vocab_snapshot_or_size)`.
  Add `train(..., record_trace=True)` to BPE/WordPiece.
- `viz/app.py` (Streamlit):
  - `st.text_area` for input; `st.selectbox`/`st.multiselect` for tokenizers and vocab size.
  - Render tokens with `st.markdown` + inline HTML spans (background color per token); cycle a color palette.
  - `st.slider` bound to the merge-trace index for replay.
- Cache trained tokenizers with `@st.cache_resource` so the app is snappy.

## 5. Edge cases & gotchas
- Long inputs → cap rendered tokens or paginate (HTML with thousands of spans gets slow).
- Byte-level tokens contain non-letter glyphs (`Ġ`, `Ċ`) — render them literally and add a legend.
- Keep the app importing the **library**, never duplicating tokenizer logic.

## 6. Test plan
- Snapshot test: for a fixed input + seed, the rendered token list matches a stored expectation.
- Manual QA checklist for the UI (input edge cases: empty, emoji, very long).

## 7. Metrics shown (not new — surfaced from guide 06)
- Per-tokenizer token count, compression, fertility, unk rate, displayed live.

## 8. Datasets to use
- Ship a few **preset example texts** (English prose, code snippet, emoji/multilingual sentence) as buttons.

## 9. Portfolio presentation
- **Record a 20–30s GIF** of the merge-replay slider and the side-by-side comparison — embed it at the top
  of the repo README. This single GIF does most of the selling.
- Deploy free on **Streamlit Community Cloud** or **HuggingFace Spaces**; put the live link in your resume.
- Resume bullet: *"Built an interactive tokenizer playground (Streamlit, deployed on HF Spaces) visualizing
  BPE merge dynamics and cross-algorithm segmentation differences."*

## 10. Stretch goals
- Token-cost calculator (tie to guide 02): estimate API cost of a prompt across model tokenizers.
- "Tokenization diff" view between your tokenizer and `tiktoken`/`bert` on the same text.
