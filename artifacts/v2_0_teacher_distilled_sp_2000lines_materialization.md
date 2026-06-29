# v2.0 Teacher-Distilled SP Score Probe

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Source vocab: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_2000lines_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_2000lines_unigram_64000.vocab`
Max lines: `2000`

This probe fits global Unigram scores to teacher-compliant no-cross
paths over the fixed SP64 vocabulary. It is a score-space upper-bound
diagnostic, not a production trainer.

## Summary

| Metric | Value |
| --- | ---: |
| lines | 2000 |
| segments | 343822 |
| skipped segments | 0 |
| counted tokens | 521014 |
| counted piece types | 27754 |
| missing piece tokens | 0 |
| changed scores | 63997 |
| score floor | -30.0000 |

## Top Counted Pieces

| Piece | Count |
| --- | ---: |
| `.` | 17100 |
| `,` | 15843 |
| `▁ve` | 11302 |
| `da` | 10047 |
| `de` | 9382 |
| `n` | 5787 |
| `▁bir` | 5668 |
| `s` | 5235 |
| `ler` | 5231 |
| `lar` | 4841 |
| `te` | 3985 |
| `ki` | 3958 |
| `ın` | 3955 |
| `ta` | 3641 |
| `ni` | 3534 |
| `dan` | 3368 |
| `k` | 3199 |
| `dir` | 3002 |
| `dır` | 2998 |
| `in` | 2983 |
| `lik` | 2961 |
| `▁Bu` | 2939 |
| `nı` | 2883 |
| `mış` | 2748 |
| `ti` | 2740 |
| `miş` | 2677 |
| `▁olarak` | 2664 |
| `den` | 2629 |
| `tır` | 2597 |
| `tir` | 2575 |
| `l` | 2490 |
| `▁bu` | 2478 |
| `▁ile` | 2419 |
| `"` | 2400 |
| `-` | 2195 |
| `m` | 2144 |
| `a` | 2134 |
| `im` | 1894 |
| `nu` | 1848 |
| `e` | 1710 |

## Reading

If this model still behaves like SP64 on deployed Viterbi, then global
score space is exhausted for this vocabulary. If it jumps toward the
oracle ceiling, the previous EM/score-shift probes were underpowered.
