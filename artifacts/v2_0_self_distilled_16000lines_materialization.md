# v2.0 Self-Distilled SP Score Control

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_self_distilled_sp/self_distilled_16000lines_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_self_distilled_sp/self_distilled_16000lines_unigram_64000.vocab`
Max lines: `16000`

This is the non-morphology matched control for the teacher-distilled
score bound. It keeps the fixed SP64 vocabulary and re-estimates global
Unigram scores from official SentencePiece segmentations on the same
train-line budget. It does not use morphology teacher boundaries.

## Summary

| Metric | Value |
| --- | ---: |
| lines | 16000 |
| segments | 2854463 |
| counted tokens | 3509481 |
| counted piece types | 60120 |
| changed scores | 63997 |
| score floor | -30.0000 |

## Top Counted Pieces

| Piece | Count |
| --- | ---: |
| `▁` | 200380 |
| `▁.` | 145456 |
| `,` | 132656 |
| `▁ve` | 94281 |
| `▁bir` | 33341 |
| `▁Bu` | 22897 |
| `▁-` | 21478 |
| `)` | 21341 |
| `▁(` | 21263 |
| `▁ile` | 20865 |
| `▁olarak` | 20232 |
| `▁"` | 15449 |
| `▁bu` | 15402 |
| `n` | 12731 |
| `▁için` | 11367 |
| `:` | 10982 |
| `▁de` | 10436 |
| `▁olan` | 10309 |
| `nin` | 10241 |
| `e` | 9159 |
| `▁da` | 8897 |
| `;` | 8187 |
| `▁the` | 7879 |
| `▁olduğu` | 7633 |
| `nın` | 7397 |
| `a` | 7386 |
| `▁göre` | 6771 |
| `▁%` | 6761 |
| `▁of` | 6694 |
| `▁daha` | 6553 |
| `▁önemli` | 6337 |
| `▁en` | 6236 |
| `▁ise` | 5969 |
| `k` | 5895 |
| `i` | 5869 |
| `▁Türkiye` | 5848 |
| `▁ortaya` | 5527 |
| `▁arasında` | 5489 |
| `▁and` | 5222 |
| `▁gibi` | 5175 |

## Reading

Compare this control against `teacher_distilled_16000`. If both improve
BPB similarly versus the protected SP64 floor, the earlier gain is
mostly score re-estimation / effective-vocabulary geometry. If the
teacher-distilled model wins clearly over this control, the morphology
teacher is carrying additional signal.
