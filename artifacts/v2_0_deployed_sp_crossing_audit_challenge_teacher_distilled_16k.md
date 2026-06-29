# v2.0 Deployed SP Viterbi Crossing Audit

Dataset: `data/eval/tr_challenge.tsv`

This report measures crossings from the serialized model's deployed
SentencePiece Viterbi path, not the tilted training posterior.

## Summary

| Model | Examples | Segments | Teacher boundaries | Crossed boundaries | Crossed boundary rate | Model pieces | Pieces/word | Crossing piece rate | Alignment failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sp64` | 108 | 464 | 305 | 170 | 0.557377 | 730 | 1.9060 | 0.191781 | 0 |
| `teacher_distilled_16k` | 108 | 464 | 305 | 139 | 0.455738 | 787 | 2.0548 | 0.153748 | 0 |

## Crossing Attribution: `sp64`

| Piece crossing-rate bucket | Piece types | Piece occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| 1.00 | 89 | 136 | 166 | 0.976471 |
| 0.70-0.99 | 0 | 0 | 0 | 0.000000 |
| 0.40-0.69 | 2 | 5 | 3 | 0.017647 |
| 0.20-0.39 | 1 | 3 | 1 | 0.005882 |
| 0.00-0.19 | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Count | Crossing occurrences | Crossed boundaries | Occurrence crossing rate | Crossing count rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `lerden` | 7 | 7 | 7 | 1.000000 | 1.000000 |
| `dim` | 6 | 6 | 6 | 1.000000 | 1.000000 |
| `larımızdan` | 3 | 3 | 6 | 1.000000 | 2.000000 |
| `dık` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁döndü` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁açtı` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `larımızda` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁aldık` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `adım` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁gittik` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁yeniden` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁geldi` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `▁vardı` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `niz` | 3 | 2 | 2 | 0.666667 | 0.666667 |
| `leri` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `sini` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `daki` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `diler` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁kitabı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁verdi` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁gördü` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁dosyası` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁aldı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `cağı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁Yazın` | 2 | 2 | 2 | 1.000000 | 1.000000 |

## Crossing Attribution: `teacher_distilled_16k`

| Piece crossing-rate bucket | Piece types | Piece occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| 1.00 | 65 | 102 | 120 | 0.863309 |
| 0.70-0.99 | 2 | 15 | 12 | 0.086331 |
| 0.40-0.69 | 3 | 12 | 7 | 0.050360 |
| 0.20-0.39 | 0 | 0 | 0 | 0.000000 |
| 0.00-0.19 | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Count | Crossing occurrences | Crossed boundaries | Occurrence crossing rate | Crossing count rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ım` | 9 | 7 | 7 | 0.777778 | 0.777778 |
| `larımız` | 5 | 5 | 5 | 1.000000 | 1.000000 |
| `im` | 6 | 5 | 5 | 0.833333 | 0.833333 |
| `dık` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁döndü` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `ın` | 7 | 4 | 4 | 0.571429 | 0.571429 |
| `▁aldık` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁gittik` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁yeniden` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `ad` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `▁geldi` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `▁vardı` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `üm` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `ld` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `din` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `led` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `leri` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁kitabı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁verdi` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁gördü` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `sını` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁aldı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `cağı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁Yazın` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `um` | 3 | 2 | 2 | 0.666667 | 0.666667 |

## Reading

If lambda-trained/distilled models do not reduce deployed Viterbi crossings,
the training posterior signal is not surviving projection into the serialized
Unigram model. If crossings are concentrated in high-rate pieces, inventory
work may help; diffuse medium-rate damage points toward a context-free limit.
