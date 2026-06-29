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
| boundary_biased_lambda0_numeric_sp | 20 | 0 | 20 | 0 | 0.000000 | 0.154277 | 57669 | 57942 |
| boundary_biased_lambda4_numeric_sp | 20 | 0 | 20 | 0 | 0.000000 | 0.155196 | 57669 | 57941 |

## Failure Samples

### boundary_biased_lambda0_numeric_sp

- line `1` reason `mismatch`
  - raw bytes/chars: `2639` / `2396`
  - decoded bytes/chars: `2655` / `2412`
  - first diff index: `39`
- line `2` reason `mismatch`
  - raw bytes/chars: `1870` / `1702`
  - decoded bytes/chars: `1878` / `1710`
  - first diff index: `122`
- line `3` reason `mismatch`
  - raw bytes/chars: `2963` / `2714`
  - decoded bytes/chars: `2996` / `2747`
  - first diff index: `18`
- line `4` reason `mismatch`
  - raw bytes/chars: `3015` / `2743`
  - decoded bytes/chars: `3024` / `2752`
  - first diff index: `19`
- line `5` reason `mismatch`
  - raw bytes/chars: `3068` / `2800`
  - decoded bytes/chars: `3080` / `2812`
  - first diff index: `69`
- line `6` reason `mismatch`
  - raw bytes/chars: `3932` / `3598`
  - decoded bytes/chars: `3914` / `3580`
  - first diff index: `5`
- line `7` reason `mismatch`
  - raw bytes/chars: `2811` / `2590`
  - decoded bytes/chars: `2815` / `2594`
  - first diff index: `70`
- line `8` reason `mismatch`
  - raw bytes/chars: `3075` / `2813`
  - decoded bytes/chars: `3097` / `2835`
  - first diff index: `12`
- line `9` reason `mismatch`
  - raw bytes/chars: `1121` / `1025`
  - decoded bytes/chars: `1133` / `1037`
  - first diff index: `55`
- line `10` reason `mismatch`
  - raw bytes/chars: `2438` / `2232`
  - decoded bytes/chars: `2460` / `2254`
  - first diff index: `10`

### boundary_biased_lambda4_numeric_sp

- line `1` reason `mismatch`
  - raw bytes/chars: `2639` / `2396`
  - decoded bytes/chars: `2655` / `2412`
  - first diff index: `39`
- line `2` reason `mismatch`
  - raw bytes/chars: `1870` / `1702`
  - decoded bytes/chars: `1878` / `1710`
  - first diff index: `122`
- line `3` reason `mismatch`
  - raw bytes/chars: `2963` / `2714`
  - decoded bytes/chars: `2996` / `2747`
  - first diff index: `18`
- line `4` reason `mismatch`
  - raw bytes/chars: `3015` / `2743`
  - decoded bytes/chars: `3024` / `2752`
  - first diff index: `19`
- line `5` reason `mismatch`
  - raw bytes/chars: `3068` / `2800`
  - decoded bytes/chars: `3080` / `2812`
  - first diff index: `69`
- line `6` reason `mismatch`
  - raw bytes/chars: `3932` / `3598`
  - decoded bytes/chars: `3914` / `3580`
  - first diff index: `5`
- line `7` reason `mismatch`
  - raw bytes/chars: `2811` / `2590`
  - decoded bytes/chars: `2815` / `2594`
  - first diff index: `70`
- line `8` reason `mismatch`
  - raw bytes/chars: `3075` / `2813`
  - decoded bytes/chars: `3097` / `2835`
  - first diff index: `12`
- line `9` reason `mismatch`
  - raw bytes/chars: `1121` / `1025`
  - decoded bytes/chars: `1133` / `1037`
  - first diff index: `55`
- line `10` reason `mismatch`
  - raw bytes/chars: `2438` / `2232`
  - decoded bytes/chars: `2460` / `2254`
  - first diff index: `10`

## Private Samples

Private failure samples: `artifacts/private/v2_0_boundary_encoder_roundtrip_audit_smoke_failures.jsonl`
