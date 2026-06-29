# v2.0 Score-Shifted SentencePiece Model

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_score_shifted_sp/score_shift_mass_lambda4_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_score_shifted_sp/score_shift_mass_lambda4_unigram_64000.vocab`

This is a train-only post-hoc Unigram score-shift probe. It does not
change the vocabulary or add runtime boundary markers. It lowers scores
for pieces that frequently cross custom-teacher soft morphology
boundaries in the train split.

## Parameters

| Parameter | Value |
| --- | ---: |
| penalty_lambda | 4.000000 |
| penalty_mode | mass |
| min_count | 20 |
| min_crossing_count | 20 |
| min_crossing_rate | 0.000000 |
| min_surface_len | 2 |
| max_penalty | 8.000000 |

## Summary

| Metric | Value |
| --- | ---: |
| scanned lines | 0 |
| observed pieces | 60119 |
| pieces with crossing evidence | 19322 |
| adjusted pieces | 4592 |
| alignment failures | 0 |

## Top Adjusted Pieces

| Piece | Count | Crossing count | Crossing rate | Score delta |
| --- | ---: | ---: | ---: | ---: |
| `▁kullanılmıştır` | 2835 | 2835 | 1.000000 | -2.119626 |
| `▁yapılmıştır` | 1860 | 1860 | 1.000000 | -1.390654 |
| `▁olmuştur` | 1536 | 1536 | 1.000000 | -1.148411 |
| `▁görülmüştür` | 1405 | 1405 | 1.000000 | -1.050467 |
| `mektedir` | 1197 | 1197 | 1.000000 | -0.894954 |
| `▁oluşturmaktadır` | 1188 | 1188 | 1.000000 | -0.888225 |
| `▁etmektedir` | 1088 | 1088 | 1.000000 | -0.813457 |
| `▁alınmıştır` | 1067 | 1067 | 1.000000 | -0.797757 |
| `▁görülmektedir` | 1056 | 1056 | 1.000000 | -0.789533 |
| `mıştır` | 988 | 988 | 1.000000 | -0.738691 |
| `maktadır` | 850 | 850 | 1.000000 | -0.635514 |
| `▁bulunmaktadır` | 766 | 766 | 1.000000 | -0.572710 |
| `▁sahiptir` | 754 | 754 | 1.000000 | -0.563738 |
| `▁ulaşılmıştır` | 747 | 747 | 1.000000 | -0.558505 |
| `▁uygulanmıştır` | 709 | 709 | 1.000000 | -0.530093 |
| `▁önemlidir` | 659 | 659 | 1.000000 | -0.492710 |
| `▁almaktadır` | 625 | 625 | 1.000000 | -0.467290 |
| `▁amaçlamaktadır` | 606 | 606 | 1.000000 | -0.453084 |
| `▁verilmiştir` | 597 | 597 | 1.000000 | -0.446355 |
| `▁toplanmıştır` | 586 | 586 | 1.000000 | -0.438130 |
| `▁olmaktadır` | 540 | 540 | 1.000000 | -0.403738 |
| `▁etmiştir` | 525 | 525 | 1.000000 | -0.392524 |
| `▁yürütülmüştür` | 519 | 519 | 1.000000 | -0.388038 |
| `▁gerekmektedir` | 496 | 496 | 1.000000 | -0.370841 |
| `▁oluşmaktadır` | 485 | 485 | 1.000000 | -0.362617 |
| `▁biridir` | 473 | 473 | 1.000000 | -0.353645 |
| `▁çıkmaktadır` | 438 | 438 | 1.000000 | -0.327477 |
| `▁değildir` | 419 | 419 | 1.000000 | -0.313271 |
| `lardır` | 402 | 402 | 1.000000 | -0.300561 |
| `▁taşımaktadır` | 399 | 399 | 1.000000 | -0.298318 |
| `▁almıştır` | 389 | 389 | 1.000000 | -0.290841 |
| `kullanılmaktadır` | 386 | 386 | 1.000000 | -0.288598 |
| `▁gelmektedir` | 377 | 377 | 1.000000 | -0.281869 |
| `▁başlamıştır` | 374 | 374 | 1.000000 | -0.279626 |
| `▁sunulmuştur` | 355 | 355 | 1.000000 | -0.265421 |
| `▁oluşturmuştur` | 349 | 349 | 1.000000 | -0.260935 |
| `▁koymaktadır` | 330 | 330 | 1.000000 | -0.246729 |
| `▁oluşturulmuştur` | 319 | 319 | 1.000000 | -0.238504 |
| `▁varılmıştır` | 314 | 314 | 1.000000 | -0.234766 |
| `▁mümkündür` | 306 | 306 | 1.000000 | -0.228786 |

## Next

Evaluate this model with the finite protected wrapper. Continue only if
it improves normal-text morphology F1 without materially increasing
tokens/raw byte or breaking roundtrip/protected invariants.
