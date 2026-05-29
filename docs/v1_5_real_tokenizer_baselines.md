# v1.5 Real Tokenizer Baseline Plan

Status: infrastructure started
Date: 2026-05-30
Tokenizer behavior: not changed

## Purpose

v0.8 and v0.9 used a pure-Python toy BPE baseline. That was useful for building
comparison infrastructure, but it is not enough for an LLM-tokenizer claim.

v1.5 should compare `tr-centric-tokenizer` against real tokenizer families:

- Qwen byte-level BPE tokenizer
- LLaMA/Mistral-style SentencePiece or byte-fallback tokenizers
- SentencePiece BPE trained on Turkish demo/prototype corpora
- SentencePiece Unigram trained on Turkish demo/prototype corpora

The goal is not to claim production superiority. The goal is to answer a more
concrete research question:

```text
At a comparable token budget, does the Turkish-centered morphology layer preserve
Turkish morphological boundaries better than production-like subword tokenizers?
```

## Qwen-Inspired Takeaways

The Qwen tokenizer family is useful as a design reference because it shows a
practical multilingual LLM tokenizer pattern:

- byte-level BPE for lossless coverage and no normal `<unk>` failure mode
- large vocabulary, roughly in the 150k range for current Qwen2/Qwen2.5-style
  tokenizers
- strong allocation for Chinese characters and multilingual/code text
- special chat/control tokens such as message boundary tokens
- tokenizer behavior tied to the model family and chat template

The Turkish-centered analogue is not "copy Qwen." It is:

```text
Chinese gets character-aware efficiency in Qwen.
Turkish should get morphology-aware efficiency in this project.
```

That means v2.0 should preserve options for:

- Turkish stem/surface-stem pieces
- productive Turkish suffix pieces
- code/file/URL/number protection
- English/code-mixed coverage
- Turkic script/character coverage
- byte fallback as the last-resort lossless layer

## Non-Goals

v1.5 should not:

- change tokenizer behavior just to beat a baseline
- claim Qwen/LLaMA/Mistral internals beyond observable tokenizer behavior
- require large LLM pretraining
- implement MorphBPE yet
- treat token count alone as tokenizer quality
- add broad Turkish suffix rules while tuning against external tokenizers

## Baselines To Add

| Baseline | Role | Notes |
| --- | --- | --- |
| project toy BPE | continuity with v0.8/v0.9 | Already implemented; keep as a sanity baseline. |
| SentencePiece BPE | standard trainable subword baseline | Requires optional dependency and a Turkish demo corpus. |
| SentencePiece Unigram | strong morphology-adjacent baseline | Important because Unigram often competes well on morphology-like segmentation. |
| Qwen tokenizer | production-like multilingual byte-level BPE reference | Evaluate fertility and boundary alignment on Turkish eval text. |
| LLaMA/Mistral tokenizer | widely used LLM tokenizer reference | Evaluate Turkish token fertility and boundary alignment. |
| character/byte fallback baseline | lower-bound diagnostic | Helps separate coverage from morphology quality. |

## Metrics

### Required Intrinsic Metrics

| Metric | Meaning |
| --- | --- |
| avg tokens/example | Compression at example level. |
| avg tokens/word | Token fertility; lower is not always better. |
| boundary precision/recall/F1 | Alignment with gold morphological boundaries. |
| exact match vs gold | Only meaningful for the custom tokenizer; mostly expected low for BPE/LLM tokenizers. |
| protected span break rate | Whether URL/file/code/number spans are broken. |
| byte/unknown fallback rate | Coverage quality for multilingual/Turkic stress examples. |

### Important Interpretation Rule

Token count alone is not quality.

Example:

```text
Geldim
```

A baseline tokenizer may produce:

```text
▁Geldim
```

This is short, but loses the `gel +di +m` boundary information.

The custom tokenizer produces:

```text
▁Gel +di +m
```

This uses more tokens but preserves Turkish morphology.

