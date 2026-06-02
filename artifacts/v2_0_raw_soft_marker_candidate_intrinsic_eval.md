# v2.0 Raw-Soft-Marker Candidate Intrinsic Eval

Candidate model: `artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model`
SP64 reference: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`

This is an intrinsic visible-set diagnostic. It is not hidden eval and
not an LLM result. Candidate boundary F1 is marker-aware: private-use
soft markers inside SentencePiece pieces are interpreted as morphology
boundary hints for this diagnostic.
The protected-aware row is an upper-bound diagnostic, not a final
finite-vocabulary design.

## Gold Expanded

| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_unigram_64000_train_only | ok | 50 | 6.0600 | 2.5041 | 0.7551 | 1/50 |  |
| protected_hard_soft_marker_raw_sp64 | ok | 50 | 7.8600 | 3.2479 | 0.7808 | 18/50 | marker-aware boundary diagnostic |
| protected_aware_soft_marker_sp64 | ok | 50 | 7.4400 | 3.0744 | 0.9040 | 25/50 | protected-aware marker diagnostic |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | protected_hard_soft_marker_raw_sp64 | protected_aware_soft_marker_sp64 |
| --- | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6829 | 0.5870 | 0.7949 |
| informal | 1.0000 | 0.7222 | 0.7143 | 0.7143 |
| negative_word | 1.0000 | 0.8980 | 0.9804 | 0.9804 |
| proper_name | 1.0000 | 0.9000 | 0.4000 | 0.8989 |
| question | 1.0000 | 0.8000 | 0.7647 | 0.8955 |
| softening | 1.0000 | 0.6087 | 0.9487 | 0.9487 |
| suffix_chain | 1.0000 | 0.6988 | 0.9714 | 0.9714 |
| verb_future | 1.0000 | 0.7143 | 0.9200 | 0.9200 |
| verb_past | 1.0000 | 0.8205 | 0.9545 | 0.9545 |

## Challenge

| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| sp_unigram_64000_train_only | ok | 108 | 7.8056 | 2.2010 | 0.7351 | 0/108 |  |
| protected_hard_soft_marker_raw_sp64 | ok | 108 | 9.7222 | 2.7415 | 0.6724 | 7/108 | marker-aware boundary diagnostic |
| protected_aware_soft_marker_sp64 | ok | 108 | 9.0556 | 2.5535 | 0.8259 | 17/108 | protected-aware marker diagnostic |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | protected_hard_soft_marker_raw_sp64 | protected_aware_soft_marker_sp64 |
| --- | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8041 | 0.7885 | 0.7885 |
| code_mixed | 0.9315 | 0.6310 | 0.4583 | 0.7470 |
| informal | 0.8649 | 0.7586 | 0.7556 | 0.7556 |
| negative_word | 0.8317 | 0.8269 | 0.8750 | 0.8750 |
| numbers_dates | 0.9649 | 0.7119 | 0.4964 | 0.9573 |
| proper_name | 1.0000 | 0.8133 | 0.3169 | 0.8686 |
| punctuation | 0.9921 | 0.7121 | 0.5479 | 0.6715 |
| question | 0.9500 | 0.8333 | 0.6438 | 0.8613 |
| softening | 0.8906 | 0.6769 | 0.7857 | 0.7857 |
| suffix_chain | 0.8958 | 0.6272 | 0.9118 | 0.9118 |
| verb_future | 0.8246 | 0.6942 | 0.7883 | 0.7883 |
| verb_past | 0.9554 | 0.8158 | 0.8537 | 0.8537 |

## Multilingual Smoke

| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 2.0000 | 0.9551 | 17/20 |  |
| sp_unigram_64000_train_only | ok | 20 | 22.0000 | 6.0274 | 0.4341 | 0/20 |  |
| protected_hard_soft_marker_raw_sp64 | ok | 20 | 21.7000 | 5.9452 | 0.3640 | 0/20 | marker-aware boundary diagnostic |
| protected_aware_soft_marker_sp64 | ok | 20 | 8.6500 | 2.3699 | 0.8015 | 9/20 | protected-aware marker diagnostic |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | protected_hard_soft_marker_raw_sp64 | protected_aware_soft_marker_sp64 |
| --- | ---: | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 0.2222 | 1.0000 |
| azerbaijani | 0.8571 | 0.5882 | 0.4528 | 0.7895 |
| french | 1.0000 | 0.4865 | 0.4444 | 0.9474 |
| german | 1.0000 | 0.5641 | 0.5143 | 0.5000 |
| greek | 1.0000 | 0.2857 | 0.2857 | 1.0000 |
| italian | 1.0000 | 0.4211 | 0.3750 | 0.6000 |
| kazakh_cyrillic | 1.0000 | 0.3182 | 0.2921 | 0.7742 |
| kyrgyz_cyrillic | 1.0000 | 0.5000 | 0.4583 | 1.0000 |
| multilingual_mixed | 0.6250 | 0.5000 | 0.2222 | 0.7778 |
| russian | 1.0000 | 0.3182 | 0.2667 | 0.5556 |
| spanish | 1.0000 | 0.5455 | 0.2727 | 1.0000 |
| tatar_cyrillic | 1.0000 | 0.4815 | 0.4074 | 1.0000 |
| uzbek_latin | 1.0000 | 0.4444 | 0.4545 | 0.7692 |

## Protected Span Stress

| Model | Status | Examples | Protected preserved | Break rate | Avg tokens/example | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 34 | 25/25 | 0.0000 | 7.2647 |  |
| sp_unigram_64000_train_only | ok | 34 | 1/25 | 0.9600 | 15.9706 |  |
| protected_hard_soft_marker_raw_sp64 | ok | 34 | 1/25 | 0.9600 | 16.1765 |  |
| protected_aware_soft_marker_sp64 | ok | 34 | 25/25 | 0.0000 | 8.2941 |  |

## Gate

Proceed to tiny-LM only if token pressure, protected spans, and visible
boundary diagnostics are all acceptable. A compression pass alone is
not enough.
