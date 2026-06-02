# v2.0 Raw-Hard Candidate Intrinsic Eval

Candidate model: `artifacts/private/v2_0_candidate_sentencepiece/protected_hard_raw_sp64_unigram_64000.model`
SP64 reference: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`

This is an intrinsic visible-set diagnostic. It is not hidden eval and
not an LLM result.

## Gold Expanded

| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| sp_unigram_64000_train_only | ok | 50 | 6.0600 | 2.5041 | 0.7551 | 1/50 |  |
| protected_hard_raw_sp64 | ok | 50 | 6.4200 | 2.6529 | 0.5931 | 1/50 |  |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | protected_hard_raw_sp64 |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6829 | 0.3765 |
| informal | 1.0000 | 0.7222 | 0.6154 |
| negative_word | 1.0000 | 0.8980 | 0.9167 |
| proper_name | 1.0000 | 0.9000 | 0.3953 |
| question | 1.0000 | 0.8000 | 0.6000 |
| softening | 1.0000 | 0.6087 | 0.6269 |
| suffix_chain | 1.0000 | 0.6988 | 0.6988 |
| verb_future | 1.0000 | 0.7143 | 0.6364 |
| verb_past | 1.0000 | 0.8205 | 0.7317 |

## Challenge

| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| sp_unigram_64000_train_only | ok | 108 | 7.8056 | 2.2010 | 0.7351 | 0/108 |  |
| protected_hard_raw_sp64 | ok | 108 | 8.2222 | 2.3185 | 0.5951 | 0/108 |  |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | protected_hard_raw_sp64 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8041 | 0.7097 |
| code_mixed | 0.9315 | 0.6310 | 0.3864 |
| informal | 0.8649 | 0.7586 | 0.7045 |
| negative_word | 0.8317 | 0.8269 | 0.8738 |
| numbers_dates | 0.9649 | 0.7119 | 0.4375 |
| proper_name | 1.0000 | 0.8133 | 0.3270 |
| punctuation | 0.9921 | 0.7121 | 0.6331 |
| question | 0.9500 | 0.8333 | 0.5606 |
| softening | 0.8906 | 0.6769 | 0.6769 |
| suffix_chain | 0.8958 | 0.6272 | 0.6235 |
| verb_future | 0.8246 | 0.6942 | 0.6508 |
| verb_past | 0.9554 | 0.8158 | 0.7785 |

## Multilingual Smoke

| Model | Status | Examples | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 2.0000 | 0.9551 | 17/20 |  |
| sp_unigram_64000_train_only | ok | 20 | 22.0000 | 6.0274 | 0.4341 | 0/20 |  |
| protected_hard_raw_sp64 | ok | 20 | 22.0500 | 6.0411 | 0.3444 | 0/20 |  |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | protected_hard_raw_sp64 |
| --- | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 0.2222 |
| azerbaijani | 0.8571 | 0.5882 | 0.4615 |
| french | 1.0000 | 0.4865 | 0.2564 |
| german | 1.0000 | 0.5641 | 0.2632 |
| greek | 1.0000 | 0.2857 | 0.2857 |
| italian | 1.0000 | 0.4211 | 0.3158 |
| kazakh_cyrillic | 1.0000 | 0.3182 | 0.2921 |
| kyrgyz_cyrillic | 1.0000 | 0.5000 | 0.4583 |
| multilingual_mixed | 0.6250 | 0.5000 | 0.2222 |
| russian | 1.0000 | 0.3182 | 0.2609 |
| spanish | 1.0000 | 0.5455 | 0.6000 |
| tatar_cyrillic | 1.0000 | 0.4815 | 0.4074 |
| uzbek_latin | 1.0000 | 0.4444 | 0.4545 |

## Protected Span Stress

| Model | Status | Examples | Protected preserved | Break rate | Avg tokens/example | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 34 | 25/25 | 0.0000 | 7.2647 |  |
| sp_unigram_64000_train_only | ok | 34 | 1/25 | 0.9600 | 15.9706 |  |
| protected_hard_raw_sp64 | ok | 34 | 1/25 | 0.9600 | 16.2353 |  |

## Gate

Proceed to tiny-LM only if token pressure, protected spans, and visible
boundary diagnostics are all acceptable. A compression pass alone is
not enough.
