# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `200`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `em_l0_100_bare` | 108 | 0.7392 [0.7067, 0.7664] | 2.3133 [2.1765, 2.4581] | 0.0000 [0.0000, 0.0000] |
| `em_l0_100_finite` | 108 | 0.6796 [0.6428, 0.7176] | 2.3995 [2.2574, 2.5547] | 0.0000 [0.0000, 0.0000] |
| `em_l4_100_bare` | 108 | 0.7308 [0.7006, 0.7663] | 2.3107 [2.1847, 2.4235] | 0.0000 [0.0000, 0.0000] |
| `em_l4_100_finite` | 108 | 0.6774 [0.6387, 0.7166] | 2.3890 [2.2441, 2.5343] | 0.0000 [0.0000, 0.0000] |
| `em_l16_100_bare` | 108 | 0.7410 [0.7147, 0.7642] | 2.4230 [2.2990, 2.5485] | 0.0000 [0.0000, 0.0000] |
| `em_l16_100_finite` | 108 | 0.6906 [0.6609, 0.7260] | 2.5013 [2.3253, 2.6380] | 0.0000 [0.0000, 0.0000] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
