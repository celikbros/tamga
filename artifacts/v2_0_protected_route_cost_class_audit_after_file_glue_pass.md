# v2.0 Protected Route Cost Class Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Splits: `train, valid, test`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Private examples: `artifacts/private/v2_0_protected_route_cost_class_examples_after_file_glue_pass.jsonl`

This audit breaks the remaining high-cost finite-protected routes into
actionable subclasses before changing the wrapper or starting MorphBPE
work.

## Route Summary

| Route | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `numeric_like` | 81045 | 279296 | 16592 | 260370 | 122485 | 137885 | 0.932237 | 0.438549 |
| `file_like` | 8006 | 128795 | 6435 | 102538 | 30495 | 72043 | 0.796133 | 0.236772 |
| `apostrophe_surface` | 3662 | 37989 | 2188 | 34938 | 14276 | 20662 | 0.919687 | 0.375793 |

## Class Summary

### `apostrophe_surface`

| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `foreign_or_mixed_apostrophe` | 1148 | 17567 | 983 | 15854 | 5407 | 10447 | 0.902488 | 0.307793 |
| `lexical_transliteration_apostrophe` | 1659 | 13413 | 729 | 12305 | 5792 | 6513 | 0.917394 | 0.431820 |
| `english_contraction_or_possessive` | 796 | 6520 | 443 | 6352 | 2860 | 3492 | 0.974233 | 0.438650 |
| `turkish_buffered_suffix_candidate` | 59 | 489 | 33 | 427 | 217 | 210 | 0.873211 | 0.443763 |

### `file_like`

| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `glued_sentence_boundary` | 5224 | 106885 | 4787 | 86180 | 21237 | 64943 | 0.806287 | 0.198690 |
| `dotted_version_or_measurement` | 621 | 8060 | 511 | 6223 | 2062 | 4161 | 0.772084 | 0.255831 |
| `dotted_compound` | 352 | 4570 | 302 | 4083 | 1627 | 2456 | 0.893435 | 0.356018 |
| `dotted_abbreviation_or_version` | 1279 | 6454 | 760 | 4470 | 4277 | 193 | 0.692594 | 0.662690 |
| `underscore_identifier` | 60 | 411 | 45 | 397 | 209 | 188 | 0.965937 | 0.508516 |
| `css_px_value` | 288 | 1512 | 4 | 648 | 576 | 72 | 0.428571 | 0.380952 |
| `known_file_extension` | 15 | 121 | 12 | 97 | 56 | 41 | 0.801653 | 0.462810 |
| `statistical_p_value` | 167 | 782 | 14 | 440 | 451 | -11 | 0.562660 | 0.576726 |

### `numeric_like`

| Class | Occurrences | Bytes | Unique surfaces | Protected tokens | SP tokens on same surface | Delta | Protected tokens/byte | SP tokens/byte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `plain_integer_3_4_digit` | 19916 | 72730 | 2021 | 72730 | 23667 | 49063 | 1.000000 | 0.325409 |
| `decimal_or_grouped_number` | 16412 | 72955 | 7730 | 55454 | 34744 | 20710 | 0.760112 | 0.476239 |
| `year_range` | 2985 | 26656 | 1312 | 26656 | 6563 | 20093 | 1.000000 | 0.246211 |
| `plain_integer_2_digit` | 18927 | 37854 | 100 | 37854 | 18972 | 18882 | 1.000000 | 0.501189 |
| `alnum_mixed_text` | 2208 | 22960 | 1896 | 21535 | 6980 | 14555 | 0.937936 | 0.304007 |
| `numeric_range_or_code` | 1843 | 8956 | 857 | 8956 | 3783 | 5173 | 1.000000 | 0.422398 |
| `short_alnum_code` | 3872 | 14501 | 1369 | 14501 | 9832 | 4669 | 1.000000 | 0.678022 |
| `slash_number` | 572 | 3540 | 385 | 3540 | 1605 | 1935 | 1.000000 | 0.453390 |
| `number_with_unit_or_suffix` | 1358 | 4503 | 624 | 4503 | 2832 | 1671 | 1.000000 | 0.628914 |
| `plain_integer_long` | 247 | 1357 | 205 | 1357 | 581 | 776 | 1.000000 | 0.428150 |
| `calendar_date` | 47 | 442 | 47 | 442 | 194 | 248 | 1.000000 | 0.438914 |
| `time` | 51 | 235 | 36 | 235 | 125 | 110 | 1.000000 | 0.531915 |
| `plain_integer_1_digit` | 12607 | 12607 | 10 | 12607 | 12607 | 0 | 1.000000 | 1.000000 |

## Interpretation Gate

- `glued_sentence_boundary` and `alnum_mixed_text` point to corpus quality
  or pretokenization cleanup rather than tokenizer innovation.
- `turkish_buffered_suffix_candidate` points to missing apostrophe suffix
  handling, not a learned-vocabulary problem.
- Classes where protected tokens are much higher than SP tokens should be
  optimized before constrained/MorphBPE work.
