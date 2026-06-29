# v2.0 Score-Shifted SentencePiece Model

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_score_shifted_sp/score_shift_mass_lambda1_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_score_shifted_sp/score_shift_mass_lambda1_unigram_64000.vocab`

This is a train-only post-hoc Unigram score-shift probe. It does not
change the vocabulary or add runtime boundary markers. It lowers scores
for pieces that frequently cross custom-teacher soft morphology
boundaries in the train split.

## Parameters

| Parameter | Value |
| --- | ---: |
| penalty_lambda | 1.000000 |
| penalty_mode | mass |
| min_count | 20 |
| min_crossing_count | 20 |
| min_crossing_rate | 0.000000 |
| min_surface_len | 2 |
| max_penalty | 8.000000 |

## Summary

| Metric | Value |
| --- | ---: |
| scanned lines | 16000 |
| observed pieces | 60119 |
| pieces with crossing evidence | 19322 |
| adjusted pieces | 4592 |
| alignment failures | 0 |

## Top Adjusted Pieces

| Piece | Count | Crossing count | Crossing rate | Score delta |
| --- | ---: | ---: | ---: | ---: |
| `▁kullanılmıştır` | 2835 | 2835 | 1.000000 | -0.529907 |
| `▁yapılmıştır` | 1860 | 1860 | 1.000000 | -0.347663 |
| `▁olmuştur` | 1536 | 1536 | 1.000000 | -0.287103 |
| `▁görülmüştür` | 1405 | 1405 | 1.000000 | -0.262617 |
| `mektedir` | 1197 | 1197 | 1.000000 | -0.223739 |
| `▁oluşturmaktadır` | 1188 | 1188 | 1.000000 | -0.222056 |
| `▁etmektedir` | 1088 | 1088 | 1.000000 | -0.203364 |
| `▁alınmıştır` | 1067 | 1067 | 1.000000 | -0.199439 |
| `▁görülmektedir` | 1056 | 1056 | 1.000000 | -0.197383 |
| `mıştır` | 988 | 988 | 1.000000 | -0.184673 |
| `maktadır` | 850 | 850 | 1.000000 | -0.158878 |
| `▁bulunmaktadır` | 766 | 766 | 1.000000 | -0.143178 |
| `▁sahiptir` | 754 | 754 | 1.000000 | -0.140935 |
| `▁ulaşılmıştır` | 747 | 747 | 1.000000 | -0.139627 |
| `▁uygulanmıştır` | 709 | 709 | 1.000000 | -0.132524 |
| `▁önemlidir` | 659 | 659 | 1.000000 | -0.123178 |
| `▁almaktadır` | 625 | 625 | 1.000000 | -0.116822 |
| `▁amaçlamaktadır` | 606 | 606 | 1.000000 | -0.113271 |
| `▁verilmiştir` | 597 | 597 | 1.000000 | -0.111588 |
| `▁toplanmıştır` | 586 | 586 | 1.000000 | -0.109532 |
| `▁olmaktadır` | 540 | 540 | 1.000000 | -0.100935 |
| `▁etmiştir` | 525 | 525 | 1.000000 | -0.098131 |
| `▁yürütülmüştür` | 519 | 519 | 1.000000 | -0.097010 |
| `▁gerekmektedir` | 496 | 496 | 1.000000 | -0.092710 |
| `▁oluşmaktadır` | 485 | 485 | 1.000000 | -0.090654 |
| `▁biridir` | 473 | 473 | 1.000000 | -0.088411 |
| `▁çıkmaktadır` | 438 | 438 | 1.000000 | -0.081869 |
| `▁değildir` | 419 | 419 | 1.000000 | -0.078318 |
| `lardır` | 402 | 402 | 1.000000 | -0.075140 |
| `▁taşımaktadır` | 399 | 399 | 1.000000 | -0.074579 |
| `▁almıştır` | 389 | 389 | 1.000000 | -0.072710 |
| `kullanılmaktadır` | 386 | 386 | 1.000000 | -0.072149 |
| `▁gelmektedir` | 377 | 377 | 1.000000 | -0.070467 |
| `▁başlamıştır` | 374 | 374 | 1.000000 | -0.069906 |
| `▁sunulmuştur` | 355 | 355 | 1.000000 | -0.066355 |
| `▁oluşturmuştur` | 349 | 349 | 1.000000 | -0.065233 |
| `▁koymaktadır` | 330 | 330 | 1.000000 | -0.061683 |
| `▁oluşturulmuştur` | 319 | 319 | 1.000000 | -0.059627 |
| `▁varılmıştır` | 314 | 314 | 1.000000 | -0.058692 |
| `▁mümkündür` | 306 | 306 | 1.000000 | -0.057197 |

## Next

Evaluate this model with the finite protected wrapper. Continue only if
it improves normal-text morphology F1 without materially increasing
tokens/raw byte or breaking roundtrip/protected invariants.
