# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `200`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `em_lambda0_100_bare` | 108 | 0.7392 [0.7067, 0.7664] | 2.3133 [2.1765, 2.4581] | 0.0000 [0.0000, 0.0000] |
| `em_lambda0_100_finite` | 108 | 0.6796 [0.6428, 0.7176] | 2.3995 [2.2574, 2.5547] | 0.0000 [0.0000, 0.0000] |
| `em_lambda1_100_bare` | 108 | 0.7404 [0.7104, 0.7749] | 2.3133 [2.1912, 2.4290] | 0.0000 [0.0000, 0.0000] |
| `em_lambda1_100_finite` | 108 | 0.6809 [0.6378, 0.7220] | 2.3995 [2.2493, 2.5534] | 0.0000 [0.0000, 0.0000] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
