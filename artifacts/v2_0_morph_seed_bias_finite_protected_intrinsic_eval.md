# v2.0 Finite Protected SP64 Intrinsic Eval

SP64 reference: `artifacts/private/v2_0_morph_seed_vocab/morph_seed_bias_unigram_64000.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This is an intrinsic prototype, not a final tokenizer. Normal text uses
the train-only SP64 Unigram model. Protected spans use finite selected
pieces with UTF-8 byte fallback. Boundary scoring uses logical protected
span tokens; model token counts include finite protected pieces.

## Gold Expanded

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 6.6400 | 2.7438 | 1.0000 | 50/50 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 50 | 6.0600 | 6.0600 | 2.5041 | 0.7551 | 1/50 | 0.000000 |  |
| finite_protected_sp64 | ok | 50 | 6.0200 | 6.4200 | 2.6529 | 0.7317 | 1/50 | 0.000000 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_sp64 |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6829 | 0.6857 |
| informal | 1.0000 | 0.7222 | 0.6667 |
| negative_word | 1.0000 | 0.8980 | 0.8980 |
| proper_name | 1.0000 | 0.9000 | 0.8148 |
| question | 1.0000 | 0.8000 | 0.7333 |
| softening | 1.0000 | 0.6087 | 0.6087 |
| suffix_chain | 1.0000 | 0.6988 | 0.6988 |
| verb_future | 1.0000 | 0.7143 | 0.6977 |
| verb_past | 1.0000 | 0.8205 | 0.8205 |

## Challenge

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 7.7130 | 2.1749 | 0.9220 | 44/108 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 108 | 7.8056 | 7.8056 | 2.2010 | 0.7351 | 0/108 | 0.000000 |  |
| finite_protected_sp64 | ok | 108 | 7.7500 | 8.5370 | 2.4073 | 0.6913 | 0/108 | 0.000000 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_sp64 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8041 | 0.7835 |
| code_mixed | 0.9315 | 0.6310 | 0.5906 |
| informal | 0.8649 | 0.7586 | 0.7416 |
| negative_word | 0.8317 | 0.8269 | 0.8269 |
| numbers_dates | 0.9649 | 0.7119 | 0.7963 |
| proper_name | 1.0000 | 0.8133 | 0.7059 |
| punctuation | 0.9921 | 0.7121 | 0.6569 |
| question | 0.9500 | 0.8333 | 0.7143 |
| softening | 0.8906 | 0.6769 | 0.6615 |
| suffix_chain | 0.8958 | 0.6272 | 0.6036 |
| verb_future | 0.8246 | 0.6942 | 0.6774 |
| verb_past | 0.9554 | 0.8158 | 0.6667 |

## Multilingual Smoke

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 7.3000 | 2.0000 | 0.9551 | 17/20 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 20 | 22.0000 | 22.0000 | 6.0274 | 0.4341 | 0/20 | 0.000000 |  |
| finite_protected_sp64 | ok | 20 | 9.9000 | 35.1000 | 9.6164 | 0.5185 | 5/20 | 0.738516 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_sp64 |
| --- | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 1.0000 |
| azerbaijani | 0.8571 | 0.5882 | 0.3500 |
| french | 1.0000 | 0.4865 | 0.9000 |
| german | 1.0000 | 0.5641 | 0.4444 |
| greek | 1.0000 | 0.2857 | 1.0000 |
| italian | 1.0000 | 0.4211 | 0.6000 |
| kazakh_cyrillic | 1.0000 | 0.3182 | 0.3529 |
| kyrgyz_cyrillic | 1.0000 | 0.5000 | 0.4828 |
| multilingual_mixed | 0.6250 | 0.5000 | 0.7368 |
| russian | 1.0000 | 0.3182 | 0.3333 |
| spanish | 1.0000 | 0.5455 | 1.0000 |
| tatar_cyrillic | 1.0000 | 0.4815 | 0.3750 |
| uzbek_latin | 1.0000 | 0.4444 | 0.4138 |

## Protected Span Stress

| Model | Status | Examples | Protected preserved | Break rate | Avg model tokens/example | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 34 | 25/25 | 0.0000 | 7.2647 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 34 | 1/25 | 0.9600 | 15.9706 | 0.000000 |  |
| finite_protected_sp64 | ok | 34 | 25/25 | 0.0000 | 24.0588 | 0.440678 |  |

## Gate

This prototype is worth further work only if it preserves protected
spans and improves visible boundary behavior without hiding protected
token pressure.
