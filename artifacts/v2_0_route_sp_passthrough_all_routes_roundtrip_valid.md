# v2.0 Boundary Encoder Roundtrip Audit

Config: `configs/v2_0_tiny_lm_route_sp_passthrough.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Split: `valid`

This audit checks whether tokenizer IDs decode back to the exact raw
line text. Public samples omit raw text; private samples, when written,
are stored separately.

## Summary

| Tokenizer | Lines | Exact | Failures | Decode errors | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_all_sp_routes | 1994 | 1994 | 0 | 0 | 1.000000 | 0.158326 | 2843294 | 2843294 |

## Failure Samples

### finite_protected_sp64_all_sp_routes

No failures.

## Private Samples

Private failure samples: `artifacts/private/v2_0_route_sp_passthrough_all_routes_roundtrip_valid_failures.jsonl`
