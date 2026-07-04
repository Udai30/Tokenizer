# 00 — Overview, Shared Skeleton & Conventions

This is the index for a set of **from-scratch, Python, intermediate** tokenizer projects whose goal is to
**learn the internals** of subword tokenization and produce a **portfolio-grade** result.

## The guides
| # | File | Project | Real-world analogue |
|---|------|---------|--------------------|
| 01 | `01-bpe.md` | Character-level BPE | GPT-1 era, classic Sennrich 2016 |
| 02 | `02-byte-level-bpe.md` | Byte-level BPE | GPT-2/3/4, `tiktoken`, RoBERTa |
| 03 | `03-wordpiece.md` | WordPiece | BERT, DistilBERT, Electra |
| 04 | `04-unigram-lm.md` | Unigram LM | SentencePiece, ALBERT, T5, XLNet |
| 05 | `05-visualizer-playground.md` | Interactive demo | — |
| 06 | `06-benchmark-suite.md` | Comparison + metrics | — |
| 07 | `07-multilingual-analysis.md` | Cross-lingual study | — |
| 08 | `08-domain-tokenizer.md` | Code/DNA/SMILES | StarCoder, ProtBERT |
| 09 | `09-tiny-lm-pipeline.md` | Tokenizer → tiny LM (capstone) | nanoGPT |
| — | `RECOMMENDATION.md` | What to showcase + sequence | — |

## Why these algorithms differ (the 30-second mental model)
- **BPE** and **WordPiece** are *merge-based / bottom-up*: start from characters (or bytes) and greedily
  combine the best pair, repeatedly, until you hit the target vocab size. They differ only in **how they
  score "best pair"** and how they **encode** a new word.
- **Unigram LM** is *probabilistic / top-down*: start with a huge candidate vocab and **prune** it,
  keeping the tokens that best explain the corpus under a unigram language model. Encoding finds the
  **most probable segmentation** via Viterbi.

| | Train direction | "Best token" rule | Encode method |
|---|---|---|---|
| BPE | bottom-up merges | most **frequent** adjacent pair | replay merges in order |
| WordPiece | bottom-up merges | max **likelihood gain** `freq(ab)/(freq(a)·freq(b))` | greedy **longest-match** with `##` |
| Unigram | top-down prune | token whose removal **least hurts** corpus likelihood | **Viterbi** max-prob segmentation |

## Shared repo skeleton (build this first)
```
tokenizer/
  __init__.py
  base.py            # abstract Tokenizer: train / encode / decode / save / load / get_vocab
  pretokenize.py     # whitespace, GPT-2 regex, byte-level pre-tokenizers
  bpe.py
  byte_bpe.py
  wordpiece.py
  unigram.py
  utils.py           # counting, pair stats, (de)serialization helpers
data/                # small corpora (see datasets below)
benchmarks/          # metric scripts + plots
viz/                 # streamlit/gradio app
tests/               # round-trip + known-fixture tests
docs/                # these guides
README.md
pyproject.toml
```

## Shared base interface (`tokenizer/base.py`)
Every tokenizer implements the same contract so the visualizer/benchmark code is written once:

```python
from abc import ABC, abstractmethod

class Tokenizer(ABC):
    def __init__(self):
        self.vocab = {}          # token (str/bytes) -> id
        self.inv_vocab = {}      # id -> token
        self.special_tokens = {} # e.g. {"<unk>":0, "<pad>":1, ...}

    @abstractmethod
    def train(self, corpus: list[str], vocab_size: int, **kwargs) -> None: ...

    @abstractmethod
    def encode(self, text: str) -> list[int]: ...

    @abstractmethod
    def decode(self, ids: list[int]) -> str: ...

    def save(self, path: str) -> None: ...   # JSON: vocab + merges/log-probs + config
    @classmethod
    def load(cls, path: str): ...

    def get_vocab(self) -> dict: return dict(self.vocab)
```

The **golden invariant** every tokenizer must satisfy (tested everywhere):
```python
assert tok.decode(tok.encode(s)) == s   # for byte-level / lossless tokenizers
```
(Character/WordPiece tokenizers may normalize, so for them assert round-trip on the *normalized* text.)

## Master datasets (download once into `data/`)
- **Tiny Shakespeare** (~1 MB) — fast dev loop. (`char-rnn` dataset, single .txt.)
- **WikiText-2 / WikiText-103 sample** — clean English baseline.
- **Tatoeba / FLORES-200 / OSCAR subset** — multilingual (English, Turkish, Finnish, Chinese, Japanese, Arabic).
- **CodeSearchNet / The Stack (small slice)** — source code.
- **ChEMBL SMILES sample / genome FASTA sample** — optional non-text domains.
- **`stress.txt`** — hand-built file with emoji 😀, CJK 漢字, accents café, RTL العربية, whitespace edges, control chars.

Keep everything in the **few-MB range** so training is seconds-to-minutes.

## Reference libraries (for comparison ONLY — never for the core algorithm)
- HuggingFace `tokenizers` (Rust-backed BPE/WordPiece/Unigram)
- `sentencepiece` (Unigram + BPE)
- `tiktoken` (GPT byte-level BPE)
Use these to **validate** your merges/segmentations and to **benchmark** speed/quality against.

## Glossary
- **Pre-tokenization**: splitting raw text into "words"/chunks before subword splitting (whitespace, regex, or byte mapping).
- **Merge rule**: an ordered `(a, b) -> ab` operation learned by BPE/WordPiece.
- **Continuation prefix (`##`)**: WordPiece marker meaning "this piece attaches to the previous one."
- **Viterbi**: dynamic-programming algorithm to find the highest-probability segmentation.
- **EM (Expectation-Maximization)**: iterative algorithm Unigram uses to estimate token probabilities.
- **Fertility**: average number of tokens produced per word.