The useful comparison is therefore:

```text
token budget + boundary F1 + protected span integrity
```

not token count alone.

## Evaluation Sets

v1.5 should run the real baselines on:

| Dataset | Role |
| --- | --- |
| `data/eval/tr_gold_expanded.tsv` | Frozen 50-example morphology regression. |
| `data/eval/tr_challenge.tsv` | Visible dev/error-analysis set. |
| `data/eval/tr_stress_public.tsv` | Public surface/protection/multilingual smoke set. |

No private hidden examples should be added to the public repo.

## Implementation Plan

Current implementation:

- `src/tr_tokenizer/external_baselines.py`
- `scripts/compare_real_tokenizers.py`
- `scripts/train_sentencepiece_baselines.py`
- built-in `custom_tr_morph` and `unicode_char` baselines
- optional Hugging Face tokenizer adapter
- optional SentencePiece adapter
- optional toy BPE model adapter
- Markdown report output

The optional adapters skip cleanly when the package or local model is not
available.

First local SentencePiece demo results:

```text
expanded:
custom_tr_morph avg_tokens/word=2.7438, boundary_f1=1.0000
sp_bpe          avg_tokens/word=2.7273, boundary_f1=0.6263
sp_unigram      avg_tokens/word=3.0744, boundary_f1=0.6325

challenge:
custom_tr_morph avg_tokens/word=2.1749, boundary_f1=0.9220
sp_bpe          avg_tokens/word=2.7807, boundary_f1=0.6497
sp_unigram      avg_tokens/word=2.9321, boundary_f1=0.6225
```

First Qwen reference results:

```text
expanded:
custom_tr_morph avg_tokens/word=2.7438, boundary_f1=1.0000
qwen            avg_tokens/word=3.0661, boundary_f1=0.3317

challenge:
custom_tr_morph avg_tokens/word=2.1749, boundary_f1=0.9220
qwen            avg_tokens/word=2.8590, boundary_f1=0.3511
```

Interpretation: this does not mean Qwen is a poor general tokenizer. Qwen is a
multilingual LLM tokenizer, not a Turkish morpheme-boundary tokenizer. The
useful signal is that Turkish-centered morphology preserves Turkish gold
boundaries better at a comparable or lower token budget on these controlled
sets.

First Mistral reference results:

```text
expanded:
custom_tr_morph avg_tokens/word=2.7438, boundary_f1=1.0000
mistral         avg_tokens/word=4.3306, boundary_f1=0.5423

challenge:
custom_tr_morph avg_tokens/word=2.1749, boundary_f1=0.9220
mistral         avg_tokens/word=3.9426, boundary_f1=0.5463
```

Official Meta LLaMA access attempt:

```text
model_id: meta-llama/Llama-3.2-1B
status: skipped
reason: gated Hugging Face repository; authentication was available, but the
account was not authorized for this model yet
```

If official LLaMA comparison is required later, authenticate with a Hugging Face
token from an account that has access to the model, then rerun:

```powershell
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --hf llama=meta-llama/Llama-3.2-1B --allow-download --markdown-out artifacts/v1_5_llama_report_expanded.md
```

### Step 1: Optional Dependency Boundary

Do not force all users to install heavy tokenizer dependencies.

The optional extra is:

```toml
[project.optional-dependencies]
baselines = [
  "sentencepiece",
  "transformers",
  "tokenizers",
]
```

If these dependencies are unavailable, baseline scripts should print a clear
skip message rather than breaking normal tests.

### Step 2: Wrapper Interface

Create a small adapter layer:

```text
scripts/compare_real_tokenizers.py
src/tr_tokenizer/external_baselines.py
```

Each baseline should expose:

```text
name
encode(text) -> list[str]
decode(tokens) -> str | None
available() -> bool
```

This keeps Qwen, LLaMA/Mistral, SentencePiece, and future tokenizers behind one
comparison interface.

### Step 3: Boundary Mapping

