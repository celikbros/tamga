# v2.0 Protected Boundary Alignment Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Private samples: `artifacts/private/v2_0_protected_boundary_alignment_samples.jsonl`

This audit checks whether detected protected-span boundaries align with
SentencePiece token boundaries. Logical sidecar protection is only strong
enough for masking/copy policies if span edges are token-boundary aligned.

## Split Summary

| Split | Lines | Protected spans | Protected edges | Aligned edges | Misaligned edges | Edge alignment rate | Crossing pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 1994 | 9545 | 19090 | 8663 | 10427 | 0.453798 | 9447 |
| test | 1998 | 9234 | 18468 | 8564 | 9904 | 0.463721 | 9014 |

## Route Summary

| Split | Route | Spans | Misaligned edges | Crossing pieces |
| --- | --- | ---: | ---: | ---: |
| valid | `apostrophe_surface` | 363 | 319 | 319 |
| valid | `arabic_word` | 6 | 0 | 0 |
| valid | `cyrillic_word` | 2 | 0 | 0 |
| valid | `file_like` | 766 | 703 | 703 |
| valid | `greek_word` | 45 | 14 | 14 |
| valid | `non_turkish_latin_word` | 205 | 181 | 181 |
| valid | `numeric_like` | 8152 | 9204 | 8224 |
| valid | `uzbek_apostrophe_word` | 6 | 6 | 6 |
| test | `apostrophe_surface` | 335 | 283 | 283 |
| test | `cyrillic_word` | 9 | 0 | 0 |
| test | `file_like` | 870 | 821 | 821 |
| test | `greek_word` | 56 | 28 | 28 |
| test | `non_turkish_latin_word` | 176 | 151 | 151 |
| test | `numeric_like` | 7781 | 8614 | 7724 |
| test | `uzbek_apostrophe_word` | 7 | 7 | 7 |

## Gate

For sidecar/logical protected spans to be a strong tokenizer contract,
the preferred result is:

```text
misaligned_edges = 0
crossing_pieces = 0
```
