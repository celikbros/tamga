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
| soft-boundary segments | 170 |
| unconstrained crosses >=1 boundary | 127 |
| crossing share | 0.747059 |
| avg token delta constrained-unconstrained | 1.0647 |
| median token delta | 1.0000 |
| avg score delta unconstrained-constrained | 7.0634 |
| median score delta | 5.3881 |
| avg score delta on crossed segments | 9.4549 |

## Largest Score Deltas

| Source | Line | Surface | Boundaries | Unconstrained tokens | Constrained tokens | Crossed | Score delta | Token delta |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| tr_challenge | 24 | `Çocuğun` | `[5]` | 1 | 5 | 1 | 33.3185 | 4 |
| tr_challenge | 73 | `OpenAIlaştırılmış` | `[6, 12, 14]` | 5 | 8 | 2 | 28.5494 | 3 |
| tr_challenge | 5 | `Odalarımızdakilerden` | `[3, 6, 10, 12, 14, 17]` | 4 | 9 | 4 | 25.8840 | 5 |
| tr_challenge | 4 | `Defterlerimizdekilerden` | `[6, 9, 13, 15, 17, 20]` | 3 | 7 | 5 | 24.5253 | 4 |
| tr_challenge | 7 | `Sorularımızdakilerden` | `[4, 7, 11, 13, 15, 18]` | 4 | 8 | 4 | 23.8127 | 4 |
| tr_challenge | 76 | `okudum` | `[3, 5]` | 1 | 4 | 2 | 22.2584 | 3 |
| tr_challenge | 1 | `Arabacılarımızdakilerden` | `[7, 10, 14, 16, 18, 21]` | 5 | 9 | 3 | 22.2415 | 4 |
| tr_challenge | 8 | `Kayıtlarımızdakilerden` | `[5, 8, 12, 14, 16, 19]` | 4 | 8 | 3 | 22.2415 | 4 |
| tr_challenge | 53 | `Seçilebileceklerden` | `[9, 13, 16]` | 3 | 6 | 2 | 21.7201 | 3 |
| tr_challenge | 35 | `kitabı` | `[5]` | 1 | 4 | 1 | 20.7464 | 3 |
| tr_challenge | 47 | `biliyoruz` | `[7]` | 1 | 3 | 1 | 20.5289 | 2 |
| tr_challenge | 6 | `çıkardıklarımız` | `[8, 11]` | 2 | 5 | 2 | 20.1985 | 3 |
| tr_challenge | 11 | `kitabımı` | `[5, 7]` | 2 | 5 | 2 | 20.1430 | 3 |
| tr_challenge | 2 | `Evlerinizdekilerden` | `[2, 5, 7, 9, 11, 13, 16]` | 4 | 8 | 5 | 19.2947 | 4 |
| tr_challenge | 3 | `Kitapçılarımızdan` | `[7, 10, 14]` | 3 | 6 | 2 | 17.6367 | 3 |
| tr_challenge | 6 | `Çantalarımızdan` | `[3, 5, 8, 12]` | 3 | 6 | 2 | 17.6367 | 3 |
| tr_challenge | 9 | `Dosyalarımızdan` | `[5, 8, 12]` | 2 | 5 | 2 | 17.6367 | 3 |
| tr_challenge | 20 | `kırılmıştı` | `[5, 8]` | 2 | 4 | 1 | 16.8617 | 2 |
| tr_challenge | 42 | `Çıktık` | `[3, 5]` | 2 | 4 | 1 | 16.5064 | 2 |
| tr_challenge | 30 | `kayboldu` | `[6]` | 1 | 3 | 1 | 15.5383 | 2 |

## Gate

Use this as a diagnostic only. It is not an eval score and not an
LLM result.
