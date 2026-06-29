# v2.0 Protected Route Cost Class Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Splits: `train, valid, test`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Private examples: `artifacts/private/v2_0_protected_route_cost_class_examples_after_apostrophe_pass.jsonl`

This audit breaks the remaining high-cost finite-protected routes into
actionable subclasses before changing the wrapper or starting MorphBPE
work.

## Route Summary

| Route | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 81023 | 279198 | 16587 | 260279 | 122448 | 137831 | 0.932238 | 0.438570 |
| `file_like` | 12264 | 218882 | 8851 | 165789 | 44989 | 120800 | 0.757436 | 0.205540 |
| `apostrophe_surface` | 5018 | 54805 | 2719 | 50164 | 18572 | 31592 | 0.915318 | 0.338874 |

## Class Summary

### `apostrophe_surface`

| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `turkish_buffered_suffix_candidate` | 1405 | 17198 | 555 | 15550 | 4470 | 11080 | 0.904175 | 0.259914 |
| `foreign_or_mixed_apostrophe` | 1152 | 17626 | 987 | 15910 | 5426 | 10484 | 0.902644 | 0.307841 |
| `lexical_transliteration_apostrophe` | 1665 | 13461 | 734 | 12352 | 5816 | 6536 | 0.917614 | 0.432063 |
| `english_contraction_or_possessive` | 796 | 6520 | 443 | 6352 | 2860 | 3492 | 0.974233 | 0.438650 |

### `file_like`

| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `glued_sentence_boundary` | 9472 | 196895 | 7197 | 149373 | 35690 | 113683 | 0.758643 | 0.181264 |
| `dotted_version_or_measurement` | 621 | 8060 | 511 | 6223 | 2062 | 4161 | 0.772084 | 0.255831 |
| `dotted_compound` | 355 | 4604 | 304 | 4112 | 1646 | 2466 | 0.893136 | 0.357515 |
| `dotted_abbreviation_or_version` | 1286 | 6497 | 764 | 4499 | 4299 | 200 | 0.692473 | 0.661690 |
| `underscore_identifier` | 60 | 411 | 45 | 397 | 209 | 188 | 0.965937 | 0.508516 |
| `css_px_value` | 288 | 1512 | 4 | 648 | 576 | 72 | 0.428571 | 0.380952 |
| `known_file_extension` | 15 | 121 | 12 | 97 | 56 | 41 | 0.801653 | 0.462810 |
| `statistical_p_value` | 167 | 782 | 14 | 440 | 451 | -11 | 0.562660 | 0.576726 |

### `numeric_like`

| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `plain_integer_3_4_digit` | 19914 | 72723 | 2021 | 72723 | 23665 | 49058 | 1.000000 | 0.325413 |
| `decimal_or_grouped_number` | 16410 | 72946 | 7729 | 55449 | 34741 | 20708 | 0.760138 | 0.476256 |
| `year_range` | 2985 | 26656 | 1312 | 26656 | 6563 | 20093 | 1.000000 | 0.246211 |
| `plain_integer_2_digit` | 18919 | 37838 | 100 | 37838 | 18964 | 18874 | 1.000000 | 0.501189 |
| `alnum_mixed_text` | 2205 | 22918 | 1893 | 21496 | 6970 | 14526 | 0.937953 | 0.304128 |
| `numeric_range_or_code` | 1843 | 8956 | 857 | 8956 | 3783 | 5173 | 1.000000 | 0.422398 |
| `short_alnum_code` | 3869 | 14492 | 1369 | 14492 | 9824 | 4668 | 1.000000 | 0.677891 |
| `slash_number` | 572 | 3540 | 385 | 3540 | 1605 | 1935 | 1.000000 | 0.453390 |
| `number_with_unit_or_suffix` | 1357 | 4498 | 624 | 4498 | 2830 | 1668 | 1.000000 | 0.629169 |
| `plain_integer_long` | 246 | 1349 | 204 | 1349 | 579 | 770 | 1.000000 | 0.429207 |
| `calendar_date` | 47 | 442 | 47 | 442 | 194 | 248 | 1.000000 | 0.438914 |
| `time` | 51 | 235 | 36 | 235 | 125 | 110 | 1.000000 | 0.531915 |
| `plain_integer_1_digit` | 12605 | 12605 | 10 | 12605 | 12605 | 0 | 1.000000 | 1.000000 |

## Interpretation Gate

- `glued_sentence_boundary` and `alnum_mixed_text` point to corpus quality
  or pretokenization cleanup rather than tokenizer innovation.
- `turkish_buffered_suffix_candidate` points to missing apostrophe suffix
  handling, not a learned-vocabulary problem.
- Classes where protected tokens are much higher than SP tokens should be
  optimized before constrained/MorphBPE work.
