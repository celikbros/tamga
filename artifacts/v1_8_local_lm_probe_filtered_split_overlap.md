# v1.8 Local LM Probe Split Overlap

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Word shingle size: `8`
Minimum near-check words: `8`
Near-duplicate containment threshold: `0.8000`

This report checks raw train/valid/test split hygiene before LM-loss
comparison. It does not include private corpus snippets.

## Summary

| Pair | Left lines | Right lines | Raw exact pairs | Normalized exact pairs | Near pairs | Max containment | Max Jaccard |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train<->valid | 16000 | 1994 | 0 | 0 | 0 | 0.0000 | 0.0000 |
| train<->test | 16000 | 1998 | 0 | 0 | 0 | 0.0000 | 0.0000 |
| valid<->test | 1994 | 1998 | 0 | 0 | 0 | 0.0000 | 0.0000 |

## Details

Rows and source line indexes are reported instead of text snippets.

### train<->valid

No exact or near-duplicate overlap found.

### train<->test

No exact or near-duplicate overlap found.

### valid<->test

No exact or near-duplicate overlap found.
