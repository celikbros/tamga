# v2.0 Boundary Encoder Roundtrip Audit

Config: `configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Split: `test`

This audit checks whether tokenizer IDs decode back to the exact raw
line text. Public samples omit raw text; private samples, when written,
are stored separately.

## Summary

| Tokenizer | Lines | Exact | Failures | Decode errors | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sp64_protected_presplit_sidecar | 1998 | 1998 | 0 | 0 | 1.000000 | 0.165037 | 2781995 | 2781995 |

## Failure Samples

### sp64_protected_presplit_sidecar

No failures.

## Private Samples

Private failure samples: `artifacts/private/v2_1_presplit_sidecar_roundtrip_test_failures.jsonl`
