# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 6.6400 | 2.7438 | 1.0000 | 50/50 |  |
| unicode_char | ok | 18.1600 | 7.5041 | 0.4947 | 0/50 |  |
| llama | ok | 7.0200 | 2.9008 | 0.3259 | 0/50 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | llama F1 |
| --- | ---: | ---: | ---: |
| code_mixed | 1.0000 | 0.4768 | 0.3733 |
| informal | 1.0000 | 0.4478 | 0.4211 |
| negative_word | 1.0000 | 0.4167 | 0.1724 |
| proper_name | 1.0000 | 0.5087 | 0.4524 |
| question | 1.0000 | 0.5455 | 0.3607 |
| softening | 1.0000 | 0.5248 | 0.2683 |
| suffix_chain | 1.0000 | 0.4951 | 0.2340 |
| verb_future | 1.0000 | 0.4466 | 0.4255 |
| verb_past | 1.0000 | 0.6087 | 0.2727 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
