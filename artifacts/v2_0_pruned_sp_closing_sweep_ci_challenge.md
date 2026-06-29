# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `1000`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `sp64_bare` | 108 | 0.7351 [0.7047, 0.7633] | 2.2010 [2.0934, 2.3137] | 0.0000 [0.0000, 0.0000] |
| `sp64_finite` | 108 | 0.6755 [0.6366, 0.7156] | 2.2977 [2.1586, 2.4491] | 0.0000 [0.0000, 0.0000] |
| `pruned_ge070_nonword_bare` | 108 | 0.7486 [0.7189, 0.7777] | 2.2611 [2.1396, 2.3844] | 0.0000 [0.0000, 0.0000] |
| `pruned_ge070_nonword_finite` | 108 | 0.6875 [0.6486, 0.7299] | 2.3577 [2.2149, 2.5054] | 0.0000 [0.0000, 0.0000] |
| `pruned_rate100_bare` | 108 | 0.7351 [0.7019, 0.7648] | 2.2010 [2.0977, 2.3134] | 0.0000 [0.0000, 0.0000] |
| `pruned_rate100_finite` | 108 | 0.6755 [0.6335, 0.7148] | 2.2977 [2.1575, 2.4445] | 0.0000 [0.0000, 0.0000] |
| `pruned_rate090_bare` | 108 | 0.7482 [0.7171, 0.7767] | 2.2559 [2.1458, 2.3947] | 0.0000 [0.0000, 0.0000] |
| `pruned_rate090_finite` | 108 | 0.6871 [0.6447, 0.7276] | 2.3525 [2.2148, 2.5132] | 0.0000 [0.0000, 0.0000] |
| `pruned_rate070_count50_bare` | 108 | 0.7497 [0.7230, 0.7783] | 2.2480 [2.1385, 2.3695] | 0.0000 [0.0000, 0.0000] |
| `pruned_rate070_count50_finite` | 108 | 0.6897 [0.6485, 0.7285] | 2.3446 [2.1994, 2.4987] | 0.0000 [0.0000, 0.0000] |
| `teacher_distilled_16k_bare` | 108 | 0.7509 [0.7222, 0.7797] | 2.3525 [2.2242, 2.4880] | 0.0000 [0.0000, 0.0000] |
| `teacher_distilled_16k_finite` | 108 | 0.7219 [0.6852, 0.7542] | 2.4413 [2.2813, 2.6001] | 0.0000 [0.0000, 0.0000] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
