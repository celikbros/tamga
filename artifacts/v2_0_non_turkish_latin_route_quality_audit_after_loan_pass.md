# v2.0 Non-Turkish Latin Route Quality Audit

Split dir: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split`
Splits: `train, valid, test`
Private examples: `artifacts/private/v2_0_non_turkish_latin_route_quality_examples_after_loan_pass.jsonl`

This audit checks whether the `non_turkish_latin_word` protected route
is mostly true foreign Latin text or legacy-encoding-corrupted Turkish.

## Summary

| Lines | Route occurrences | Route bytes | Unique surfaces |
| ---: | ---: | ---: | ---: |
| 19992 | 1644 | 17522 | 1122 |

## Classification

| Class | Occurrences | Occurrence share | Bytes | Unique surfaces |
| --- | ---: | ---: | ---: | ---: |
| `other_non_turkish_latin` | 953 | 0.579684 | 9016 | 669 |
| `legacy_turkish_encoding_artifact` | 691 | 0.420316 | 8506 | 453 |

## Legacy Character Counts

| Character | Meaning | Count |
| --- | --- | ---: |
| `ý` | `legacy_dotless_i` | 644 |
| `Ý` | `legacy_capital_dotted_i` | 5 |
| `þ` | `legacy_s_cedilla` | 264 |
| `Þ` | `legacy_capital_s_cedilla` | 0 |
| `ð` | `legacy_g_breve` | 213 |
| `Ð` | `legacy_capital_g_breve` | 0 |

## Interpretation Gate

If legacy Turkish artifacts dominate this route, optimize data cleaning
or route handling before changing the morphology learner.
