# v2.0 Roundtrip And Wrapper Tax Audit

Config: `configs/v2_0_tiny_lm_marker_calibration.toml`
Split: `test`
Max lines: `all`

This audit is designed after the lambda-0 advisor review. It blocks
longer BPB work until exact roundtrip and clean-line wrapper tax are
understood.

## Roundtrip Summary

| Tokenizer | Lines | Exact | Failures | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp_unigram_64000_train_only | 1998 | 1989 | 9 | 0.995495 | 0.158902 | 2781995 | 2782021 |
| finite_protected_sp64_numeric_sp_floor | 1998 | 1998 | 0 | 1.000000 | 0.163779 | 2781995 | 2781995 |
| boundary_biased_lambda0_numeric_sp | 1998 | 0 | 1998 | 0.000000 | 0.163120 | 2781995 | 2783439 |
| boundary_biased_lambda4_numeric_sp | 1998 | 0 | 1998 | 0.000000 | 0.163968 | 2781995 | 2783314 |

## Roundtrip Failure Classes

### sp_unigram_64000_train_only

| Class | Count |
| --- | ---: |
| `first_decoded_whitespace,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 8 |
| `first_decoded_whitespace,first_raw_combining,length_delta,punctuation_count_delta,whitespace_count_delta` | 1 |

### finite_protected_sp64_numeric_sp_floor

No failures.

### boundary_biased_lambda0_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 793 |
| `first_decoded_other,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 500 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 332 |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 163 |
| `first_decoded_punctuation,first_raw_whitespace,space_only_difference` | 70 |
| `first_decoded_whitespace,first_raw_digit,length_delta,space_only_difference,whitespace_count_delta` | 34 |
| `first_decoded_other,first_raw_whitespace,space_only_difference` | 29 |
| `first_decoded_other,first_raw_whitespace,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 25 |
| `first_decoded_whitespace,first_raw_other,space_only_difference` | 15 |
| `first_decoded_whitespace,first_raw_apostrophe,near_apostrophe,space_only_difference` | 12 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 7 |
| `first_decoded_whitespace,first_raw_punctuation,length_delta,space_only_difference,whitespace_count_delta` | 4 |

### boundary_biased_lambda4_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 790 |
| `first_decoded_other,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 502 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 330 |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 163 |
| `first_decoded_punctuation,first_raw_whitespace,space_only_difference` | 73 |
| `first_decoded_whitespace,first_raw_digit,length_delta,space_only_difference,whitespace_count_delta` | 34 |
| `first_decoded_other,first_raw_whitespace,space_only_difference` | 28 |
| `first_decoded_other,first_raw_whitespace,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 25 |
| `first_decoded_whitespace,first_raw_other,space_only_difference` | 14 |
| `first_decoded_whitespace,first_raw_apostrophe,near_apostrophe,space_only_difference` | 14 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 7 |
| `first_decoded_whitespace,first_raw_punctuation,length_delta,space_only_difference,whitespace_count_delta` | 4 |

## Clean-Line Wrapper Tax

Only lines without protected routes are included. Positive delta means
the candidate uses more tokens than official SP on clean text.

| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta | Candidate shorter | Candidate longer | Candidate equal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 526 | 158.6331 | 158.6331 | 0.0000 | 0 | 0 | 526 |
| boundary_biased_lambda0_numeric_sp | 526 | 158.6331 | 157.9639 | -0.6692 | 236 | 99 | 191 |
| boundary_biased_lambda4_numeric_sp | 526 | 158.6331 | 158.9905 | 0.3574 | 153 | 219 | 154 |

## Wrapper Tax By Line Tag

### finite_protected_sp64_numeric_sp_floor

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 0 |
| `whitespace` | 0 |
| `punctuation` | 0 |

### boundary_biased_lambda0_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | -45 |
| `whitespace` | -352 |
| `punctuation` | -352 |

### boundary_biased_lambda4_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 214 |
| `whitespace` | 188 |
| `punctuation` | 188 |

## Private Samples

Private raw/decoded samples: `artifacts/private/v2_0_roundtrip_wrapper_tax_audit_test_after_route_only_byte_fallback.samples.jsonl`
