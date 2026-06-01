# v1.7 Downstream Probe Handoff

Date: 2026-06-01

## Purpose

This handoff turns the downstream probe protocol into a concrete LLM-team task.

The tokenizer team has prepared:

```text
same corpus split
same tokenizer comparison set
private token JSONL outputs
public aggregate prep report
```

The LLM team should now run a small LM comparison and report byte-normalized
loss.

## Inputs

Config:

```text
configs/v1_7_downstream_probe_celik_gold_clean_pilot.toml
```

Public report:

```text
artifacts/v1_7_downstream_probe_prep_celik_gold_clean_pilot.md
```

Private tokenized outputs:

```text
artifacts/private/v1_7_downstream_probe/celik_gold_clean_pilot_20k/
```

Raw split source:

```text
data/train/claim_grade/celik_gold_clean_pilot.txt
```

All private files above are local-only and git-ignored.

## Prepared Split

| Split | Lines | Bytes | Words |
| --- | ---: | ---: | ---: |
| train | 16000 | 21.76 MiB | 2603245 |
| valid | 2000 | 2.72 MiB | 324562 |
| test | 2000 | 2.65 MiB | 316529 |

The split seed is:

```text
20260601
```

## Tokenizer Set

The prepared tokenizers are:

| Tokenizer | Role |
| --- | --- |
| `custom_tr_morph` | project tokenizer candidate |
| `unicode_char` | high-fertility lower-bound baseline |
| `sp_bpe_8000_celik_gold_clean` | clean local SP BPE baseline |
| `sp_unigram_8000_celik_gold_clean` | clean local SP Unigram baseline |
| `sp_bpe_16000_celik_gold_clean` | larger clean local SP BPE baseline |
| `sp_unigram_16000_celik_gold_clean` | larger clean local SP Unigram baseline |
| `sp_bpe_32000_celik_gold_clean` | closest-fertility clean local SP BPE baseline |
| `sp_unigram_32000_celik_gold_clean` | closest-fertility clean local SP Unigram baseline |
| `sp_bpe_64000_celik_gold_clean` | large-vocab clean local SP BPE baseline |
| `sp_unigram_64000_celik_gold_clean` | large-vocab clean local SP Unigram baseline |

Recommended minimum first LM run:

```text
custom_tr_morph
sp_unigram_32000_celik_gold_clean
sp_bpe_32000_celik_gold_clean
sp_unigram_64000_celik_gold_clean
sp_unigram_16000_celik_gold_clean
unicode_char
```

If time permits, include the 8k SP baselines too.

## Prep Metrics

Validation split:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4931 | 0.170166 | 5.8766 |
| unicode_char | 7.0540 | 0.803931 | 1.2439 |
| sp_bpe_8000_celik_gold_clean | 1.9272 | 0.219642 | 4.5529 |
| sp_unigram_8000_celik_gold_clean | 1.8791 | 0.214160 | 4.6694 |
| sp_bpe_16000_celik_gold_clean | 1.6775 | 0.191180 | 5.2307 |
| sp_unigram_16000_celik_gold_clean | 1.6464 | 0.187635 | 5.3295 |
| sp_bpe_32000_celik_gold_clean | 1.5014 | 0.171116 | 5.8440 |
| sp_unigram_32000_celik_gold_clean | 1.4844 | 0.169170 | 5.9112 |
| sp_bpe_64000_celik_gold_clean | 1.3776 | 0.156997 | 6.3696 |
| sp_unigram_64000_celik_gold_clean | 1.3703 | 0.156169 | 6.4033 |

Test split:

| Tokenizer | Avg tokens/word | Tokens/byte | Bytes/token |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.4925 | 0.169754 | 5.8909 |
| unicode_char | 7.0689 | 0.803977 | 1.2438 |
| sp_bpe_8000_celik_gold_clean | 1.9407 | 0.220729 | 4.5305 |
| sp_unigram_8000_celik_gold_clean | 1.8923 | 0.215217 | 4.6465 |
| sp_bpe_16000_celik_gold_clean | 1.6884 | 0.192026 | 5.2076 |
| sp_unigram_16000_celik_gold_clean | 1.6582 | 0.188597 | 5.3023 |
| sp_bpe_32000_celik_gold_clean | 1.5109 | 0.171842 | 5.8193 |
| sp_unigram_32000_celik_gold_clean | 1.4942 | 0.169943 | 5.8843 |
| sp_bpe_64000_celik_gold_clean | 1.3857 | 0.157606 | 6.3450 |
| sp_unigram_64000_celik_gold_clean | 1.3775 | 0.156664 | 6.3831 |

Observation:

```text
custom_tr_morph is close to the 32k SP baselines in token fertility and has much
better visible morphology-boundary F1. The 64k SP baselines use fewer tokens per
byte, so byte-normalized LM loss is the required decision metric.
```

## Required LLM Metrics

Primary:

```text
validation bits-per-byte
test bits-per-byte
```

Secondary:

```text
training loss curve
tokens/sec
bytes/sec
wall-clock time
GPU memory
max effective context in bytes
```

Report token-level perplexity only as a secondary internal metric. It is not
directly comparable across tokenizer vocabularies and token counts.

## Fairness Rules

Every tokenizer run must use:

```text
same train/valid/test split
same model architecture
same optimizer and schedule
same batch construction policy
same training budget definition
same random seed when possible
```

If the training budget is fixed by tokens, report bytes seen.
If the training budget is fixed by bytes, report tokens seen.

## Suggested Small-LM Setup

The LLM team can choose the implementation. A minimal probe should be small
enough to run quickly:

```text
5M-30M parameters
4-8 layers
context length fixed in tokens, with byte-normalized reporting
1 seed first, 3 seeds if affordable
```

This is a screening probe. It should not be treated as final pretraining proof.

## Decision Readout

After the LLM team runs the probe, fill this table:

| Tokenizer | Valid bits/byte | Test bits/byte | Tokens/sec | Bytes/sec | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | TBD | TBD | TBD | TBD |  |
| sp_unigram_32000_celik_gold_clean | TBD | TBD | TBD | TBD |  |
| sp_bpe_32000_celik_gold_clean | TBD | TBD | TBD | TBD |  |
| sp_unigram_64000_celik_gold_clean | TBD | TBD | TBD | TBD |  |
| sp_unigram_16000_celik_gold_clean | TBD | TBD | TBD | TBD |  |
| unicode_char | TBD | TBD | TBD | TBD |  |

Decision rule:

```text
If custom_tr_morph is comparable or better in bits-per-byte and does not create
throughput/context pressure, it is a valid LLM pilot candidate.

If custom_tr_morph is clearly worse in bits-per-byte, keep it as a morphology
research tokenizer but do not recommend it as the default LLM tokenizer yet.
```

## What Not To Do

Do not:

- add new Turkish morphology rules before this probe
- choose a tokenizer based only on visible boundary F1
- compare token-level perplexity as the primary metric
- publish private token JSONL files
- treat this pilot as production tokenizer certification

## Next Tokenizer-Team Action

After the LLM team returns the probe table, the tokenizer team should write:

```text
docs/v1_7_downstream_probe_result_triage.md
```

That triage should recommend one of:

```text
pilot custom_tr_morph in the LLM project
pilot SP Unigram/BPE while continuing morphology research
run a larger corpus/vocab sweep before deciding
```
