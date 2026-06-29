# v2.0 Eval Crossing Piece Source Audit

Dataset: `data/eval/tr_gold_expanded.tsv`
Train stats: `artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json`

This report re-attributes deployed eval crossings using train-side
crossing statistics. It avoids treating eval one-off crossing rates as
evidence of concentration.

It also checks whether crossing pieces in a score-distilled model carry
floor scores or counted scores.

## Summary

| Model | Examples | Segments | Teacher boundaries | Crossed boundaries | Crossed boundary rate | Crossing piece occurrences | Alignment failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sp64` | 50 | 158 | 153 | 79 | 0.516340 | 64 | 0 |
| `teacher_distilled_16k` | 50 | 158 | 153 | 55 | 0.359477 | 45 | 0 |

## Train-Side Attribution: `sp64`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| train_rate=1.00 | 0 | 0 | 0 | 0.000000 |
| train_rate=0.70-0.99 | 16 | 31 | 34 | 0.430380 |
| train_rate=0.40-0.69 | 2 | 2 | 2 | 0.025316 |
| train_rate=0.20-0.39 | 2 | 3 | 3 | 0.037975 |
| train_rate=0.00-0.19 | 5 | 8 | 9 | 0.113924 |
| train_rate=0.00 | 1 | 1 | 1 | 0.012658 |
| train_count< 20 | 13 | 19 | 30 | 0.379747 |
| no_train_stats | 0 | 0 | 0 | 0.000000 |

## Score Attribution: `sp64`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| counted_score | 39 | 64 | 79 | 1.000000 |
| floor_score | 0 | 0 | 0 | 0.000000 |
| score_missing | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Eval crossed boundaries | Eval crossing occurrences | Train count | Train crossing count | Train crossing rate | Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `larımızdan` | 8 | 4 | 10 | 10 | 1.000000 | -12.783038 |
| `lerden` | 4 | 4 | 986 | 968 | 0.981744 | -8.116520 |
| `▁aldı` | 4 | 4 | 54 | 53 | 0.981481 | -11.026914 |
| `▁geldi` | 4 | 4 | 67 | 58 | 0.865672 | -10.903255 |
| `larımızda` | 4 | 2 | 14 | 14 | 1.000000 | -12.511462 |
| `▁altında` | 4 | 2 | 1049 | 1026 | 0.978074 | -8.115650 |
| `dim` | 3 | 3 | 20 | 14 | 0.700000 | -12.050552 |
| `▁Alaca` | 3 | 3 | 25 | 4 | 0.160000 | -12.088184 |
| `diler` | 2 | 2 | 29 | 28 | 0.965517 | -11.677504 |
| `▁birini` | 2 | 2 | 99 | 95 | 0.959596 | -10.548139 |
| `▁gitti` | 2 | 2 | 9 | 9 | 1.000000 | -12.953035 |
| `tim` | 2 | 2 | 49 | 17 | 0.346939 | -11.158456 |
| `um` | 2 | 2 | 409 | 59 | 0.144254 | -9.086095 |
| `▁dosyası` | 2 | 2 | 13 | 13 | 1.000000 | -12.623216 |
| `▁açtı` | 2 | 2 | 24 | 23 | 0.958333 | -11.913140 |
| `▁Evleri` | 2 | 1 | 8 | 7 | 0.875000 | -12.844005 |
| `mizdeki` | 2 | 1 | 13 | 12 | 0.923077 | -12.446866 |
| `ğini` | 2 | 1 | 17 | 17 | 1.000000 | -12.148074 |
| `ttin` | 2 | 1 | 10 | 10 | 1.000000 | -12.644881 |
| `labilecek` | 2 | 1 | 36 | 34 | 0.944444 | -11.740438 |
| `▁Kitapları` | 2 | 1 | 18 | 16 | 0.888889 | -11.831203 |
| `lamayan` | 2 | 1 | 22 | 4 | 0.181818 | -11.907444 |
| `▁oldu` | 1 | 1 | 212 | 207 | 0.976415 | -9.684240 |
| `▁kitabı` | 1 | 1 | 223 | 214 | 0.959641 | -9.666260 |
| `▁kayboldu` | 1 | 1 | 4 | 4 | 1.000000 | -13.813478 |
| `▁Kitabı` | 1 | 1 | 43 | 27 | 0.627907 | -11.213621 |
| `▁Ağacı` | 1 | 1 | 27 | 24 | 0.888889 | -11.793164 |
| `ini` | 1 | 1 | 395 | 354 | 0.896203 | -8.662354 |
| `adı` | 1 | 1 | 34 | 4 | 0.117647 | -11.465362 |
| `▁Çocuğun` | 1 | 1 | 22 | 21 | 0.954545 | -12.003451 |
| `cağı` | 1 | 1 | 13 | 3 | 0.230769 | -12.731957 |
| `rıldı` | 1 | 1 | 9 | 0 | 0.000000 | -12.919312 |
| `emeyecek` | 1 | 1 | 21 | 17 | 0.809524 | -12.281666 |
| `amayacak` | 1 | 1 | 12 | 12 | 1.000000 | -12.746415 |
| `din` | 1 | 1 | 59 | 31 | 0.525424 | -10.760761 |
| `▁yaptı` | 1 | 1 | 32 | 8 | 0.250000 | -11.530468 |
| `ıyor` | 1 | 1 | 50 | 0 | 0.000000 | -11.098442 |
| `li` | 1 | 1 | 3068 | 15 | 0.004889 | -6.899472 |
| `lardan` | 1 | 1 | 896 | 879 | 0.981027 | -8.249237 |

## Train-Side Attribution: `teacher_distilled_16k`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| train_rate=1.00 | 0 | 0 | 0 | 0.000000 |
| train_rate=0.70-0.99 | 11 | 22 | 25 | 0.454545 |
| train_rate=0.40-0.69 | 1 | 1 | 1 | 0.018182 |
| train_rate=0.20-0.39 | 1 | 1 | 1 | 0.018182 |
| train_rate=0.00-0.19 | 7 | 10 | 11 | 0.200000 |
| train_rate=0.00 | 2 | 2 | 2 | 0.036364 |
| train_count< 20 | 7 | 9 | 15 | 0.272727 |
| no_train_stats | 0 | 0 | 0 | 0.000000 |

## Score Attribution: `teacher_distilled_16k`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| counted_score | 29 | 45 | 55 | 1.000000 |
| floor_score | 0 | 0 | 0 | 0.000000 |
| score_missing | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Eval crossed boundaries | Eval crossing occurrences | Train count | Train crossing count | Train crossing rate | Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `larımız` | 4 | 4 | 20 | 15 | 0.750000 | -13.667802 |
| `▁aldı` | 4 | 4 | 54 | 53 | 0.981481 | -11.780732 |
| `▁geldi` | 4 | 4 | 67 | 58 | 0.865672 | -12.638182 |
| `▁Kitapları` | 4 | 2 | 18 | 16 | 0.888889 | -14.584092 |
| `▁altında` | 4 | 2 | 1049 | 1026 | 0.978074 | -12.141746 |
| `ım` | 3 | 3 | 161 | 4 | 0.024845 | -6.009385 |
| `amayacakları` | 3 | 1 | 8 | 3 | 0.375000 | -13.485480 |
| `▁gitti` | 2 | 2 | 9 | 9 | 1.000000 | -15.277240 |
| `um` | 2 | 2 | 409 | 59 | 0.144254 | -5.942648 |
| `sını` | 2 | 2 | 230 | 217 | 0.943478 | -12.504651 |
| `▁Evleri` | 2 | 1 | 8 | 7 | 0.875000 | -15.277240 |
| `mizdeki` | 2 | 1 | 13 | 12 | 0.923077 | -15.277240 |
| `labilecek` | 2 | 1 | 36 | 34 | 0.944444 | -15.277240 |
| `lamayan` | 2 | 1 | 22 | 4 | 0.181818 | -12.332800 |
| `▁oldu` | 1 | 1 | 212 | 207 | 0.976415 | -11.876042 |
| `▁kil` | 1 | 1 | 101 | 0 | 0.000000 | -10.357259 |
| `▁kitabı` | 1 | 1 | 223 | 214 | 0.959641 | -13.080015 |
| `oldu` | 1 | 1 | 6 | 0 | 0.000000 | -13.197798 |
| `▁Ağacı` | 1 | 1 | 27 | 24 | 0.888889 | -14.178627 |
| `gi` | 1 | 1 | 96 | 4 | 0.041667 | -9.712719 |
| `adı` | 1 | 1 | 34 | 4 | 0.117647 | -11.693721 |
| `eği` | 1 | 1 | 33 | 1 | 0.030303 | -7.072841 |
| `▁Çocuğun` | 1 | 1 | 22 | 21 | 0.954545 | -15.277240 |
| `cağı` | 1 | 1 | 13 | 3 | 0.230769 | -12.974654 |
| `ın` | 1 | 1 | 2419 | 153 | 0.063249 | -4.954745 |
| `emeyecek` | 1 | 1 | 21 | 17 | 0.809524 | -13.667802 |
| `din` | 1 | 1 | 59 | 31 | 0.525424 | -10.755451 |
| `▁yaptı` | 1 | 1 | 32 | 8 | 0.250000 | -11.043133 |
| `ıyor` | 1 | 1 | 50 | 0 | 0.000000 | -10.799903 |

## Reading

If most eval crossings come from pieces that were high-crossing in the
train statistics, targeted inventory pruning may still have headroom.
If most come from low/zero/unsupported train-rate pieces, the remaining
damage is context-dependent and context-free pruning is near its limit.

For teacher-distilled score-bound models, crossing pieces with floor
scores would indicate a serialization/scoring problem. Crossing pieces
with counted scores mean the bound is mechanically valid and the limit
is in the global score/inventory family itself.
