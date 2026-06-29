# v2.0 Finite Protected Reference Intrinsic Eval

Reference model: `partial_boundary_rho025_unigram_64000`
Reference path: `artifacts/private/v2_0_partial_boundary_sp/partial_boundary_rho025_unigram_64000.model`
Selected protected pieces: `artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv`

This is an intrinsic prototype, not a final tokenizer. Normal text uses
the supplied SentencePiece reference model. Protected spans use finite selected
pieces with UTF-8 byte fallback. Boundary scoring uses logical protected
span tokens; model token counts include finite protected pieces.

## Gold Expanded

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 50 | 6.6400 | 6.6400 | 2.7438 | 1.0000 | 50/50 | 0.000000 |  |
| partial_boundary_rho025_unigram_64000 | ok | 50 | 6.0000 | 6.0000 | 2.4793 | 0.7406 | 1/50 | 0.000000 |  |
| finite_protected_partial_boundary_rho025 | ok | 50 | 5.8000 | 6.2000 | 2.5620 | 0.7165 | 1/50 | 0.000000 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | partial_boundary_rho025_unigram_64000 | finite_protected_partial_boundary_rho025 |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.6914 | 0.5070 |
| informal | 1.0000 | 0.7222 | 0.7222 |
| negative_word | 1.0000 | 0.8980 | 0.8980 |
| proper_name | 1.0000 | 0.9000 | 0.9000 |
| question | 1.0000 | 0.7925 | 0.7925 |
| softening | 1.0000 | 0.5970 | 0.5970 |
| suffix_chain | 1.0000 | 0.6588 | 0.6588 |
| verb_future | 1.0000 | 0.6829 | 0.6829 |
| verb_past | 1.0000 | 0.7500 | 0.7500 |

## Challenge

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 108 | 7.7130 | 7.7130 | 2.1749 | 0.9220 | 44/108 | 0.000000 |  |
| partial_boundary_rho025_unigram_64000 | ok | 108 | 7.7500 | 7.7500 | 2.1854 | 0.7380 | 0/108 | 0.000000 |  |
| finite_protected_partial_boundary_rho025 | ok | 108 | 7.4259 | 8.0926 | 2.2820 | 0.6782 | 0/108 | 0.092308 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | partial_boundary_rho025_unigram_64000 | finite_protected_partial_boundary_rho025 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.8298 | 0.8298 |
| code_mixed | 0.9315 | 0.6310 | 0.4730 |
| informal | 0.8649 | 0.7586 | 0.7586 |
| negative_word | 0.8317 | 0.8350 | 0.8350 |
| numbers_dates | 0.9649 | 0.6949 | 0.2703 |
| proper_name | 1.0000 | 0.8267 | 0.8267 |
| punctuation | 0.9921 | 0.7121 | 0.7188 |
| question | 0.9500 | 0.8235 | 0.7652 |
| softening | 0.8906 | 0.6719 | 0.6562 |
| suffix_chain | 0.8958 | 0.6322 | 0.6092 |
| verb_future | 0.8246 | 0.7000 | 0.7000 |
| verb_past | 0.9554 | 0.8322 | 0.7651 |

## Multilingual Smoke

| Model | Status | Examples | Avg logical tokens/example | Avg model tokens/example | Avg model tokens/word | Boundary F1 | Exact match | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 20 | 7.3000 | 7.3000 | 2.0000 | 0.9551 | 17/20 | 0.000000 |  |
| partial_boundary_rho025_unigram_64000 | ok | 20 | 22.1500 | 22.1500 | 6.0685 | 0.4391 | 0/20 | 0.000000 |  |
| finite_protected_partial_boundary_rho025 | ok | 20 | 13.6500 | 38.8500 | 10.6438 | 0.2903 | 0/20 | 0.738516 | finite protected pieces + normal SP64 |

### Category F1

| Category | custom_tr_morph | partial_boundary_rho025_unigram_64000 | finite_protected_partial_boundary_rho025 |
| --- | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2778 | 0.3750 |
| azerbaijani | 0.8571 | 0.5882 | 0.2326 |
| french | 1.0000 | 0.4865 | 0.2857 |
| german | 1.0000 | 0.5641 | 0.3158 |
| greek | 1.0000 | 0.2857 | 0.1429 |
| italian | 1.0000 | 0.4211 | 0.1538 |
| kazakh_cyrillic | 1.0000 | 0.3371 | 0.2553 |
| kyrgyz_cyrillic | 1.0000 | 0.5000 | 0.3333 |
| multilingual_mixed | 0.6250 | 0.5000 | 0.2857 |
| russian | 1.0000 | 0.3556 | 0.3077 |
| spanish | 1.0000 | 0.5217 | 0.4211 |
| tatar_cyrillic | 1.0000 | 0.4815 | 0.3684 |
| uzbek_latin | 1.0000 | 0.4444 | 0.2424 |

## Protected Span Stress

| Model | Status | Examples | Protected preserved | Break rate | Avg model tokens/example | Protected byte-token rate | Notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 34 | 25/25 | 0.0000 | 7.2647 | 0.000000 |  |
| partial_boundary_rho025_unigram_64000 | ok | 34 | 1/25 | 0.9600 | 16.0000 | 0.000000 |  |
| finite_protected_partial_boundary_rho025 | ok | 34 | 25/25 | 0.0000 | 25.5000 | 0.489871 |  |

## Gate

This prototype is worth further work only if it preserves protected
spans and improves visible boundary behavior without hiding protected
token pressure.
