# v2.0 Rung-0 SP64 Morph-Compliant Path Audit

Vocab: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.vocab`

This diagnostic asks whether the existing SP64 vocabulary already has
paths that avoid high-confidence custom morphology boundaries.

If constrained paths are close to unconstrained paths, a soft training
prior may be enough. If constrained paths are much more expensive, the
vocabulary itself needs reshaping.

## Summary

| Metric | Value |
| --- | ---: |
| soft-boundary segments | 8787 |
| unconstrained crosses >=1 boundary | 8156 |
| crossing share | 0.928189 |
| avg token delta constrained-unconstrained | 1.5614 |
| median token delta | 1.0000 |
| avg score delta unconstrained-constrained | 11.9824 |
| median score delta | 10.6109 |
| avg score delta on crossed segments | 12.9094 |

## Largest Score Deltas

| Source | Line | Surface | Boundaries | Unconstrained tokens | Constrained tokens | Crossed | Score delta | Token delta |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| valid | 285 | `ORTAÖĞRETİM` | `[8, 10]` | 1 | 6 | 2 | 50.3822 | 5 |
| valid | 259 | `YAKLAŞIMI` | `[3, 6, 8]` | 1 | 6 | 3 | 45.6896 | 5 |
| valid | 285 | `YAKLAŞIMI` | `[3, 6, 8]` | 1 | 6 | 3 | 45.6896 | 5 |
| valid | 163 | `Uygulamasında` | `[5, 8, 11]` | 2 | 7 | 3 | 42.7310 | 5 |
| valid | 135 | `cumhuriyetin` | `[9, 11]` | 1 | 6 | 2 | 42.5913 | 5 |
| valid | 148 | `cumhuriyetin` | `[9, 11]` | 1 | 6 | 2 | 42.5913 | 5 |
| valid | 212 | `Federasyonu` | `[9]` | 1 | 6 | 1 | 42.1052 | 5 |
| valid | 119 | `İMPARATORLUKTAN` | `[9, 12]` | 2 | 6 | 1 | 41.9572 | 4 |
| valid | 149 | `baktığımızda` | `[6, 10]` | 1 | 6 | 2 | 41.2300 | 5 |
| valid | 287 | `ÖĞRETİM` | `[4, 6]` | 1 | 5 | 2 | 40.7205 | 4 |
| valid | 180 | `uygulamasından` | `[5, 8, 11]` | 1 | 6 | 3 | 39.8224 | 5 |
| valid | 180 | `uygulamasında` | `[5, 8, 11]` | 1 | 6 | 3 | 39.6771 | 5 |
| valid | 143 | `Restorasyonu` | `[10]` | 2 | 6 | 1 | 39.3618 | 4 |
| valid | 303 | `AÇISINDAN` | `[2, 3, 6]` | 1 | 5 | 3 | 38.2428 | 4 |
| valid | 297 | `uygulamalardaki` | `[5, 8, 11, 13]` | 1 | 6 | 4 | 38.1945 | 5 |
| valid | 297 | `uygulamalardaki` | `[5, 8, 11, 13]` | 1 | 6 | 4 | 38.1945 | 5 |
| valid | 208 | `Konvansiyonu` | `[10]` | 1 | 5 | 1 | 37.7663 | 4 |
| valid | 208 | `Konvansiyonu` | `[10]` | 1 | 5 | 1 | 37.7663 | 4 |
| valid | 281 | `YAKLAŞIM` | `[3, 6]` | 1 | 5 | 2 | 37.5170 | 4 |
| valid | 235 | `fonksiyonunu` | `[8, 10]` | 1 | 5 | 2 | 37.2450 | 4 |
| valid | 121 | `üniversitelerde` | `[8, 10, 13]` | 1 | 6 | 3 | 36.8078 | 5 |
| valid | 121 | `üniversitelerde` | `[8, 10, 13]` | 1 | 6 | 3 | 36.8078 | 5 |
| valid | 168 | `organizasyonu` | `[11]` | 1 | 5 | 1 | 36.7976 | 4 |
| valid | 199 | `yadsınamayacak` | `[3, 6, 9]` | 1 | 6 | 3 | 36.7681 | 5 |
| valid | 154 | `yapacağımız` | `[7]` | 1 | 5 | 1 | 36.6435 | 4 |
| valid | 305 | `UYARLAMA` | `[7]` | 1 | 5 | 1 | 35.4174 | 4 |
| valid | 258 | `Komisyonu` | `[7]` | 1 | 5 | 1 | 35.4004 | 4 |
| valid | 117 | `motivasyonu` | `[9]` | 1 | 5 | 1 | 35.1154 | 4 |
| valid | 201 | `mahkemesindeki` | `[4, 7, 10, 12]` | 2 | 7 | 4 | 34.7043 | 5 |
| valid | 286 | `BEKLENTİLERİ` | `[7, 8, 11]` | 1 | 5 | 3 | 34.6099 | 4 |

## Gate

Use this as a diagnostic only. It is not an eval score and not an
LLM result.
