# v2.0 Score-Shifted SentencePiece Model

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_score_shifted_sp/score_shift_lambda05_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_score_shifted_sp/score_shift_lambda05_unigram_64000.vocab`

This is a train-only post-hoc Unigram score-shift probe. It does not
change the vocabulary or add runtime boundary markers. It lowers scores
for pieces that frequently cross custom-teacher soft morphology
boundaries in the train split.

## Parameters

| Parameter | Value |
| --- | ---: |
| penalty_lambda | 0.500000 |
| min_count | 20 |
| min_crossing_rate | 0.500000 |
| min_surface_len | 2 |
| max_penalty | 2.000000 |

## Summary

| Metric | Value |
| --- | ---: |
| scanned lines | 16000 |
| observed pieces | 60119 |
| pieces with crossing evidence | 19322 |
| adjusted pieces | 4878 |
| alignment failures | 0 |

## Top Adjusted Pieces

| Piece | Count | Crossing count | Crossing rate | Score delta |
| --- | ---: | ---: | ---: | ---: |
| `▁kullanılmıştır` | 2835 | 2835 | 1.000000 | -0.500000 |
| `▁yapılmıştır` | 1860 | 1860 | 1.000000 | -0.500000 |
| `▁olmuştur` | 1536 | 1536 | 1.000000 | -0.500000 |
| `▁görülmüştür` | 1405 | 1405 | 1.000000 | -0.500000 |
| `mektedir` | 1197 | 1197 | 1.000000 | -0.500000 |
| `▁oluşturmaktadır` | 1188 | 1188 | 1.000000 | -0.500000 |
| `▁etmektedir` | 1088 | 1088 | 1.000000 | -0.500000 |
| `▁alınmıştır` | 1067 | 1067 | 1.000000 | -0.500000 |
| `▁görülmektedir` | 1056 | 1056 | 1.000000 | -0.500000 |
| `mıştır` | 988 | 988 | 1.000000 | -0.500000 |
| `maktadır` | 850 | 850 | 1.000000 | -0.500000 |
| `▁bulunmaktadır` | 766 | 766 | 1.000000 | -0.500000 |
| `▁sahiptir` | 754 | 754 | 1.000000 | -0.500000 |
| `▁ulaşılmıştır` | 747 | 747 | 1.000000 | -0.500000 |
| `▁uygulanmıştır` | 709 | 709 | 1.000000 | -0.500000 |
| `▁önemlidir` | 659 | 659 | 1.000000 | -0.500000 |
| `▁almaktadır` | 625 | 625 | 1.000000 | -0.500000 |
| `▁amaçlamaktadır` | 606 | 606 | 1.000000 | -0.500000 |
| `▁verilmiştir` | 597 | 597 | 1.000000 | -0.500000 |
| `▁toplanmıştır` | 586 | 586 | 1.000000 | -0.500000 |
| `▁olmaktadır` | 540 | 540 | 1.000000 | -0.500000 |
| `▁etmiştir` | 525 | 525 | 1.000000 | -0.500000 |
| `▁yürütülmüştür` | 519 | 519 | 1.000000 | -0.500000 |
| `▁gerekmektedir` | 496 | 496 | 1.000000 | -0.500000 |
| `▁oluşmaktadır` | 485 | 485 | 1.000000 | -0.500000 |
| `▁biridir` | 473 | 473 | 1.000000 | -0.500000 |
| `▁çıkmaktadır` | 438 | 438 | 1.000000 | -0.500000 |
| `▁değildir` | 419 | 419 | 1.000000 | -0.500000 |
| `lardır` | 402 | 402 | 1.000000 | -0.500000 |
| `▁taşımaktadır` | 399 | 399 | 1.000000 | -0.500000 |
| `▁almıştır` | 389 | 389 | 1.000000 | -0.500000 |
| `kullanılmaktadır` | 386 | 386 | 1.000000 | -0.500000 |
| `▁gelmektedir` | 377 | 377 | 1.000000 | -0.500000 |
| `▁başlamıştır` | 374 | 374 | 1.000000 | -0.500000 |
| `▁sunulmuştur` | 355 | 355 | 1.000000 | -0.500000 |
| `▁oluşturmuştur` | 349 | 349 | 1.000000 | -0.500000 |
| `▁koymaktadır` | 330 | 330 | 1.000000 | -0.500000 |
| `▁oluşturulmuştur` | 319 | 319 | 1.000000 | -0.500000 |
| `▁varılmıştır` | 314 | 314 | 1.000000 | -0.500000 |
| `▁mümkündür` | 306 | 306 | 1.000000 | -0.500000 |

## Next

Evaluate this model with the finite protected wrapper. Continue only if
it improves normal-text morphology F1 without materially increasing
tokens/raw byte or breaking roundtrip/protected invariants.
