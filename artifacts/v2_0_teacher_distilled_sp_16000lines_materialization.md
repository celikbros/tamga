# v2.0 Teacher-Distilled SP Score Probe

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Source vocab: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_16000lines_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_teacher_distilled_sp/teacher_distilled_16000lines_unigram_64000.vocab`
Max lines: `16000`

This probe fits global Unigram scores to teacher-compliant no-cross
paths over the fixed SP64 vocabulary. It is a score-space upper-bound
diagnostic, not a production trainer.

## Summary

| Metric | Value |
| --- | ---: |
| lines | 16000 |
| segments | 2854463 |
| skipped segments | 0 |
| counted tokens | 4313410 |
| counted piece types | 53493 |
| missing piece tokens | 0 |
| changed scores | 63997 |
| score floor | -30.0000 |

## Top Counted Pieces

| Piece | Count |
| --- | ---: |
| `.` | 145456 |
| `,` | 132656 |
| `▁ve` | 95101 |
| `da` | 83133 |
| `de` | 75651 |
| `ler` | 47968 |
| `s` | 43707 |
| `n` | 43143 |
| `lar` | 41001 |
| `▁bir` | 36960 |
| `ın` | 30409 |
| `mış` | 29406 |
| `ki` | 28861 |
| `te` | 28295 |
| `miş` | 27304 |
| `ta` | 27116 |
| `ni` | 26497 |
| `in` | 25954 |
| `tır` | 25749 |
| `k` | 25596 |
| `tir` | 24403 |
| `dan` | 24041 |
| `▁Bu` | 23669 |
| `l` | 22776 |
| `lik` | 22211 |
| `▁ile` | 21861 |
| `ti` | 21761 |
| `-` | 21478 |
| `)` | 21341 |
| `▁(` | 21263 |
| `dir` | 21238 |
| `nı` | 20961 |
| `den` | 20814 |
| `▁olarak` | 20230 |
| `dır` | 19805 |
| `a` | 17287 |
| `▁bu` | 15756 |
| `m` | 15737 |
| `im` | 15670 |
| `"` | 15449 |

## Reading

If this model still behaves like SP64 on deployed Viterbi, then global
score space is exhausted for this vocabulary. If it jumps toward the
oracle ceiling, the previous EM/score-shift probes were underpowered.
