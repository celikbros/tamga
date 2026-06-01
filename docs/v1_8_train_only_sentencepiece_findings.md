# v1.8 Train-Only SentencePiece Findings

Date: 2026-06-01

## Status

```text
fairness prerequisite completed
intrinsic visible-eval result only
not downstream LM evidence
not final tokenizer selection evidence
```

## Purpose

This note records the train-only SentencePiece sweep required by the v1.8 local
LM probe protocol.

The advisor concern was that previous SP baselines were trained on the full
100k pilot, while the local LM probe split is drawn from that same pilot. For
the LM probe, SP vocabularies must not see validation/test text.

The v1.8 train-only sweep fixes that issue by training SP vocabularies only on:

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/train.txt
```

The validation/test split files are not used for SP vocabulary training.

## Artifacts

```text
artifacts/v1_8_train_only_sentencepiece_sweep_expanded.md
artifacts/v1_8_train_only_sentencepiece_sweep_challenge.md
```

Private SP model artifacts are kept under:

```text
artifacts/private/v1_8_train_only_sentencepiece/
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
| sp_bpe_16000_train_only | 2.4804 | 0.6937 | 0/108 |
| sp_unigram_16000_train_only | 2.5666 | 0.7227 | 0/108 |
| sp_bpe_32000_train_only | 2.3081 | 0.7036 | 0/108 |
| sp_unigram_32000_train_only | 2.3864 | 0.7412 | 0/108 |
| sp_bpe_64000_train_only | 2.1619 | 0.7032 | 0/108 |
| sp_unigram_64000_train_only | 2.2010 | 0.7351 | 0/108 |

## Key Expanded Results

Dataset:

```text
data/eval/tr_gold_expanded.tsv
```

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 | 50/50 |
| sp_bpe_16000_train_only | 2.8264 | 0.7038 | 0/50 |
| sp_unigram_16000_train_only | 2.9091 | 0.7123 | 0/50 |
| sp_bpe_32000_train_only | 2.6694 | 0.7171 | 0/50 |
| sp_unigram_32000_train_only | 2.6694 | 0.7423 | 0/50 |
| sp_bpe_64000_train_only | 2.4050 | 0.7228 | 0/50 |
| sp_unigram_64000_train_only | 2.5041 | 0.7551 | 1/50 |

## Interpretation

The train-only fairness fix does not remove the visible boundary-F1 lead of
`custom_tr_morph`.

On `tr_challenge.tsv`, the closest fertility comparison is:

```text
custom_tr_morph:        2.1749 tokens/word, boundary F1 0.9220
sp_bpe_64000_train_only: 2.1619 tokens/word, boundary F1 0.7032
```

The strongest train-only SP challenge F1 in this sweep is:

```text
sp_unigram_32000_train_only: boundary F1 0.7412
```

This remains well below `custom_tr_morph` on the visible challenge set.

## Caveats

These results are still intrinsic and visible-eval only.

They do not prove that the custom tokenizer improves LM loss, downstream
behavior, throughput, or multilingual robustness. They only show that the
boundary-F1 advantage survives the train-only SP vocabulary fairness fix.

The v1.8 local LM probe remains incomplete until at least:

```text
split-overlap check
lossless roundtrip report
hybrid morphology-aware SP baseline
canary diagnostics
tiny LM bits-per-byte probe
```

## Current Decision

```text
Do not hand off custom_tr_morph as a final LLM tokenizer.
Do keep it in the v1.8 probe matrix.
Proceed to split-overlap and roundtrip checks before LM training.
```
