# v2.0 Eval Crossing Piece Source Audit

Dataset: `data/eval/tr_challenge.tsv`
Train stats: `artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json`

This report re-attributes deployed eval crossings using train-side
crossing statistics. It avoids treating eval one-off crossing rates as
evidence of concentration.

It also checks whether crossing pieces in a score-distilled model carry
floor scores or counted scores.

## Summary

| Model | Examples | Segments | Teacher boundaries | Crossed boundaries | Crossed boundary rate | Crossing piece occurrences | Alignment failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sp64` | 108 | 464 | 305 | 170 | 0.557377 | 140 | 0 |
| `teacher_distilled_16k` | 108 | 464 | 305 | 139 | 0.455738 | 121 | 0 |
| `pruned_ge070_nonword` | 108 | 464 | 305 | 151 | 0.495082 | 121 | 0 |

## Train-Side Attribution: `sp64`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| train_rate=1.00 | 3 | 5 | 7 | 0.041176 |
| train_rate=0.70-0.99 | 37 | 63 | 69 | 0.405882 |
| train_rate=0.40-0.69 | 2 | 3 | 3 | 0.017647 |
| train_rate=0.20-0.39 | 1 | 2 | 2 | 0.011765 |
| train_rate=0.00-0.19 | 10 | 13 | 13 | 0.076471 |
| train_rate=0.00 | 1 | 1 | 1 | 0.005882 |
| train_count< 20 | 38 | 53 | 75 | 0.441176 |
| no_train_stats | 0 | 0 | 0 | 0.000000 |

## Score Attribution: `sp64`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| counted_score | 92 | 140 | 170 | 1.000000 |
| floor_score | 0 | 0 | 0 | 0.000000 |
| score_missing | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Eval crossed boundaries | Eval crossing occurrences | Train count | Train crossing count | Train crossing rate | Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `lerden` | 7 | 7 | 986 | 968 | 0.981744 | -8.116520 |
| `dim` | 6 | 6 | 20 | 14 | 0.700000 | -12.050552 |
| `larımızdan` | 6 | 3 | 10 | 10 | 1.000000 | -12.783038 |
| `dık` | 4 | 4 | 37 | 32 | 0.864865 | -11.269510 |
| `▁döndü` | 4 | 4 | 16 | 6 | 0.375000 | -12.337378 |
| `▁açtı` | 4 | 4 | 24 | 23 | 0.958333 | -11.913140 |
| `larımızda` | 4 | 2 | 14 | 14 | 1.000000 | -12.511462 |
| `▁aldık` | 4 | 2 | 15 | 14 | 0.933333 | -12.130407 |
| `adım` | 4 | 2 | 4 | 4 | 1.000000 | -13.514901 |
| `▁gittik` | 4 | 2 | 13 | 0 | 0.000000 | -12.587613 |
| `▁yeniden` | 4 | 2 | 995 | 970 | 0.974874 | -8.180124 |
| `▁geldi` | 3 | 3 | 67 | 58 | 0.865672 | -10.903255 |
| `▁vardı` | 3 | 3 | 95 | 95 | 1.000000 | -10.522627 |
| `niz` | 2 | 2 | 28 | 9 | 0.321429 | -11.823159 |
| `leri` | 2 | 2 | 3009 | 41 | 0.013626 | -7.024103 |
| `sini` | 2 | 2 | 383 | 362 | 0.945170 | -8.923077 |
| `daki` | 2 | 2 | 1002 | 971 | 0.969062 | -7.712314 |
| `diler` | 2 | 2 | 29 | 28 | 0.965517 | -11.677504 |
| `▁kitabı` | 2 | 2 | 223 | 214 | 0.959641 | -9.666260 |
| `▁verdi` | 2 | 2 | 38 | 5 | 0.131579 | -11.331605 |
| `▁gördü` | 2 | 2 | 4 | 0 | 0.000000 | -13.536433 |
| `▁dosyası` | 2 | 2 | 13 | 13 | 1.000000 | -12.623216 |
| `▁aldı` | 2 | 2 | 54 | 53 | 0.981481 | -11.026914 |
| `cağı` | 2 | 2 | 13 | 3 | 0.230769 | -12.731957 |
| `▁Yazın` | 2 | 2 | 9 | 5 | 0.555556 | -12.742117 |
| `um` | 2 | 2 | 409 | 59 | 0.144254 | -9.086095 |
| `amayacak` | 2 | 2 | 12 | 12 | 1.000000 | -12.746415 |
| `dini` | 2 | 2 | 12 | 7 | 0.583333 | -12.367192 |
| `dik` | 2 | 2 | 62 | 35 | 0.564516 | -10.772795 |
| `▁oldu` | 2 | 2 | 212 | 207 | 0.976415 | -9.684240 |
| `▁Evleri` | 2 | 1 | 8 | 7 | 0.875000 | -12.844005 |
| `▁Defterleri` | 2 | 1 | 8 | 0 | 0.000000 | -13.070181 |
| `mizdeki` | 2 | 1 | 13 | 12 | 0.923077 | -12.446866 |
| `▁Odaları` | 2 | 1 | 7 | 0 | 0.000000 | -13.219808 |
| `▁çıkardıkları` | 2 | 1 | 14 | 0 | 0.000000 | -12.517413 |
| `▁Soruları` | 2 | 1 | 16 | 0 | 0.000000 | -12.413423 |
| `▁evinde` | 2 | 1 | 23 | 23 | 1.000000 | -11.999876 |
| `▁gölünü` | 2 | 1 | 7 | 7 | 1.000000 | -13.709812 |
| `larından` | 2 | 1 | 647 | 628 | 0.970634 | -8.573436 |
| `▁Kitabın` | 2 | 1 | 41 | 41 | 1.000000 | -11.492769 |

## Train-Side Attribution: `teacher_distilled_16k`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| train_rate=1.00 | 1 | 3 | 3 | 0.021583 |
| train_rate=0.70-0.99 | 22 | 36 | 41 | 0.294964 |
| train_rate=0.40-0.69 | 3 | 6 | 6 | 0.043165 |
| train_rate=0.20-0.39 | 0 | 0 | 0 | 0.000000 |
| train_rate=0.00-0.19 | 16 | 36 | 36 | 0.258993 |
| train_rate=0.00 | 3 | 5 | 5 | 0.035971 |
| train_count< 20 | 25 | 35 | 48 | 0.345324 |
| no_train_stats | 0 | 0 | 0 | 0.000000 |

## Score Attribution: `teacher_distilled_16k`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| counted_score | 69 | 120 | 137 | 0.985612 |
| floor_score | 1 | 1 | 2 | 0.014388 |
| score_missing | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Eval crossed boundaries | Eval crossing occurrences | Train count | Train crossing count | Train crossing rate | Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ım` | 7 | 7 | 161 | 4 | 0.024845 | -6.009385 |
| `larımız` | 5 | 5 | 20 | 15 | 0.750000 | -13.667802 |
| `im` | 5 | 5 | 243 | 8 | 0.032922 | -5.617736 |
| `dık` | 4 | 4 | 37 | 32 | 0.864865 | -11.539570 |
| `▁döndü` | 4 | 4 | 16 | 6 | 0.375000 | -12.974654 |
| `ın` | 4 | 4 | 2419 | 153 | 0.063249 | -4.954745 |
| `▁aldık` | 4 | 2 | 15 | 14 | 0.933333 | -12.569189 |
| `▁gittik` | 4 | 2 | 13 | 0 | 0.000000 | -12.712290 |
| `▁yeniden` | 4 | 2 | 995 | 970 | 0.974874 | -12.058364 |
| `ad` | 3 | 3 | 104 | 2 | 0.019231 | -8.936880 |
| `▁geldi` | 3 | 3 | 67 | 58 | 0.865672 | -12.638182 |
| `▁vardı` | 3 | 3 | 95 | 95 | 1.000000 | -15.277240 |
| `üm` | 3 | 3 | 50 | 2 | 0.040000 | -7.259273 |
| `ld` | 3 | 3 | 17 | 0 | 0.000000 | -11.613678 |
| `din` | 3 | 3 | 59 | 31 | 0.525424 | -10.755451 |
| `led` | 3 | 3 | 26 | 0 | 0.000000 | -11.588360 |
| `leri` | 2 | 2 | 3009 | 41 | 0.013626 | -7.066571 |
| `▁kitabı` | 2 | 2 | 223 | 214 | 0.959641 | -13.080015 |
| `▁verdi` | 2 | 2 | 38 | 5 | 0.131579 | -11.539570 |
| `▁gördü` | 2 | 2 | 4 | 0 | 0.000000 | -12.569189 |
| `sını` | 2 | 2 | 230 | 217 | 0.943478 | -12.504651 |
| `▁aldı` | 2 | 2 | 54 | 53 | 0.981481 | -11.780732 |
| `cağı` | 2 | 2 | 13 | 3 | 0.230769 | -12.974654 |
| `▁Yazın` | 2 | 2 | 9 | 5 | 0.555556 | -13.890945 |
| `um` | 2 | 2 | 409 | 59 | 0.144254 | -5.942648 |
| `dik` | 2 | 2 | 62 | 35 | 0.564516 | -10.672070 |
| `▁oldu` | 2 | 2 | 212 | 207 | 0.976415 | -11.876042 |
| `▁Defterleri` | 2 | 1 | 8 | 0 | 0.000000 | -13.197798 |
| `mizdeki` | 2 | 1 | 13 | 12 | 0.923077 | -15.277240 |
| `▁Odaları` | 2 | 1 | 7 | 0 | 0.000000 | -13.331329 |
| `▁çıkardıkları` | 2 | 1 | 14 | 0 | 0.000000 | -12.638182 |
| `▁Soruları` | 2 | 1 | 16 | 0 | 0.000000 | -12.504651 |
| `basın` | 2 | 1 | 7 | 3 | 0.428571 | -13.890945 |
| `▁yazısı` | 2 | 1 | 45 | 44 | 0.977778 | -15.277240 |
| `▁verdik` | 2 | 1 | 16 | 9 | 0.562500 | -13.331329 |
| `▁Kitapları` | 2 | 1 | 18 | 16 | 0.888889 | -14.584092 |
| `laştırılmış` | 2 | 1 | 99 | 97 | 0.979798 | -14.584092 |
| `▁okudum` | 2 | 1 | 5 | 5 | 1.000000 | -30.000000 |
| `▁değerini` | 2 | 1 | 85 | 82 | 0.964706 | -14.178627 |
| `lerin` | 1 | 1 | 2501 | 28 | 0.011196 | -6.932022 |

