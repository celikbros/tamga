# v2.0 Boundary-Weighted Unigram EM Prototype

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_boundary_weighted_unigram_em/lambda16_iter1_100lines_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_boundary_weighted_unigram_em/lambda16_iter1_100lines_unigram_64000.vocab`
Boundary lambda: `16.0`
Iterations: `1`
Max lines: `100`

This is a small prototype, not a production trainer. It updates existing
SP64 Unigram scores using expected counts from a boundary-weighted
lattice over normal-text segments.

## Iterations

| Iteration | Lines | Segments | Skipped segments | Expected piece types | Expected mass | Expected crossings | Avg expected crossings/segment | Changed scores | Avg log Z/segment |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 100 | 25486 | 0 | 15479 | 37019.1245 | 484.1948 | 0.018998 | 15479 | -12.289839 |

## Gate

Evaluate this model as a diagnostic. Continue only if lambda curves
produce a material bare-F1 gain outside the current visible-eval noise
floor without unacceptable token pressure.
