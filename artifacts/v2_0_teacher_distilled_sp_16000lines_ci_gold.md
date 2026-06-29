# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_gold_expanded.tsv`
Bootstrap samples: `1000`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `sp64_bare` | 50 | 0.7551 [0.7071, 0.8024] | 2.5041 [2.2500, 2.8505] | 0.0200 [0.0000, 0.0600] |
| `sp64_finite` | 50 | 0.7314 [0.6679, 0.7886] | 2.5868 [2.3022, 2.9403] | 0.0200 [0.0000, 0.0600] |
| `teacher_distilled_16k_bare` | 50 | 0.8042 [0.7557, 0.8487] | 2.7686 [2.4444, 3.1546] | 0.0200 [0.0000, 0.0600] |
| `teacher_distilled_16k_finite` | 50 | 0.8129 [0.7728, 0.8525] | 2.8430 [2.4839, 3.2633] | 0.0200 [0.0000, 0.0600] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
