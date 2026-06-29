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
| finite_protected_sp64_numeric_sp_floor | 20 | 0 | 20 | 0.000000 | 0.161993 | 57669 | 58856 |
| boundary_biased_lambda0_numeric_sp | 20 | 0 | 20 | 0.000000 | 0.154277 | 57669 | 57942 |
| boundary_biased_lambda4_numeric_sp | 20 | 0 | 20 | 0.000000 | 0.155196 | 57669 | 57941 |

## Roundtrip Failure Classes

### sp_unigram_64000_train_only

No failures.

### finite_protected_sp64_numeric_sp_floor

| Class | Count |
| --- | ---: |
| `first_decoded_whitespace,first_raw_punctuation,length_delta,space_only_difference,whitespace_count_delta` | 12 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 7 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 1 |

### boundary_biased_lambda0_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 8 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 7 |
| `first_decoded_other,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 2 |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 2 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 1 |

### boundary_biased_lambda4_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 8 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 7 |
| `first_decoded_other,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 2 |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 2 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 1 |

## Clean-Line Wrapper Tax

Only lines without protected routes are included. Positive delta means
the candidate uses more tokens than official SP on clean text.

| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta | Candidate shorter | Candidate longer | Candidate equal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 4 | 438.0000 | 461.2500 | 23.2500 | 0 | 4 | 0 |
| boundary_biased_lambda0_numeric_sp | 4 | 438.0000 | 434.7500 | -3.2500 | 3 | 0 | 1 |
| boundary_biased_lambda4_numeric_sp | 4 | 438.0000 | 437.7500 | -0.2500 | 2 | 1 | 1 |

## Wrapper Tax By Line Tag

### finite_protected_sp64_numeric_sp_floor

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 93 |
| `whitespace` | 93 |
| `punctuation` | 93 |

### boundary_biased_lambda0_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | -13 |
| `whitespace` | -13 |
| `punctuation` | -13 |

### boundary_biased_lambda4_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | -1 |
| `whitespace` | -1 |
| `punctuation` | -1 |

## Private Samples

Private raw/decoded samples: `artifacts/private/v2_0_roundtrip_wrapper_tax_audit_smoke.samples.jsonl`
