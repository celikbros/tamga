# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `1000`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `em_l0_2000_bare` | 108 | 0.7383 [0.7063, 0.7676] | 2.2402 [2.1297, 2.3498] | 0.0000 [0.0000, 0.0000] |
| `em_l0_2000_finite` | 108 | 0.6767 [0.6375, 0.7141] | 2.3368 [2.1964, 2.4974] | 0.0000 [0.0000, 0.0000] |
| `em_l1_2000_bare` | 108 | 0.7396 [0.7080, 0.7699] | 2.2402 [2.1285, 2.3529] | 0.0000 [0.0000, 0.0000] |
| `em_l1_2000_finite` | 108 | 0.6780 [0.6407, 0.7169] | 2.3368 [2.2010, 2.4776] | 0.0000 [0.0000, 0.0000] |
| `em_l2_2000_bare` | 108 | 0.7396 [0.7061, 0.7707] | 2.2402 [2.1343, 2.3536] | 0.0000 [0.0000, 0.0000] |
| `em_l2_2000_finite` | 108 | 0.6780 [0.6376, 0.7131] | 2.3368 [2.1927, 2.4790] | 0.0000 [0.0000, 0.0000] |
| `em_l4_2000_bare` | 108 | 0.7391 [0.7057, 0.7684] | 2.2428 [2.1421, 2.3659] | 0.0000 [0.0000, 0.0000] |
| `em_l4_2000_finite` | 108 | 0.6802 [0.6395, 0.7180] | 2.3394 [2.1963, 2.4934] | 0.0000 [0.0000, 0.0000] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
