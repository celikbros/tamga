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
| sp_unigram_64000_train_only | 1998 | 1989 | 9 | 0 | 0.995495 | 0.158902 | 2781995 | 2782021 |

## Failure Samples

### sp_unigram_64000_train_only

- line `94` reason `mismatch`
  - raw bytes/chars: `761` / `701`
  - decoded bytes/chars: `764` / `703`
  - first diff index: `8`
- line `431` reason `mismatch`
  - raw bytes/chars: `1750` / `1544`
  - decoded bytes/chars: `1704` / `1549`
  - first diff index: `223`
- line `512` reason `mismatch`
  - raw bytes/chars: `758` / `626`
  - decoded bytes/chars: `794` / `650`
  - first diff index: `0`
- line `555` reason `mismatch`
  - raw bytes/chars: `1210` / `1094`
  - decoded bytes/chars: `1213` / `1096`
  - first diff index: `28`
- line `755` reason `mismatch`
  - raw bytes/chars: `1199` / `1082`
  - decoded bytes/chars: `1202` / `1084`
  - first diff index: `364`
- line `1175` reason `mismatch`
  - raw bytes/chars: `1187` / `1086`
  - decoded bytes/chars: `1190` / `1088`
  - first diff index: `1004`
- line `1502` reason `mismatch`
  - raw bytes/chars: `1000` / `918`
  - decoded bytes/chars: `1003` / `920`
  - first diff index: `607`
- line `1930` reason `mismatch`
  - raw bytes/chars: `3942` / `3721`
  - decoded bytes/chars: `3960` / `3733`
  - first diff index: `641`
- line `1931` reason `mismatch`
  - raw bytes/chars: `800` / `731`
  - decoded bytes/chars: `803` / `733`
  - first diff index: `54`

## Private Samples

Private failure samples: `artifacts/private/v2_0_sp64_roundtrip_test_failures.jsonl`
