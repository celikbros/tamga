# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `1000`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `sp64_bare` | 108 | 0.7351 [0.7047, 0.7633] | 2.2010 [2.0934, 2.3137] | 0.0000 [0.0000, 0.0000] |
| `sp64_finite` | 108 | 0.6755 [0.6366, 0.7156] | 2.2977 [2.1586, 2.4491] | 0.0000 [0.0000, 0.0000] |
| `pruned_ge070_all_bare` | 108 | 0.7447 [0.7171, 0.7730] | 2.3525 [2.2321, 2.4737] | 0.0000 [0.0000, 0.0000] |
| `pruned_ge070_all_finite` | 108 | 0.6582 [0.6178, 0.7007] | 2.4491 [2.3059, 2.5942] | 0.0000 [0.0000, 0.0000] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
