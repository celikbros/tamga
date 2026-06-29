# v2.0 Protected Boundary Alignment Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
SP passthrough routes: `apostrophe_surface, arabic_word, cyrillic_word, file_like, greek_word, non_turkish_latin_word, numeric_like, uzbek_apostrophe_word`
Isolate SP passthrough routes: `False`
Byte fallback crossing pieces: `True`
Private samples: `artifacts/private/v2_0_protected_boundary_alignment_all_routes_edge_safe_samples.jsonl`

This audit checks whether detected protected-span boundaries align with
SentencePiece token boundaries. Logical sidecar protection is only strong
enough for masking/copy policies if span edges are token-boundary aligned.

## Split Summary

| Split | Lines | Protected spans | Protected edges | Aligned edges | Misaligned edges | Edge alignment rate | Crossing pieces |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| valid | 1994 | 9545 | 19090 | 19090 | 0 | 1.000000 | 0 |
| test | 1998 | 9234 | 18468 | 18468 | 0 | 1.000000 | 0 |

## Route Summary

| Split | Route | Spans | Misaligned edges | Crossing pieces |
| --- | --- | ---: | ---: | ---: |
| valid | `apostrophe_surface` | 363 | 0 | 0 |
| valid | `arabic_word` | 6 | 0 | 0 |
| valid | `cyrillic_word` | 2 | 0 | 0 |
| valid | `file_like` | 766 | 0 | 0 |
| valid | `greek_word` | 45 | 0 | 0 |
| valid | `non_turkish_latin_word` | 205 | 0 | 0 |
| valid | `numeric_like` | 8152 | 0 | 0 |
| valid | `uzbek_apostrophe_word` | 6 | 0 | 0 |
| test | `apostrophe_surface` | 335 | 0 | 0 |
| test | `cyrillic_word` | 9 | 0 | 0 |
| test | `file_like` | 870 | 0 | 0 |
| test | `greek_word` | 56 | 0 | 0 |
| test | `non_turkish_latin_word` | 176 | 0 | 0 |
| test | `numeric_like` | 7781 | 0 | 0 |
| test | `uzbek_apostrophe_word` | 7 | 0 | 0 |

## Gate

For sidecar/logical protected spans to be a strong tokenizer contract,
the preferred result is:

```text
misaligned_edges = 0
crossing_pieces = 0
```
