# v2.1 Sidecar Detector Adversarial Battery

This generated battery stresses protected-span detection before any
pre-split training run. Under pre-split semantics, detector decisions
affect model-token boundaries, so detector failures are training-time
failures rather than metadata-only failures.

## Summary

| Cases | Expected spans | Detected spans | TP | FP | FN | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 61 | 62 | 62 | 62 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |

## Category Summary

| Category | Cases | Missed expected spans | False positive spans |
| --- | ---: | ---: | ---: |
| `nested_or_comparator` | 3 | 0 | 0 |
| `numeric_suffix_attachment` | 20 | 0 | 0 |
| `percent_encoded_suffix` | 12 | 0 | 0 |
| `protected_suffix_attachment` | 16 | 0 | 0 |
| `span_adjacent_punctuation` | 6 | 0 | 0 |
| `span_at_line_edge` | 4 | 0 | 0 |

## Failure Samples

No detector mismatches.