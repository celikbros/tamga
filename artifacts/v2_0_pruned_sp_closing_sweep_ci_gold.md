# v2.0 SP Model Bootstrap CI

Dataset: `data/eval/tr_gold_expanded.tsv`
Bootstrap samples: `1000`
Numeric protected SP passthrough: `True`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI | Exact match rate 95% CI |
| --- | ---: | ---: | ---: | ---: |
| `sp64_bare` | 50 | 0.7551 [0.7071, 0.8024] | 2.5041 [2.2500, 2.8505] | 0.0200 [0.0000, 0.0600] |
| `sp64_finite` | 50 | 0.7314 [0.6679, 0.7886] | 2.5868 [2.3022, 2.9403] | 0.0200 [0.0000, 0.0600] |
| `pruned_ge070_nonword_bare` | 50 | 0.7684 [0.7187, 0.8155] | 2.5785 [2.3071, 2.9213] | 0.0200 [0.0000, 0.0600] |
| `pruned_ge070_nonword_finite` | 50 | 0.7453 [0.6898, 0.8053] | 2.6612 [2.3360, 3.0311] | 0.0200 [0.0000, 0.0600] |
| `pruned_rate100_bare` | 50 | 0.7551 [0.7127, 0.8039] | 2.5041 [2.2500, 2.8351] | 0.0200 [0.0000, 0.0600] |
| `pruned_rate100_finite` | 50 | 0.7314 [0.6775, 0.7876] | 2.5868 [2.2834, 2.9727] | 0.0200 [0.0000, 0.0600] |
| `pruned_rate090_bare` | 50 | 0.7721 [0.7225, 0.8169] | 2.5785 [2.3263, 2.9371] | 0.0200 [0.0000, 0.0600] |
| `pruned_rate090_finite` | 50 | 0.7491 [0.6902, 0.7993] | 2.6612 [2.3538, 3.0702] | 0.0200 [0.0000, 0.0600] |
| `pruned_rate070_count50_bare` | 50 | 0.7652 [0.7181, 0.8124] | 2.5537 [2.2867, 2.8948] | 0.0200 [0.0000, 0.0600] |
| `pruned_rate070_count50_finite` | 50 | 0.7420 [0.6847, 0.7969] | 2.6364 [2.3414, 3.0178] | 0.0200 [0.0000, 0.0800] |
| `teacher_distilled_16k_bare` | 50 | 0.8042 [0.7589, 0.8473] | 2.7686 [2.4656, 3.1712] | 0.0200 [0.0000, 0.0600] |
| `teacher_distilled_16k_finite` | 50 | 0.8129 [0.7743, 0.8502] | 2.8430 [2.4962, 3.2902] | 0.0200 [0.0000, 0.0600] |

## Reading

Use the interval width as the visible-eval noise floor. Do not treat
tiny point-estimate changes as real unless they clear this uncertainty.
