# v2.0 Roundtrip And Wrapper Tax Audit

Config: `configs/v2_0_tiny_lm_marker_calibration.toml`
Split: `valid`
Max lines: `all`

This audit is designed after the lambda-0 advisor review. It blocks
longer BPB work until exact roundtrip and clean-line wrapper tax are
understood.

## Roundtrip Summary

| Tokenizer | Lines | Exact | Failures | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp_unigram_64000_train_only | 1994 | 1985 | 9 | 0.995486 | 0.158319 | 2843294 | 2843331 |
| finite_protected_sp64_numeric_sp_floor | 1994 | 1991 | 3 | 0.998495 | 0.162864 | 2843294 | 2843301 |
| boundary_biased_lambda0_numeric_sp | 1994 | 0 | 1994 | 0.000000 | 0.162451 | 2843294 | 2844873 |
| boundary_biased_lambda4_numeric_sp | 1994 | 0 | 1994 | 0.000000 | 0.163313 | 2843294 | 2844759 |

## Roundtrip Failure Classes

### sp_unigram_64000_train_only

| Class | Count |
| --- | ---: |
| `first_decoded_whitespace,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 7 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,punctuation_count_delta,whitespace_count_delta` | 1 |
| `first_decoded_whitespace,first_raw_punctuation,length_delta,whitespace_count_delta` | 1 |

### finite_protected_sp64_numeric_sp_floor

| Class | Count |
| --- | ---: |
| `first_decoded_whitespace,first_raw_other,length_delta,punctuation_count_delta,whitespace_count_delta` | 2 |
| `first_decoded_whitespace,first_raw_punctuation,length_delta,whitespace_count_delta` | 1 |

### boundary_biased_lambda0_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 803 |
| `first_decoded_other,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 492 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 331 |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 153 |
| `first_decoded_punctuation,first_raw_whitespace,space_only_difference` | 70 |
| `first_decoded_whitespace,first_raw_digit,length_delta,space_only_difference,whitespace_count_delta` | 40 |
| `first_decoded_other,first_raw_whitespace,space_only_difference` | 25 |
| `first_decoded_other,first_raw_whitespace,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 19 |
| `first_decoded_whitespace,first_raw_apostrophe,near_apostrophe,space_only_difference` | 17 |
| `first_decoded_whitespace,first_raw_other,space_only_difference` | 13 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 6 |
| `first_decoded_whitespace,first_raw_digit,space_only_difference` | 5 |

### boundary_biased_lambda4_numeric_sp

| Class | Count |
| --- | ---: |
| `first_decoded_punctuation,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 808 |
| `first_decoded_other,first_raw_whitespace,length_delta,space_only_difference,whitespace_count_delta` | 492 |
| `first_decoded_whitespace,first_raw_apostrophe,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 334 |
| `first_decoded_whitespace,first_raw_other,length_delta,space_only_difference,whitespace_count_delta` | 155 |
| `first_decoded_punctuation,first_raw_whitespace,space_only_difference` | 66 |
| `first_decoded_whitespace,first_raw_digit,length_delta,space_only_difference,whitespace_count_delta` | 41 |
| `first_decoded_other,first_raw_whitespace,space_only_difference` | 23 |
| `first_decoded_other,first_raw_whitespace,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 19 |
| `first_decoded_whitespace,first_raw_apostrophe,near_apostrophe,space_only_difference` | 15 |
| `first_decoded_whitespace,first_raw_other,space_only_difference` | 11 |
| `first_decoded_whitespace,first_raw_other,length_delta,near_apostrophe,space_only_difference,whitespace_count_delta` | 6 |
| `first_decoded_other,first_raw_whitespace,near_apostrophe,space_only_difference` | 4 |

## Clean-Line Wrapper Tax

Only lines without protected routes are included. Positive delta means
the candidate uses more tokens than official SP on clean text.

| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta | Candidate shorter | Candidate longer | Candidate equal |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 484 | 164.2955 | 164.2955 | 0.0000 | 0 | 0 | 484 |
| boundary_biased_lambda0_numeric_sp | 484 | 164.2955 | 163.4380 | -0.8574 | 238 | 92 | 154 |
| boundary_biased_lambda4_numeric_sp | 484 | 164.2955 | 164.4690 | 0.1736 | 164 | 193 | 127 |

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
| `apostrophe` | -47 |
| `whitespace` | -415 |
| `punctuation` | -415 |

### boundary_biased_lambda4_numeric_sp

| Tag | Net token delta |
| --- | ---: |
| `apostrophe` | 238 |
| `whitespace` | 84 |
| `punctuation` | 84 |

## Private Samples

Private raw/decoded samples: `artifacts/private/v2_0_roundtrip_wrapper_tax_audit_valid_after_route_only.samples.jsonl`
