# v1.8 Local LM Probe Split Overlap

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/raw_split`
Word shingle size: `8`
Minimum near-check words: `8`
Near-duplicate containment threshold: `0.8000`

This report checks raw train/valid/test split hygiene before LM-loss
comparison. It does not include private corpus snippets.

## Summary

| Pair | Left lines | Right lines | Raw exact pairs | Normalized exact pairs | Near pairs | Max containment | Max Jaccard |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train<->valid | 16000 | 2000 | 0 | 0 | 6 | 1.0000 | 0.8333 |
| train<->test | 16000 | 2000 | 0 | 0 | 2 | 1.0000 | 0.8000 |
| valid<->test | 2000 | 2000 | 0 | 0 | 0 | 0.0000 | 0.0000 |

## Details

Rows and source line indexes are reported instead of text snippets.

### train<->valid


| Left row | Left source | Right row | Right source | Shared shingles | Containment | Jaccard |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4282 | 5373 | 545 | 5374 | 64 | 1.0000 | 0.4638 |
| 12282 | 15337 | 1523 | 15487 | 155 | 0.9172 | 0.8333 |
| 3348 | 4199 | 435 | 4163 | 40 | 0.9091 | 0.1455 |
| 12281 | 15336 | 1508 | 15335 | 60 | 0.8955 | 0.7500 |
| 4495 | 5636 | 569 | 5637 | 52 | 0.8667 | 0.7647 |
| 4510 | 5658 | 572 | 5660 | 23 | 0.8214 | 0.5750 |

### train<->test


| Left row | Left source | Right row | Right source | Shared shingles | Containment | Jaccard |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3932 | 4924 | 495 | 4931 | 4 | 1.0000 | 0.8000 |
| 9343 | 11675 | 1199 | 11689 | 88 | 0.8544 | 0.7040 |

### valid<->test

No exact or near-duplicate overlap found.

## Filtered Split

Filtered split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`

| Split | Kept lines | Removed lines |
| --- | ---: | ---: |
| train | 16000 | 0 |
| valid | 1994 | 6 |
| test | 1998 | 2 |
