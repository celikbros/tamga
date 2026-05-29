# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| unicode_char | ok | 18.1600 | 7.5041 | 0.4947 | 0/50 |  |
| toy_bpe_1000 | ok | 6.6400 | 2.7438 | 0.6277 | 1/50 |  |
| sp_bpe | ok | 6.6000 | 2.7273 | 0.6263 | 1/50 |  |
| sp_unigram | ok | 7.4400 | 3.0744 | 0.6325 | 0/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | toy_bpe_1000 F1 | sp_bpe F1 | sp_unigram F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.4768 | 0.6866 | 0.6667 | 0.5882 |
| informal | 1.0000 | 0.4478 | 0.7200 | 0.7200 | 0.5882 |
| negative_word | 1.0000 | 0.4167 | 0.7143 | 0.7407 | 0.7333 |
| proper_name | 1.0000 | 0.5087 | 0.6139 | 0.6535 | 0.6600 |
| question | 1.0000 | 0.5455 | 0.7541 | 0.7333 | 0.7667 |
| softening | 1.0000 | 0.5248 | 0.6000 | 0.5915 | 0.5333 |
| suffix_chain | 1.0000 | 0.4951 | 0.5176 | 0.5057 | 0.5618 |
| verb_future | 1.0000 | 0.4466 | 0.5185 | 0.4815 | 0.6429 |
| verb_past | 1.0000 | 0.6087 | 0.6222 | 0.6341 | 0.6667 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
