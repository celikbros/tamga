# v2.0 Boundary Encoder Roundtrip Audit

Config: `configs/v2_0_tiny_lm_route_sp_passthrough.toml`
Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Split: `test`

This audit checks whether tokenizer IDs decode back to the exact raw
line text. Public samples omit raw text; private samples, when written,
are stored separately.

## Summary

| Tokenizer | Lines | Exact | Failures | Decode errors | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_all_sp_routes_isolated | 1998 | 526 | 1472 | 0 | 0.263263 | 0.165058 | 2781995 | 2800366 |

## Failure Samples

### finite_protected_sp64_all_sp_routes_isolated

- line `6` reason `mismatch`
  - raw bytes/chars: `1895` / `1694`
  - decoded bytes/chars: `1907` / `1706`
  - first diff index: `99`
- line `7` reason `mismatch`
  - raw bytes/chars: `1409` / `1265`
  - decoded bytes/chars: `1415` / `1271`
  - first diff index: `79`
- line `8` reason `mismatch`
  - raw bytes/chars: `2995` / `2731`
  - decoded bytes/chars: `3003` / `2739`
  - first diff index: `51`
- line `10` reason `mismatch`
  - raw bytes/chars: `3106` / `2813`
  - decoded bytes/chars: `3118` / `2825`
  - first diff index: `432`
- line `11` reason `mismatch`
  - raw bytes/chars: `2731` / `2503`
  - decoded bytes/chars: `2751` / `2523`
  - first diff index: `189`
- line `12` reason `mismatch`
  - raw bytes/chars: `2989` / `2695`
  - decoded bytes/chars: `2991` / `2697`
  - first diff index: `780`
- line `13` reason `mismatch`
  - raw bytes/chars: `2849` / `2553`
  - decoded bytes/chars: `2857` / `2561`
  - first diff index: `511`
- line `14` reason `mismatch`
  - raw bytes/chars: `2934` / `2612`
  - decoded bytes/chars: `2936` / `2614`
  - first diff index: `1669`
- line `15` reason `mismatch`
  - raw bytes/chars: `1154` / `1027`
  - decoded bytes/chars: `1158` / `1031`
  - first diff index: `152`
- line `16` reason `mismatch`
  - raw bytes/chars: `2763` / `2595`
  - decoded bytes/chars: `2765` / `2597`
  - first diff index: `1919`

## Private Samples

Private failure samples: `artifacts/private/v2_0_route_sp_passthrough_all_routes_isolated_roundtrip_test_failures.jsonl`
