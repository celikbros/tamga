# v2.0 Soft Morph Seed Vocabulary Analysis

Seed vocab: `artifacts/private/v2_0_soft_morph/soft_morph_seed_vocab.train.tsv`

This report summarizes the private seed vocabulary without listing raw
corpus tokens. It is used to decide how much of the custom morphology
piece inventory should be seeded into a learned tokenizer.

## Inventory Summary

| Metric | Value |
| --- | ---: |
| unique seed tokens | 218981 |
| total seed token count | 3882002 |

## Coverage By Vocabulary Cap

| Cap | Unique kept | Covered token count | Uncovered token count | Coverage |
| ---: | ---: | ---: | ---: | ---: |
| 1000 | 1000 | 2528515 | 1353487 | 0.651343 |
| 4000 | 4000 | 3022976 | 859026 | 0.778716 |
| 8000 | 8000 | 3240660 | 641342 | 0.834791 |
| 16000 | 16000 | 3426416 | 455586 | 0.882641 |
| 32000 | 32000 | 3578602 | 303400 | 0.921844 |
| 64000 | 64000 | 3701258 | 180744 | 0.953441 |
| 128000 | 128000 | 3791021 | 90981 | 0.976563 |

## Category Summary

| Category | Unique tokens | Token count | Share |
| --- | ---: | ---: | ---: |
| other | 100 | 584 | 0.000150 |
| punct_or_symbol | 152 | 430085 | 0.110789 |
| suffix | 244 | 925856 | 0.238500 |
| word_start | 218485 | 2525477 | 0.650560 |

## Category Coverage At Cap 64000

| Category | Unique kept | Covered token count | Covered share of all tokens |
| --- | ---: | ---: | ---: |
| other | 28 | 502 | 0.000129 |
| punct_or_symbol | 102 | 430014 | 0.110771 |
| suffix | 203 | 925808 | 0.238487 |
| word_start | 63667 | 2344934 | 0.604053 |

## Decision Hint

If a 64k seed cap already covers most seed-token occurrences, then the
remaining pressure is mostly from rare surface pieces and whitespace
serialization. If coverage is low, the learned-vocab path must either
seed fewer morphology pieces and rely on merges, or increase the vocab
budget before tiny-LM comparison.
