# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `1000`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `sp64_bare` | 108 | 0.7351 [0.7047, 0.7633] | 2.2010 [2.0934, 2.3137] | 0.0000 [0.0000, 0.0000] |
| `sp64_finite` | 108 | 0.6755 [0.6366, 0.7156] | 2.2977 [2.1586, 2.4491] | 0.0000 [0.0000, 0.0000] |
| `partial_rho025_bare` | 108 | 0.7380 [0.7094, 0.7676] | 2.1854 [2.0775, 2.2959] | 0.0000 [0.0000, 0.0000] |
| `partial_rho025_finite` | 108 | 0.6782 [0.6391, 0.7190] | 2.2820 [2.1491, 2.4235] | 0.0000 [0.0000, 0.0000] |
| `score_shift_mass_l8_bare` | 108 | 0.7364 [0.7045, 0.7658] | 2.2010 [2.0977, 2.3134] | 0.0000 [0.0000, 0.0000] |
| `score_shift_mass_l8_finite` | 108 | 0.6768 [0.6356, 0.7152] | 2.2977 [2.1575, 2.4445] | 0.0000 [0.0000, 0.0000] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
