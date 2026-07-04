# 02 — Byte-Level BPE (GPT-2 / `tiktoken` style) ⭐ showcase core

## 1. What it is & why it matters
Byte-level BPE runs the **exact same merge algorithm as guide 01**, but the *atoms* are the **256 raw
UTF-8 bytes** instead of characters. Consequences:
- **Zero OOV, ever** — any string (emoji, CJK, binary-ish bytes) is representable, because every byte is
  in the base vocab. No `<unk>` token is ever needed.
- This is what **GPT-2, GPT-3, GPT-4, RoBERTa** use. Recruiters instantly recognize "GPT-style tokenizer."
**This is your portfolio centerpiece.** Build guide 01 first, then this is a focused upgrade.

## 2. Internals you'll learn
- The **byte→unicode mapping trick** (why GPT-2 maps bytes to printable chars).
- **Regex pre-tokenization** (the GPT-2 / GPT-4 split pattern).
- Why byte-level guarantees losslessness and language-agnosticism.

## 3. Algorithm, step by step

### 3.1 The byte→unicode trick (critical detail)
BPE works on strings, but raw bytes include control chars/whitespace that break string handling. GPT-2
maps all 256 bytes to a set of 256 **printable, non-whitespace** Unicode code points, reversibly:
```python
def bytes_to_unicode():
    bs = list(range(ord("!"), ord("~")+1)) + list(range(ord("¡"), ord("¬")+1)) + list(range(ord("®"), ord("ÿ")+1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b); cs.append(256 + n); n += 1
    return dict(zip(bs, (chr(c) for c in cs)))   # byte -> unicode char
```
Encode pipeline: `text → utf-8 bytes → map each byte to its unicode char → run BPE merges on that string`.
Decode reverses it exactly → **lossless**.

### 3.2 Regex pre-tokenization (GPT-2 pattern)
Instead of splitting only on whitespace, GPT-2 uses a regex that keeps contractions, leading spaces,
numbers, and punctuation as sensible chunks:
```python
import regex as re   # the `regex` module, not `re` — needs \p{L}, \p{N}
GPT2_PAT = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
chunks = GPT2_PAT.findall(text)
```
(GPT-4/`cl100k_base` uses a slightly different, case-insensitive variant — worth mentioning in the README.)
Leading spaces are encoded as the byte for `' '` (mapped to `Ġ`), so word boundaries are preserved without a `</w>` marker.

### 3.3 Training & encoding
Identical to guide 01's merge loop, operating on the byte-mapped chunks. Base vocab = 256 byte tokens
(+ special tokens). Merges build up from there to `vocab_size` (GPT-2 = 50,257).

## 4. Implementation plan
Reuse `bpe.py` internals; new file `byte_bpe.py`:
1. `pretokenize.py: bytes_to_unicode()`, `unicode_to_bytes()`, `gpt2_split(text)`.
2. `byte_bpe.py: ByteLevelBPE(Tokenizer)`:
   - `train`: map corpus → byte-unicode chunks → BPE merge loop.
   - `encode`: regex split → byte-map each chunk → apply merges by rank → ids.
   - `decode`: ids → tokens → join → reverse byte-map → utf-8 decode.
3. Implement the **rank-based encoder** (apply lowest-rank merge present, repeat) — this is the standard
   fast BPE encode and matches `tiktoken` behavior.

## 5. Edge cases & gotchas
- **Use the `regex` package**, not stdlib `re` — you need `\p{L}`/`\p{N}` Unicode classes.
- **utf-8 decode with `errors="replace"` only on truly malformed input** — normal round-trips must be exact.
- **Leading-space semantics**: `"hello"` vs `" hello"` tokenize differently (the `Ġ` prefix). Test both.
- **Special tokens** (`<|endoftext|>`) must be matched *before* the regex split, never merged.

## 6. Test plan
- **Golden invariant**: `decode(encode(s)) == s` for ALL of `stress.txt` (emoji, CJK, RTL, control bytes) — byte-level must be perfectly lossless.
- **Cross-check vs. `tiktoken`/HF ByteLevel BPE** trained on the same corpus: compare token counts and a few segmentations.
- **No `<unk>` ever**: assert encoding never emits an unknown id for arbitrary random bytes.

## 7. Metrics to evaluate against
- **OOV rate = 0** (the headline property — show it).
- Compression ratio vs. character-level BPE (guide 01) on the same text — byte-level usually wins on mixed/multilingual.
- Encode throughput vs. `tiktoken` (you'll be slower in pure Python — report it honestly, it's expected).

## 8. Datasets to use
- WikiText-2 for the main numbers; **`stress.txt`** to prove losslessness; a multilingual sample to show the OOV=0 advantage.

## 9. Portfolio presentation
- **Lead with this project.** README headline: *"A GPT-2-style byte-level BPE tokenizer built from scratch."*
- Side-by-side table: your tokenizer vs. `tiktoken` token counts on sample prompts.
- A demo cell: tokenize an emoji-and-Chinese sentence and show it round-trips perfectly while a naive char tokenizer fails.
- Resume bullet: *"Built a GPT-2-style byte-level BPE tokenizer from scratch (byte→unicode mapping, regex
  pre-tokenization, rank-based encoder); achieved lossless round-trip on arbitrary Unicode and benchmarked
  token counts against OpenAI `tiktoken`."*

## 10. Stretch goals
- Reproduce `cl100k_base`-style regex and compare GPT-2 vs GPT-4 segmentation on the same text.
- Load real GPT-2 merges (`vocab.bpe`) into your encoder and verify you match HF exactly.
- A `count_tokens()` cost estimator ("how many tokens / $ is this prompt") — recruiter catnip.
