# v2.0 Roundtrip And Wrapper Tax Audit

Config: `configs/v2_0_tiny_lm_marker_calibration.toml`
Split: `valid`
Max lines: `20`

This audit is designed after the lambda-0 advisor review. It blocks
longer BPB work until exact roundtrip and clean-line wrapper tax are
understood.

## Roundtrip Summary

| Tokenizer | Lines | Exact | Failures | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp_unigram_64000_train_only | 20 | 20 | 0 | 1.000000 | 0.151190 | 57669 | 57669 |
| finite_protected_sp64_numeric_sp_floor | 20 | 0 | 20 | 0.000000 | 0.272174 | 57669 | 65210 |
| boundary_biased_lambda0_numeric_sp | 20 | 0 | 20 | 0.000000 | 0.261146 | 57669 | 88766 |
| boundary_biased_lambda4_numeric_sp | 20 | 0 | 20 | 0.000000 | 0.262065 | 57669 | 88765 |

## Roundtrip Failure Classes

### sp_unigram_64000_train_only

No failures.

### finite_protected_sp64_numeric_sp_floor

| Class | Count |
| --- | ---: |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 17 |
| `first_decoded_whitespace,first_raw_digit,length_delta,space_only_difference,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_punctuation,length_delta,space_only_difference,whitespace_count_delta` | 1 |

### boundary_biased_lambda0_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 17 |
| `first_decoded_punctuation,first_raw_digit,length_delta,punctuation_count_delta,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,punctuation_count_delta,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 1 |

### boundary_biased_lambda4_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 17 |
| `first_decoded_punctuation,first_raw_digit,length_delta,punctuation_count_delta,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,punctuation_count_delta,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 1 |

## Clean-Line Wrapper Tax

Only lines without protected routes are included. Positive delta means
the candidate uses more tokens than official SP on clean text.

| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta | Candidate shorter | Candidate longer | Candidate equal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 4 | 438.0000 | 780.7500 | 342.7500 | 0 | 4 | 0 |
| boundary_biased_lambda0_numeric_sp | 4 | 438.0000 | 751.7500 | 313.7500 | 0 | 4 | 0 |
| boundary_biased_lambda4_numeric_sp | 4 | 438.0000 | 754.7500 | 316.7500 | 0 | 4 | 0 |

## Wrapper Tax By Line Tag

### finite_protected_sp64_numeric_sp_floor

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 1371 |
| `whitespace` | 1371 |
| `punctuation` | 1371 |

### boundary_biased_lambda0_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 1255 |
| `whitespace` | 1255 |
| `punctuation` | 1255 |

### boundary_biased_lambda4_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 1267 |
| `whitespace` | 1267 |
| `punctuation` | 1267 |

## Private Samples

Private raw/decoded samples: `artifacts/private/v2_0_roundtrip_wrapper_tax_audit_smoke_after_whitespace_segment.samples.jsonl`
