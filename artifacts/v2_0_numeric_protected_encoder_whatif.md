# v2.0 Numeric Protected Encoder What-If Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
SP model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Private examples: `artifacts/private/v2_0_numeric_protected_encoder_whatif_examples.jsonl`

This audit does not change tokenizer behavior. It estimates how much
finite protected token pressure would drop if `numeric_like` used a
different lossless sub-encoder.

Policies:

- `current`: current finite protected pieces plus UTF-8 byte fallback.
- `sp_numeric`: encode numeric surfaces with the SP64 model as an upper
  bound for compression, while still treating the span as logically
  protected in the wrapper.
- `digit2`: a small numeric codec with 2-digit chunks plus literal
  punctuation/letters.
- `digit4`: an optimistic 4-digit chunk codec used only as an upper
  bound; it would require a much larger finite numeric inventory.

## Split What-If Summary

| Split | Lines | Raw bytes | Current finite tpb | Numeric current tokens | Numeric SP tokens | Numeric digit2 tokens | Numeric digit4 tokens | SP numeric what-if tpb | Digit2 what-if tpb | Digit4 what-if tpb |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 0.172871 | 208756 | 98234 | 151083 | 125327 | 0.168028 | 0.170344 | 0.169215 |
| valid | 1994 | 2843294 | 0.176643 | 25759 | 12284 | 18465 | 15250 | 0.171903 | 0.174077 | 0.172947 |
| test | 1998 | 2781995 | 0.177726 | 25855 | 11967 | 18464 | 15222 | 0.172734 | 0.175069 | 0.173904 |

## Numeric Class Cost

| Class | Count | Unique | Bytes | Current tokens | SP tokens | Digit2 tokens | Digit4 tokens | Current-SP delta | Current-Digit2 delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `plain_integer_3_4_digit` | 19916 | 2021 | 72730 | 72730 | 23667 | 39832 | 19916 | 49063 | 32898 |
| `decimal_or_grouped_number` | 16412 | 7730 | 72955 | 55454 | 34744 | 53843 | 50272 | 20710 | 1611 |
| `year_range` | 2985 | 1312 | 26656 | 26656 | 6563 | 14828 | 8975 | 20093 | 11828 |
| `plain_integer_2_digit` | 18927 | 100 | 37854 | 37854 | 18972 | 18927 | 18927 | 18882 | 18927 |
| `alnum_mixed_text` | 2208 | 1896 | 22960 | 21535 | 6980 | 20989 | 20225 | 14555 | 546 |
| `numeric_range_or_code` | 1843 | 857 | 8956 | 8956 | 3783 | 6319 | 5736 | 5173 | 2637 |
| `short_alnum_code` | 3872 | 1369 | 14501 | 14501 | 9832 | 13341 | 12982 | 4669 | 1160 |
| `slash_number` | 572 | 385 | 3540 | 3540 | 1605 | 2345 | 1733 | 1935 | 1195 |
| `number_with_unit_or_suffix` | 1358 | 624 | 4503 | 4503 | 2832 | 3774 | 3534 | 1671 | 729 |
| `plain_integer_long` | 247 | 205 | 1357 | 1357 | 581 | 781 | 504 | 776 | 576 |
| `calendar_date` | 47 | 47 | 442 | 442 | 194 | 273 | 235 | 248 | 169 |
| `time` | 51 | 36 | 235 | 235 | 125 | 153 | 153 | 110 | 82 |
| `plain_integer_1_digit` | 12607 | 10 | 12607 | 12607 | 12607 | 12607 | 12607 | 0 | 0 |

## Interpretation Gate

If `sp_numeric` recovers most wrapper cost, numeric routing should be
redesigned before MorphBPE work. If `digit2` is close to SP, a tiny
lossless numeric codec is a better production-shaped option than
letting normal SP pieces own protected number spans.