External tokenizers use different token markers and byte representations.

Boundary comparison should not depend on token string aesthetics. It should:

1. decode or reconstruct token surfaces where possible
2. map token spans back to the original text
3. extract character boundary positions
4. compare those boundaries to gold token boundaries

If an external tokenizer cannot provide reliable offsets, the report should say
so and mark boundary F1 as approximate.

### Step 4: Reports

Generate Markdown reports:

```powershell
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --markdown-out artifacts/v1_5_real_tokenizer_report_expanded.md
python scripts/compare_real_tokenizers.py data/eval/tr_challenge.tsv --markdown-out artifacts/v1_5_real_tokenizer_report_challenge.md
```

Optional external references:

```powershell
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --hf qwen=Qwen/Qwen2.5-0.5B --markdown-out artifacts/v1_5_qwen_report.md
python scripts/train_sentencepiece_baselines.py data/train/tr_bpe_train.txt artifacts/sp_bpe_1000 --model-type bpe --vocab-size 1000
python scripts/train_sentencepiece_baselines.py data/train/tr_bpe_train.txt artifacts/sp_unigram_1000 --model-type unigram --vocab-size 1000
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --sentencepiece sp_bpe=artifacts/sp_bpe_1000.model --sentencepiece sp_unigram=artifacts/sp_unigram_1000.model
python scripts/compare_real_tokenizers.py data/eval/tr_gold_expanded.tsv --toy-bpe toy_1000=artifacts/bpe_1000.json
```

By default, Hugging Face loading uses local cache only. Use `--allow-download`
only when an external model download is intentional.

`tr_stress_public.tsv` is not a morphology gold TSV. It stores protected spans
for smoke testing, so it should remain on the stress-report path until real
baseline protected-span metrics are added:

```powershell
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/stress_public_report.md
```

Initial reports should contain:

- summary table by tokenizer
- category table by tokenizer
- worst boundary-F1 examples
- protected span break table
- notes about unavailable optional baselines

## Suggested Baseline Names

Use stable report names even if exact model IDs change:

```text
custom_tr_morph
toy_bpe_200
toy_bpe_500
toy_bpe_1000
sentencepiece_bpe_demo
sentencepiece_unigram_demo
qwen_reference
llama_reference
mistral_reference
char_or_byte_reference
```

Exact external model identifiers should be recorded in the report metadata when
the script runs.

## Risk Controls

- Baseline comparison must not edit tokenizer behavior.
- Real tokenizer downloads or model loading should be explicit and optional.
- Reports should record unavailable baselines rather than silently omitting
  them.
- External tokenizer results should not be used to tune the custom tokenizer
  without a new decision document.
- Hidden/private eval must remain aggregate-only and should not be printed by
  baseline scripts.

## Expected Outcomes

Plausible outcomes:

| Outcome | Interpretation |
| --- | --- |
| custom has higher boundary F1 but more tokens | Expected and useful; morphology is preserved at a sequence-length cost. |
| custom and Qwen have similar token/word but custom higher boundary F1 | Strong signal for Turkish-centered morphology. |
| Qwen/LLaMA have much lower token count but low boundary F1 | Shows compression/morphology tradeoff. |
| SentencePiece Unigram approaches custom boundary F1 | Suggests MorphBPE/Unigram hybrid is important. |
| custom loses on protected span integrity | Protection layer must be hardened before MorphBPE. |

## Resume Point

Before starting v1.5 implementation, the current project state is:

```text
v1.4 Batch 1 complete: protected exact lexical items peki/yeni.
v1.4 Batch 2 complete: guarded possessive-buffered-ablative split.
Current metrics:
  tests: 82 passed
  expanded: 50/50
  challenge: 44/108, f1=0.8255
  proper_name: 9/9
  public stress: 28/28
```

Do not continue S2-S5 until there is an explicit decision. The recommended next
technical track is v1.5 real tokenizer baseline comparison.
