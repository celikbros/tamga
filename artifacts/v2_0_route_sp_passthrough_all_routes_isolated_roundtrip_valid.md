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
| finite_protected_sp64_all_sp_routes_isolated | 1994 | 484 | 1510 | 0 | 0.242728 | 0.164581 | 2843294 | 2862289 |

## Failure Samples

### finite_protected_sp64_all_sp_routes_isolated

- line `1` reason `mismatch`
  - raw bytes/chars: `2639` / `2396`
  - decoded bytes/chars: `2651` / `2408`
  - first diff index: `85`
- line `2` reason `mismatch`
  - raw bytes/chars: `1870` / `1702`
  - decoded bytes/chars: `1878` / `1710`
  - first diff index: `7`
- line `3` reason `mismatch`
  - raw bytes/chars: `2963` / `2714`
  - decoded bytes/chars: `2967` / `2718`
  - first diff index: `52`
- line `4` reason `mismatch`
  - raw bytes/chars: `3015` / `2743`
  - decoded bytes/chars: `3025` / `2753`
  - first diff index: `83`
- line `5` reason `mismatch`
  - raw bytes/chars: `3068` / `2800`
  - decoded bytes/chars: `3072` / `2804`
  - first diff index: `733`
- line `8` reason `mismatch`
  - raw bytes/chars: `3075` / `2813`
  - decoded bytes/chars: `3077` / `2815`
  - first diff index: `2193`
- line `10` reason `mismatch`
  - raw bytes/chars: `2438` / `2232`
  - decoded bytes/chars: `2452` / `2246`
  - first diff index: `26`
- line `11` reason `mismatch`
  - raw bytes/chars: `3696` / `3378`
  - decoded bytes/chars: `3704` / `3386`
  - first diff index: `542`
- line `12` reason `mismatch`
  - raw bytes/chars: `2058` / `1906`
  - decoded bytes/chars: `2064` / `1912`
  - first diff index: `366`
- line `14` reason `mismatch`
  - raw bytes/chars: `2735` / `2516`
  - decoded bytes/chars: `2739` / `2520`
  - first diff index: `98`

## Private Samples

Private failure samples: `artifacts/private/v2_0_route_sp_passthrough_all_routes_isolated_roundtrip_valid_failures.jsonl`
