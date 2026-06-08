# v2.0 Marker-Stripped Soft-Marker Diagnostic

Soft-marker model: `artifacts/private/v2_0_candidate_sentencepiece/protected_hard_train_only_suffix_chain2_unigram_64000.model`
SP64 reference: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`
Max lines per split: `all`

This diagnostic uses the all-soft-marker-trained Unigram model but does
not insert morphology markers into normal text at encode time. Protected
spans still use the finite protected encoder.

## Marker-Stripped Token Pressure

| Split | Lines | Bytes | Words | Model tokens | Model tokens/byte | Model tokens/word | Protected piece tokens | Protected byte tokens | Protected byte-token rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 2603245 | 4120697 | 0.180575 | 1.5829 | 507327 | 1597 | 0.003138 |
| valid | 1994 | 2843294 | 324001 | 522594 | 0.183799 | 1.6129 | 63317 | 194 | 0.003055 |
| test | 1998 | 2781995 | 316406 | 513608 | 0.184619 | 1.6233 | 64103 | 249 | 0.003869 |

## Gold Expanded

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 6.6400 | 2.7438 | 1.0000 | 50/50 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 50 | 6.0600 | 6.0600 | 2.5041 | 0.7551 | 1/50 | 0.000000 |  |
| finite_protected_marker_stripped | ok | 50 | 6.7400 | 7.3400 | 3.0331 | 0.8190 | 1/50 | 0.000000 | soft-marker model, markers stripped at encode time |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_marker_stripped |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6829 | 0.7042 |
| informal | 1.0000 | 0.7222 | 0.6667 |
| negative_word | 1.0000 | 0.8980 | 0.9167 |
| proper_name | 1.0000 | 0.9000 | 0.8333 |
| question | 1.0000 | 0.8000 | 0.8065 |
| softening | 1.0000 | 0.6087 | 0.7397 |
| suffix_chain | 1.0000 | 0.6988 | 0.9200 |
| verb_future | 1.0000 | 0.7143 | 0.8333 |
| verb_past | 1.0000 | 0.8205 | 0.9091 |

## Challenge

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 7.7130 | 2.1749 | 0.9220 | 44/108 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 108 | 7.8056 | 7.8056 | 2.2010 | 0.7351 | 0/108 | 0.000000 |  |
| finite_protected_marker_stripped | ok | 108 | 8.1759 | 9.2685 | 2.6136 | 0.7632 | 0/108 | 0.000000 | soft-marker model, markers stripped at encode time |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_marker_stripped |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8041 | 0.7368 |
| code_mixed | 0.9315 | 0.6310 | 0.6194 |
| informal | 0.8649 | 0.7586 | 0.7045 |
| negative_word | 0.8317 | 0.8269 | 0.8868 |
| numbers_dates | 0.9649 | 0.7119 | 0.8727 |
| proper_name | 1.0000 | 0.8133 | 0.7750 |
| punctuation | 0.9921 | 0.7121 | 0.7121 |
| question | 0.9500 | 0.8333 | 0.8031 |
| softening | 0.8906 | 0.6769 | 0.6667 |
| suffix_chain | 0.8958 | 0.6272 | 0.8163 |
| verb_future | 0.8246 | 0.6942 | 0.7231 |
| verb_past | 0.9554 | 0.8158 | 0.8442 |

## Multilingual Smoke

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 7.3000 | 2.0000 | 0.9551 | 17/20 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 20 | 22.0000 | 22.0000 | 6.0274 | 0.4341 | 0/20 | 0.000000 |  |
| finite_protected_marker_stripped | ok | 20 | 8.8000 | 34.0000 | 9.3151 | 0.7855 | 9/20 | 0.738516 | soft-marker model, markers stripped at encode time |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_marker_stripped |
| --- | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 1.0000 |
| azerbaijani | 0.8571 | 0.5882 | 0.8108 |
| french | 1.0000 | 0.4865 | 0.9474 |
| german | 1.0000 | 0.5641 | 0.3889 |
| greek | 1.0000 | 0.2857 | 1.0000 |
| italian | 1.0000 | 0.4211 | 0.6000 |
| kazakh_cyrillic | 1.0000 | 0.3182 | 0.7742 |
| kyrgyz_cyrillic | 1.0000 | 0.5000 | 1.0000 |
| multilingual_mixed | 0.6250 | 0.5000 | 0.7778 |
| russian | 1.0000 | 0.3182 | 0.5556 |
| spanish | 1.0000 | 0.5455 | 1.0000 |
| tatar_cyrillic | 1.0000 | 0.4815 | 1.0000 |
| uzbek_latin | 1.0000 | 0.4444 | 0.7692 |

## Protected Span Stress

| Model | Status | Examples | Protected preserved | Break rate | Avg model tokens/example | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 34 | 25/25 | 0.0000 | 7.2647 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 34 | 1/25 | 0.9600 | 15.9706 | 0.000000 |  |
| finite_protected_marker_stripped | ok | 34 | 25/25 | 0.0000 | 23.5882 | 0.440678 |  |

## Gate

If marker-stripped token pressure drops near SP64 while F1 stays above
SP64, prefer train-only vocab shaping over in-stream markers. If F1
collapses, selective in-stream markers remain the next lever.
