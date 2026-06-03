# v2.0 Finite Protected Soft-Marker Intrinsic Eval

Soft-marker model: `artifacts/private/v2_0_candidate_sentencepiece/protected_hard_soft_marker_raw_sp64_unigram_64000.model`
SP64 reference: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This is an intrinsic prototype, not a final tokenizer. Normal text uses
the train-only soft-marker model. Protected spans use finite selected
pieces with UTF-8 byte fallback. Boundary scoring uses logical protected
span tokens; model token counts include finite protected pieces.

## Gold Expanded

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 6.6400 | 2.7438 | 1.0000 | 50/50 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 50 | 6.0600 | 6.0600 | 2.5041 | 0.7551 | 1/50 | 0.000000 |  |
| finite_protected_soft_marker | ok | 50 | 7.4400 | 10.9000 | 4.5041 | 0.9040 | 25/50 | 0.000000 | finite protected pieces + soft-marker model |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_soft_marker |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6829 | 0.7949 |
| informal | 1.0000 | 0.7222 | 0.7143 |
| negative_word | 1.0000 | 0.8980 | 0.9804 |
| proper_name | 1.0000 | 0.9000 | 0.8989 |
| question | 1.0000 | 0.8000 | 0.8955 |
| softening | 1.0000 | 0.6087 | 0.9487 |
| suffix_chain | 1.0000 | 0.6988 | 0.9714 |
| verb_future | 1.0000 | 0.7143 | 0.9200 |
| verb_past | 1.0000 | 0.8205 | 0.9545 |

## Challenge

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 7.7130 | 2.1749 | 0.9220 | 44/108 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 108 | 7.8056 | 7.8056 | 2.2010 | 0.7351 | 0/108 | 0.000000 |  |
| finite_protected_soft_marker | ok | 108 | 9.0556 | 12.6667 | 3.5718 | 0.8259 | 17/108 | 0.000000 | finite protected pieces + soft-marker model |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_soft_marker |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8041 | 0.7885 |
| code_mixed | 0.9315 | 0.6310 | 0.7470 |
| informal | 0.8649 | 0.7586 | 0.7556 |
| negative_word | 0.8317 | 0.8269 | 0.8750 |
| numbers_dates | 0.9649 | 0.7119 | 0.9573 |
| proper_name | 1.0000 | 0.8133 | 0.8686 |
| punctuation | 0.9921 | 0.7121 | 0.6715 |
| question | 0.9500 | 0.8333 | 0.8613 |
| softening | 0.8906 | 0.6769 | 0.7857 |
| suffix_chain | 0.8958 | 0.6272 | 0.9118 |
| verb_future | 0.8246 | 0.6942 | 0.7883 |
| verb_past | 0.9554 | 0.8158 | 0.8537 |

## Multilingual Smoke

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 7.3000 | 2.0000 | 0.9551 | 17/20 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 20 | 22.0000 | 22.0000 | 6.0274 | 0.4341 | 0/20 | 0.000000 |  |
| finite_protected_soft_marker | ok | 20 | 8.6500 | 34.1000 | 9.3425 | 0.8015 | 9/20 | 0.738516 | finite protected pieces + soft-marker model |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_soft_marker |
| --- | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 1.0000 |
| azerbaijani | 0.8571 | 0.5882 | 0.7895 |
| french | 1.0000 | 0.4865 | 0.9474 |
| german | 1.0000 | 0.5641 | 0.5000 |
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
| finite_protected_soft_marker | ok | 34 | 25/25 | 0.0000 | 24.7647 | 0.440678 |  |

## Gate

This prototype is worth tiny-LM screening only if it preserves protected
spans and materially beats SP64 on visible challenge boundary F1 without
returning to pure-custom token pressure.
