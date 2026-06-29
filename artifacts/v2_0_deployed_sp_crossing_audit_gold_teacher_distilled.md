# v2.0 Deployed SP Viterbi Crossing Audit

Dataset: `data/eval/tr_gold_expanded.tsv`

This report measures crossings from the serialized model's deployed
SentencePiece Viterbi path, not the tilted training posterior.

## Summary

| Model | Examples | Segments | Teacher boundaries | Crossed boundaries | Crossed boundary rate | Model pieces | Pieces/word | Crossing piece rate | Alignment failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sp64` | 50 | 158 | 153 | 79 | 0.516340 | 269 | 2.2231 | 0.237918 | 0 |
| `teacher_distilled_2k` | 50 | 158 | 153 | 50 | 0.326797 | 319 | 2.6364 | 0.137931 | 0 |

## Crossing Attribution: `sp64`

| Piece crossing-rate bucket | Piece types | Piece occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| 1.00 | 39 | 64 | 79 | 1.000000 |
| 0.70-0.99 | 0 | 0 | 0 | 0.000000 |
| 0.40-0.69 | 0 | 0 | 0 | 0.000000 |
| 0.20-0.39 | 0 | 0 | 0 | 0.000000 |
| 0.00-0.19 | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Count | Crossing occurrences | Crossed boundaries | Occurrence crossing rate | Crossing count rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `larımızdan` | 4 | 4 | 8 | 1.000000 | 2.000000 |
| `lerden` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁aldı` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁geldi` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `larımızda` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `▁altında` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `dim` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `▁Alaca` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `diler` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁birini` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁gitti` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `tim` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `um` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁dosyası` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁açtı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁Evleri` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `mizdeki` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `ğini` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `ttin` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `labilecek` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `▁Kitapları` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `lamayan` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `▁oldu` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `▁kitabı` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `▁kayboldu` | 1 | 1 | 1 | 1.000000 | 1.000000 |

## Crossing Attribution: `teacher_distilled_2k`

| Piece crossing-rate bucket | Piece types | Piece occurrences | Crossed boundaries | Share of crossed boundaries |
| --- | ---: | ---: | ---: | ---: |
| 1.00 | 25 | 42 | 48 | 0.960000 |
| 0.70-0.99 | 0 | 0 | 0 | 0.000000 |
| 0.40-0.69 | 0 | 0 | 0 | 0.000000 |
| 0.20-0.39 | 2 | 7 | 2 | 0.040000 |
| 0.00-0.19 | 0 | 0 | 0 | 0.000000 |

### Top Crossing Pieces

| Piece | Count | Crossing occurrences | Crossed boundaries | Occurrence crossing rate | Crossing count rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ları` | 5 | 5 | 5 | 1.000000 | 1.000000 |
| `▁aldı` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁geldi` | 4 | 4 | 4 | 1.000000 | 1.000000 |
| `▁altında` | 2 | 2 | 4 | 1.000000 | 2.000000 |
| `im` | 3 | 3 | 3 | 1.000000 | 1.000000 |
| `amayacakları` | 1 | 1 | 3 | 1.000000 | 3.000000 |
| `▁birini` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `um` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `sını` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `▁açtı` | 2 | 2 | 2 | 1.000000 | 1.000000 |
| `labilecek` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `lamayan` | 1 | 1 | 2 | 1.000000 | 2.000000 |
| `▁oldu` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `▁kil` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `▁kitabı` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `oldu` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `ım` | 3 | 1 | 1 | 0.333333 | 0.333333 |
| `cı` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `gi` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `dı` | 4 | 1 | 1 | 0.250000 | 0.250000 |
| `eği` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `▁Çocuğun` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `ğı` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `emeyecek` | 1 | 1 | 1 | 1.000000 | 1.000000 |
| `din` | 1 | 1 | 1 | 1.000000 | 1.000000 |

## Reading

If lambda-trained/distilled models do not reduce deployed Viterbi crossings,
the training posterior signal is not surviving projection into the serialized
Unigram model. If crossings are concentrated in high-rate pieces, inventory
work may help; diffuse medium-rate damage points toward a context-free limit.
