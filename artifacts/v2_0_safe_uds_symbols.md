# v2.0 Safe UDS Symbol Selection

Policy TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_policy.train.tsv`
Symbols output: `artifacts/private/v2_0_morph_seed_vocab/safe_uds_symbols.train.txt`
Action: `safe_uds_candidate_later`

This is a small auditable user-defined-symbol pool. It is derived
only from train-policy statistics and does not use visible challenge
rows.

## Summary

| Metric | Value |
| --- | ---: |
| selected symbols | 7 |
| selected occurrences | 9954 |
| max hard share | 0.005917 |
| max exact collision rate | 0.000000 |

## Symbols

| Token | Surface | Count | Hard share | Exact collision rate | Reason |
| --- | --- | ---: | ---: | ---: | --- |
| `+ecek` | `ecek` | 3522 | 0.000000 | 0.000000 | long_low_collision_low_hard_share |
| `+acak` | `acak` | 3038 | 0.000000 | 0.000000 | long_low_collision_low_hard_share |
| `+ümüz` | `ümüz` | 1609 | 0.000000 | 0.000000 | long_low_collision_low_hard_share |
| `+ımız` | `ımız` | 703 | 0.000000 | 0.000000 | long_low_collision_low_hard_share |
| `+imiz` | `imiz` | 624 | 0.000000 | 0.000000 | long_low_collision_low_hard_share |
| `+yecek` | `yecek` | 289 | 0.000000 | 0.000000 | long_low_collision_low_hard_share |
| `+umuz` | `umuz` | 169 | 0.005917 | 0.000000 | long_low_collision_low_hard_share |

## Gate

This UDS probe should only continue if token pressure stays near the
finite-protected SP64 floor and visible boundary behavior improves.
If it does not improve morphology F1, stop this cheap UDS branch.
