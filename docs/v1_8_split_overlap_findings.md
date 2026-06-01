# v1.8 Split Overlap Findings

Date: 2026-06-01

## Status

```text
split-overlap check completed
no exact train/valid/test duplicates found
near-duplicate candidates found
do not use raw valid/test loss until candidates are handled
```

## Scope

Checked the v1.8 local LM probe raw split:

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split/
```

Settings:

```text
word shingle size: 8
minimum near-check words: 8
near-duplicate containment threshold: 0.80
```

Public report:

```text
artifacts/v1_8_local_lm_probe_split_overlap.md
```

The public report does not include private corpus text snippets.

## Summary

| Pair | Raw exact pairs | Normalized exact pairs | Near pairs |
| --- | ---: | ---: | ---: |
| train<->valid | 0 | 0 | 6 |
| train<->test | 0 | 0 | 2 |
| valid<->test | 0 | 0 | 0 |

## Interpretation

The split has no exact leakage between train, valid, and test.

However, there are 8 high-overlap train-to-eval candidates:

```text
6 valid rows
2 test rows
```

These are not enough to invalidate the split, but they are enough to avoid
using raw valid/test bits-per-byte as a clean signal without handling them.

## Required Action Before LM Loss

Use one of these two approaches before running the tiny LM probe:

```text
preferred: write filtered valid/test files that exclude the 8 near-overlap rows
alternative: regenerate the split with document/group-aware deduplication
```

The first option is cheaper and sufficient for v1.8 screening because the
training split can remain unchanged and all tokenizers can be evaluated on the
same filtered valid/test text.

## Current Decision

```text
P5 is completed as a check.
P5 is not fully cleared for LM loss until the 8 near-overlap eval rows are
excluded or the split is regenerated.
```
