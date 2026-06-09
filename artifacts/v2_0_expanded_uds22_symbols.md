# v2.0 Expanded UDS Symbol Selection

Candidate TSV: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv`
Symbols output: `artifacts/private/v2_0_morph_seed_vocab/expanded_uds22_symbols.train.txt`

This is a controlled expansion of the 7-symbol safe UDS pool. It uses
only train-side morphology candidate statistics and does not inspect
visible challenge rows.

## Parameters

| Parameter | Value |
| --- | ---: |
| recommendation | `uds_or_seed_candidate` |
| min_count | 100 |
| min_surface_len | 3 |
| max_hard_share | 0.010000 |
| max_collision_rate | 0.001000 |
| max_symbols | 64 |

## Summary

| Metric | Value |
| --- | ---: |
| input candidates | 244 |
| selected symbols | 22 |
| selected occurrences | 208112 |
| max selected hard share | 0.009723 |
| max selected exact collision rate | 0.000983 |

## Symbols

| Token | Surface | Count | Surface len | Hard share | Exact collision rate |
| --- | --- | ---: | ---: | ---: | ---: |
| `+ler` | `ler` | 47826 | 3 | 0.009723 | 0.000815 |
| `+mış` | `mış` | 28812 | 3 | 0.000000 | 0.000416 |
| `+miş` | `miş` | 26859 | 3 | 0.000000 | 0.000447 |
| `+tır` | `tır` | 24886 | 3 | 0.000643 | 0.000362 |
| `+tir` | `tir` | 23709 | 3 | 0.001097 | 0.000928 |
| `+sın` | `sın` | 19333 | 3 | 0.006983 | 0.000983 |
| `+lık` | `lık` | 14033 | 3 | 0.002494 | 0.000570 |
| `+eme` | `eme` | 8135 | 3 | 0.000000 | 0.000492 |
| `+ecek` | `ecek` | 3522 | 4 | 0.000000 | 0.000000 |
| `+müş` | `müş` | 3258 | 3 | 0.000000 | 0.000921 |
| `+acak` | `acak` | 3038 | 4 | 0.000000 | 0.000000 |
| `+ümüz` | `ümüz` | 1609 | 4 | 0.000000 | 0.000000 |
| `+ımız` | `ımız` | 703 | 4 | 0.000000 | 0.000000 |
| `+imiz` | `imiz` | 624 | 4 | 0.000000 | 0.000000 |
| `+LIK` | `LIK` | 383 | 3 | 0.000000 | 0.000000 |
| `+yecek` | `yecek` | 289 | 5 | 0.000000 | 0.000000 |
| `+SIN` | `SIN` | 273 | 3 | 0.007326 | 0.000000 |
| `+EME` | `EME` | 183 | 3 | 0.000000 | 0.000000 |
| `+LAŞ` | `LAŞ` | 181 | 3 | 0.000000 | 0.000000 |
| `+sün` | `sün` | 178 | 3 | 0.005618 | 0.000000 |
| `+umuz` | `umuz` | 169 | 4 | 0.005917 | 0.000000 |
| `+MİŞ` | `MİŞ` | 109 | 3 | 0.000000 | 0.000000 |

## Gate

This branch should continue only if it improves over the 7-symbol
safe UDS result without materially increasing token pressure.
If it merely shifts token pressure or visible F1 by noise, stop
UDS expansion and move to constrained/MorphBPE design.