## Train-Side Attribution: `pruned_ge070_nonword`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| train_rate=1.00 | 3 | 5 | 7 | 0.046358 |
| train_rate=0.70-0.99 | 20 | 34 | 38 | 0.251656 |
| train_rate=0.40-0.69 | 2 | 3 | 3 | 0.019868 |
| train_rate=0.20-0.39 | 1 | 2 | 2 | 0.013245 |
| train_rate=0.00-0.19 | 12 | 16 | 16 | 0.105960 |
| train_rate=0.00 | 1 | 1 | 1 | 0.006623 |
| train_count< 20 | 40 | 60 | 84 | 0.556291 |
| no_train_stats | 0 | 0 | 0 | 0.000000 |

## Score Attribution: `pruned_ge070_nonword`

| Bucket | Piece types | Eval crossing occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| counted_score | 79 | 121 | 151 | 1.000000 |
| floor_score | 0 | 0 | 0 | 0.000000 |
| score_missing | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Eval crossed boundaries | Eval crossing occurrences | Train count | Train crossing count | Train crossing rate | Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `larımızda` | 8 | 4 | 14 | 14 | 1.000000 | -12.511462 |
| `dim` | 6 | 6 | 20 | 14 | 0.700000 | -12.050552 |
| `larımızdan` | 6 | 3 | 10 | 10 | 1.000000 | -12.783038 |
| `▁döndü` | 4 | 4 | 16 | 6 | 0.375000 | -12.337378 |
| `▁açtı` | 4 | 4 | 24 | 23 | 0.958333 | -11.913140 |
| `▁aldık` | 4 | 2 | 15 | 14 | 0.933333 | -12.130407 |
| `adım` | 4 | 2 | 4 | 4 | 1.000000 | -13.514901 |
| `▁gittik` | 4 | 2 | 13 | 0 | 0.000000 | -12.587613 |
| `▁yeniden` | 4 | 2 | 995 | 970 | 0.974874 | -8.180124 |
| `▁geldi` | 3 | 3 | 67 | 58 | 0.865672 | -10.903255 |
| `▁vardı` | 3 | 3 | 95 | 95 | 1.000000 | -10.522627 |
| `bilecek` | 3 | 3 | 13 | 12 | 0.923077 | -12.213736 |
| `niz` | 2 | 2 | 28 | 9 | 0.321429 | -11.823159 |
| `leri` | 2 | 2 | 3009 | 41 | 0.013626 | -7.024103 |
| `▁ayırd` | 2 | 2 | 7 | 0 | 0.000000 | -13.202074 |
| `ık` | 2 | 2 | 71 | 8 | 0.112676 | -10.517703 |
| `▁kitabı` | 2 | 2 | 223 | 214 | 0.959641 | -9.666260 |
| `▁verdi` | 2 | 2 | 38 | 5 | 0.131579 | -11.331605 |
| `▁gördü` | 2 | 2 | 4 | 0 | 0.000000 | -13.536433 |
| `▁dosyası` | 2 | 2 | 13 | 13 | 1.000000 | -12.623216 |
| `▁aldı` | 2 | 2 | 54 | 53 | 0.981481 | -11.026914 |
| `cağı` | 2 | 2 | 13 | 3 | 0.230769 | -12.731957 |
| `▁Yazın` | 2 | 2 | 9 | 5 | 0.555556 | -12.742117 |
| `um` | 2 | 2 | 409 | 59 | 0.144254 | -9.086095 |
| `amayacak` | 2 | 2 | 12 | 12 | 1.000000 | -12.746415 |
| `dini` | 2 | 2 | 12 | 7 | 0.583333 | -12.367192 |
| `dik` | 2 | 2 | 62 | 35 | 0.564516 | -10.772795 |
| `▁oldu` | 2 | 2 | 212 | 207 | 0.976415 | -9.684240 |
| `▁Evleri` | 2 | 1 | 8 | 7 | 0.875000 | -12.844005 |
| `▁Defterleri` | 2 | 1 | 8 | 0 | 0.000000 | -13.070181 |
| `mizdeki` | 2 | 1 | 13 | 12 | 0.923077 | -12.446866 |
| `▁çıkardıkları` | 2 | 1 | 14 | 0 | 0.000000 | -12.517413 |
| `▁evinde` | 2 | 1 | 23 | 23 | 1.000000 | -11.999876 |
| `basın` | 2 | 1 | 7 | 3 | 0.428571 | -12.758426 |
| `▁gölünü` | 2 | 1 | 7 | 7 | 1.000000 | -13.709812 |
| `▁Kitabın` | 2 | 1 | 41 | 41 | 1.000000 | -11.492769 |
| `ğinden` | 2 | 1 | 12 | 11 | 0.916667 | -12.765739 |
| `▁yazısı` | 2 | 1 | 45 | 44 | 0.977778 | -11.378897 |
| `▁verdik` | 2 | 1 | 16 | 9 | 0.562500 | -12.525843 |
| `▁Kitapları` | 2 | 1 | 18 | 16 | 0.888889 | -11.831203 |

## Reading

If most eval crossings come from pieces that were high-crossing in the
train statistics, targeted inventory pruning may still have headroom.
If most come from low/zero/unsupported train-rate pieces, the remaining
damage is context-dependent and context-free pruning is near its limit.

For teacher-distilled score-bound models, crossing pieces with floor
scores would indicate a serialization/scoring problem. Crossing pieces
with counted scores mean the bound is mechanically valid and the limit
is in the global score/inventory family itself.
