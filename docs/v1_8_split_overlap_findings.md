# v1.8 Split Overlap Findings

Date: 2026-06-01

## Status

```text
split-overlap check completed
no exact train/valid/test duplicates found
near-duplicate candidates found
filtered split created and rechecked clean
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
artifacts/v1_8_local_lm_probe_filtered_split_overlap.md
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

## Filtered Split

The cheap v1.8 fix was applied: keep train unchanged and remove only the
overlap-risk rows from valid/test.

```text
artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/
```

Filtered split line counts:

| Split | Kept lines | Removed lines |
| --- | ---: | ---: |
| train | 16000 | 0 |
| valid | 1994 | 6 |
| test | 1998 | 2 |

The filtered split was rechecked with the same settings:

| Pair | Raw exact pairs | Normalized exact pairs | Near pairs |
| --- | ---: | ---: | ---: |
| train<->valid | 0 | 0 | 0 |
| train<->test | 0 | 0 | 0 |
| valid<->test | 0 | 0 | 0 |

## Current Decision

```text
P5 is cleared for v1.8 screening if LM validation/test loss uses the filtered
split, not the raw valid/test files.
```
