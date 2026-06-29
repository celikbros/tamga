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
| sp_unigram_64000_train_only | 1994 | 1985 | 9 | 0 | 0.995486 | 0.158319 | 2843294 | 2843331 |

## Failure Samples

### sp_unigram_64000_train_only

- line `507` reason `mismatch`
  - raw bytes/chars: `756` / `701`
  - decoded bytes/chars: `765` / `707`
  - first diff index: `585`
- line `552` reason `mismatch`
  - raw bytes/chars: `1007` / `890`
  - decoded bytes/chars: `1016` / `896`
  - first diff index: `36`
- line `969` reason `mismatch`
  - raw bytes/chars: `2187` / `1987`
  - decoded bytes/chars: `2190` / `1989`
  - first diff index: `59`
- line `1049` reason `mismatch`
  - raw bytes/chars: `1451` / `1334`
  - decoded bytes/chars: `1453` / `1336`
  - first diff index: `276`
- line `1055` reason `mismatch`
  - raw bytes/chars: `178` / `169`
  - decoded bytes/chars: `180` / `171`
  - first diff index: `123`
- line `1106` reason `mismatch`
  - raw bytes/chars: `1021` / `930`
  - decoded bytes/chars: `1024` / `932`
  - first diff index: `783`
- line `1344` reason `mismatch`
  - raw bytes/chars: `1857` / `1750`
  - decoded bytes/chars: `1860` / `1752`
  - first diff index: `658`
- line `1577` reason `mismatch`
  - raw bytes/chars: `990` / `898`
  - decoded bytes/chars: `993` / `900`
  - first diff index: `617`
- line `1578` reason `mismatch`
  - raw bytes/chars: `716` / `650`
  - decoded bytes/chars: `719` / `652`
  - first diff index: `130`

## Private Samples

Private failure samples: `artifacts/private/v2_0_sp64_roundtrip_valid_failures.jsonl`
