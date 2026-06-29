# v2.0 Boundary Encoder Roundtrip Audit

Config: `configs/v2_0_tiny_lm_marker_calibration.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Split: `valid`

This audit checks whether tokenizer IDs decode back to the exact raw
line text. Public samples omit raw text; private samples, when written,
are stored separately.

## Summary

| Tokenizer | Lines | Exact | Failures | Decode errors | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp_unigram_64000_train_only | 20 | 20 | 0 | 0 | 1.000000 | 0.151190 | 57669 | 57669 |

## Failure Samples

### sp_unigram_64000_train_only

No failures.

## Private Samples

Private failure samples: `artifacts/private/v2_0_boundary_encoder_roundtrip_audit_sp64_smoke_failures.jsonl`
