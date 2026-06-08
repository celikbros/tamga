# v2.0 Train-Only Marker Frontier Confidence Intervals

Dataset: `data/eval/tr_challenge.tsv`
Bootstrap samples: `1000`

Intervals are non-parametric bootstrap 95% intervals over examples.

| Model | Examples | Boundary F1 95% CI | Avg model tokens/word 95% CI |
| --- | ---: | ---: | ---: |
| sp_unigram_64000_train_only | 108 | 0.7351 [0.7036, 0.7648] | 2.2010 [2.0960, 2.3112] |
| finite_protected_sp64 | 108 | 0.6913 [0.6537, 0.7280] | 2.4073 [2.2730, 2.5722] |
| all_soft_marker_stripped | 108 | 0.7703 [0.7326, 0.8046] | 2.7180 [2.5651, 2.8686] |
| suffix_chain2_marker_stripped | 108 | 0.7632 [0.7273, 0.7962] | 2.6136 [2.4687, 2.7755] |
| high_value_suffix_marker_stripped | 108 | 0.7665 [0.7306, 0.7977] | 2.5144 [2.3819, 2.6494] |

## Interpretation

Use this report to avoid over-reading tiny F1 differences among
train-only marker policies. If intervals overlap heavily, prefer the
lower-token-pressure candidate until downstream/BPB calibration says
otherwise.
