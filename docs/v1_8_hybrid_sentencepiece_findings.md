# v1.8 Hybrid SentencePiece Findings

Date: 2026-06-02

## Status

```text
hybrid SP sweep completed
max_sentence_length = 20000
all 16000 hybrid-pretokenized train lines loaded
intrinsic visible-eval result only
not downstream LM evidence
```

## Purpose

This note records the morphology-aware hybrid SentencePiece baseline requested
by the v1.8 advisor review.

The hybrid baseline trains SentencePiece on a private corpus created by first
applying the deterministic custom tokenizer and then separating its pieces with
spaces. This makes the custom morphology/protection boundaries a hard
pretokenization prior for learned BPE/Unigram models.

## Artifacts

```text
artifacts/v1_8_hybrid_sentencepiece_sweep_expanded.md
artifacts/v1_8_hybrid_sentencepiece_sweep_challenge.md
```

Private model artifacts are kept under:

```text
artifacts/private/v1_8_hybrid_sentencepiece/
```

and must not be committed.

## Key Challenge Results

Dataset:

```text
data/eval/tr_challenge.tsv
```

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 | 44/108 |
| hybrid_morph_pretok_bpe_32000_train_only | 2.4778 | 0.7255 | 0/108 |
| hybrid_morph_pretok_unigram_32000_train_only | 2.7337 | 0.7580 | 0/108 |
| hybrid_morph_pretok_bpe_64000_train_only | 2.3185 | 0.7370 | 0/108 |
| hybrid_morph_pretok_unigram_64000_train_only | 2.5379 | 0.7633 | 0/108 |

## Key Expanded Results

Dataset:

```text
data/eval/tr_gold_expanded.tsv
```

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 | 50/50 |
| hybrid_morph_pretok_bpe_32000_train_only | 2.9421 | 0.7177 | 0/50 |
| hybrid_morph_pretok_unigram_32000_train_only | 3.0992 | 0.8270 | 0/50 |
| hybrid_morph_pretok_bpe_64000_train_only | 2.7025 | 0.7478 | 1/50 |
| hybrid_morph_pretok_unigram_64000_train_only | 2.9587 | 0.8441 | 1/50 |

## Interpretation

The hybrid hard-boundary prior helps some learned baselines, especially Unigram,
but it does not close the gap to the deterministic custom tokenizer on visible
boundary metrics.

On `tr_challenge.tsv`, the best hybrid boundary F1 is:

```text
hybrid_morph_pretok_unigram_64000_train_only: 0.7633
```

This is higher than the best raw train-only SP result previously observed:

```text
sp_unigram_32000_train_only: 0.7412
```

but still far below:

```text
custom_tr_morph: 0.9220
```

The best hybrid also has higher token fertility than `custom_tr_morph`:

```text
hybrid_morph_pretok_unigram_64000_train_only: 2.5379 tokens/word
custom_tr_morph:                            2.1749 tokens/word
```

## Caveats

These are intrinsic visible-eval results, not LM-loss or downstream evidence.

The current hybrid is a hard-boundary pretokenized training corpus, not a final
generation-ready tokenizer serialization. It is useful as a v1.8 baseline and as
a v2.0 design signal.

## Current Decision

```text
P3 is completed for v1.8 intrinsic screening.
Keep hybrid designs in the v2.0 search space.
Do not promote the current hard-boundary hybrid as an LLM-ready tokenizer.
Proceed to P6 canary diagnostics before any tiny LM bits-per-byte probe.
```
