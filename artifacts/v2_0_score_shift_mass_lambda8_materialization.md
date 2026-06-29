# v2.0 Score-Shifted SentencePiece Model

Source model: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Train path: `artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split/train.txt`
Output model: `artifacts/private/v2_0_score_shifted_sp/score_shift_mass_lambda8_unigram_64000.model`
Output vocab: `artifacts/private/v2_0_score_shifted_sp/score_shift_mass_lambda8_unigram_64000.vocab`

This is a train-only post-hoc Unigram score-shift probe. It does not
change the vocabulary or add runtime boundary markers. It lowers scores
for pieces that frequently cross custom-teacher soft morphology
boundaries in the train split.

## Parameters

| Parameter | Value |
| --- | ---: |
| penalty_lambda | 8.000000 |
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
| `▁kullanılmıştır` | 2835 | 2835 | 1.000000 | -4.239252 |
| `▁yapılmıştır` | 1860 | 1860 | 1.000000 | -2.781309 |
| `▁olmuştur` | 1536 | 1536 | 1.000000 | -2.296822 |
| `▁görülmüştür` | 1405 | 1405 | 1.000000 | -2.100935 |
| `mektedir` | 1197 | 1197 | 1.000000 | -1.789907 |
| `▁oluşturmaktadır` | 1188 | 1188 | 1.000000 | -1.776448 |
| `▁etmektedir` | 1088 | 1088 | 1.000000 | -1.626916 |
| `▁alınmıştır` | 1067 | 1067 | 1.000000 | -1.595514 |
| `▁görülmektedir` | 1056 | 1056 | 1.000000 | -1.579065 |
| `mıştır` | 988 | 988 | 1.000000 | -1.477384 |
| `maktadır` | 850 | 850 | 1.000000 | -1.271028 |
| `▁bulunmaktadır` | 766 | 766 | 1.000000 | -1.145421 |
| `▁sahiptir` | 754 | 754 | 1.000000 | -1.127477 |
| `▁ulaşılmıştır` | 747 | 747 | 1.000000 | -1.117009 |
| `▁uygulanmıştır` | 709 | 709 | 1.000000 | -1.060187 |
| `▁önemlidir` | 659 | 659 | 1.000000 | -0.985420 |
| `▁almaktadır` | 625 | 625 | 1.000000 | -0.934580 |
| `▁amaçlamaktadır` | 606 | 606 | 1.000000 | -0.906168 |
| `▁verilmiştir` | 597 | 597 | 1.000000 | -0.892711 |
| `▁toplanmıştır` | 586 | 586 | 1.000000 | -0.876262 |
| `▁olmaktadır` | 540 | 540 | 1.000000 | -0.807477 |
| `▁etmiştir` | 525 | 525 | 1.000000 | -0.785047 |
| `▁yürütülmüştür` | 519 | 519 | 1.000000 | -0.776074 |
| `▁gerekmektedir` | 496 | 496 | 1.000000 | -0.741682 |
| `▁oluşmaktadır` | 485 | 485 | 1.000000 | -0.725234 |
| `▁biridir` | 473 | 473 | 1.000000 | -0.707290 |
| `▁çıkmaktadır` | 438 | 438 | 1.000000 | -0.654953 |
| `▁değildir` | 419 | 419 | 1.000000 | -0.626542 |
| `lardır` | 402 | 402 | 1.000000 | -0.601122 |
| `▁taşımaktadır` | 399 | 399 | 1.000000 | -0.596636 |
| `▁almıştır` | 389 | 389 | 1.000000 | -0.581682 |
| `kullanılmaktadır` | 386 | 386 | 1.000000 | -0.577196 |
| `▁gelmektedir` | 377 | 377 | 1.000000 | -0.563738 |
| `▁başlamıştır` | 374 | 374 | 1.000000 | -0.559253 |
| `▁sunulmuştur` | 355 | 355 | 1.000000 | -0.530841 |
| `▁oluşturmuştur` | 349 | 349 | 1.000000 | -0.521869 |
| `▁koymaktadır` | 330 | 330 | 1.000000 | -0.493458 |
| `▁oluşturulmuştur` | 319 | 319 | 1.000000 | -0.477010 |
| `▁varılmıştır` | 314 | 314 | 1.000000 | -0.469533 |
| `▁mümkündür` | 306 | 306 | 1.000000 | -0.457570 |

## Next

Evaluate this model with the finite protected wrapper. Continue only if
it improves normal-text morphology F1 without materially increasing
tokens/raw byte or breaking roundtrip/protected invariants.
