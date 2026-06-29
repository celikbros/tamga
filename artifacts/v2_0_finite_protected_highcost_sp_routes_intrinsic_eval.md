# v2.0 Finite Protected Reference Intrinsic Eval

Reference model: `sp_unigram_64000_train_only`
Reference path: `artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This is an intrinsic prototype, not a final tokenizer. Normal text uses
the supplied SentencePiece reference model. Protected spans use finite selected
pieces with UTF-8 byte fallback. Boundary scoring uses logical protected
span tokens; model token counts include finite protected pieces.

## Gold Expanded

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 6.6400 | 2.7438 | 1.0000 | 50/50 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 50 | 6.0600 | 6.0600 | 2.5041 | 0.7551 | 1/50 | 0.000000 |  |
| finite_protected_sp64_highcost_sp_routes | ok | 50 | 5.8600 | 6.0600 | 2.5041 | 0.7314 | 1/50 | 0.000000 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_sp64_highcost_sp_routes |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6829 | 0.5000 |
| informal | 1.0000 | 0.7222 | 0.7222 |
| negative_word | 1.0000 | 0.8980 | 0.8980 |
| proper_name | 1.0000 | 0.9000 | 0.9000 |
| question | 1.0000 | 0.8000 | 0.8000 |
| softening | 1.0000 | 0.6087 | 0.6087 |
| suffix_chain | 1.0000 | 0.6988 | 0.6988 |
| verb_future | 1.0000 | 0.7143 | 0.7143 |
| verb_past | 1.0000 | 0.8205 | 0.8205 |

## Challenge

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 7.7130 | 2.1749 | 0.9220 | 44/108 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 108 | 7.8056 | 7.8056 | 2.2010 | 0.7351 | 0/108 | 0.000000 |  |
| finite_protected_sp64_highcost_sp_routes | ok | 108 | 7.4815 | 7.8426 | 2.2115 | 0.6755 | 0/108 | 1.000000 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_sp64_highcost_sp_routes |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8041 | 0.7835 |
| code_mixed | 0.9315 | 0.6310 | 0.5000 |
| informal | 0.8649 | 0.7586 | 0.7586 |
| negative_word | 0.8317 | 0.8269 | 0.8269 |
| numbers_dates | 0.9649 | 0.7119 | 0.2703 |
| proper_name | 1.0000 | 0.8133 | 0.8133 |
| punctuation | 0.9921 | 0.7121 | 0.7188 |
| question | 0.9500 | 0.8333 | 0.7759 |
| softening | 0.8906 | 0.6769 | 0.6615 |
| suffix_chain | 0.8958 | 0.6272 | 0.6036 |
| verb_future | 0.8246 | 0.6942 | 0.6942 |
| verb_past | 0.9554 | 0.8158 | 0.7500 |

## Multilingual Smoke

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 7.3000 | 2.0000 | 0.9551 | 17/20 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 20 | 22.0000 | 22.0000 | 6.0274 | 0.4341 | 0/20 | 0.000000 |  |
| finite_protected_sp64_highcost_sp_routes | ok | 20 | 13.5500 | 35.4500 | 9.7123 | 0.2865 | 0/20 | 0.858974 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | sp_unigram_64000_train_only | finite_protected_sp64_highcost_sp_routes |
| --- | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 0.3750 |
| azerbaijani | 0.8571 | 0.5882 | 0.2326 |
| french | 1.0000 | 0.4865 | 0.2857 |
| german | 1.0000 | 0.5641 | 0.3158 |
| greek | 1.0000 | 0.2857 | 0.1429 |
| italian | 1.0000 | 0.4211 | 0.1538 |
| kazakh_cyrillic | 1.0000 | 0.3182 | 0.2609 |
| kyrgyz_cyrillic | 1.0000 | 0.5000 | 0.3333 |
| multilingual_mixed | 0.6250 | 0.5000 | 0.2857 |
| russian | 1.0000 | 0.3182 | 0.2400 |
| spanish | 1.0000 | 0.5455 | 0.4211 |
| tatar_cyrillic | 1.0000 | 0.4815 | 0.3684 |
| uzbek_latin | 1.0000 | 0.4444 | 0.2424 |

## Protected Span Stress

| Model | Status | Examples | Protected preserved | Break rate | Avg model tokens/example | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 34 | 25/25 | 0.0000 | 7.2647 | 0.000000 |  |
| sp_unigram_64000_train_only | ok | 34 | 1/25 | 0.9600 | 15.9706 | 0.000000 |  |
| finite_protected_sp64_highcost_sp_routes | ok | 34 | 25/25 | 0.0000 | 22.2647 | 0.647815 |  |

## Gate

This prototype is worth further work only if it preserves protected
spans and improves visible boundary behavior without hiding protected
token pressure.
