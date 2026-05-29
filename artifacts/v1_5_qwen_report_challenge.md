# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| unicode_char | ok | 23.4815 | 6.6214 | 0.4949 | 0/108 |  |
| qwen | ok | 10.1389 | 2.8590 | 0.3511 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | qwen F1 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.5436 | 0.2957 |
| code_mixed | 0.9315 | 0.4695 | 0.4331 |
| informal | 0.8649 | 0.4444 | 0.2376 |
| negative_word | 0.8317 | 0.4291 | 0.1898 |
| numbers_dates | 0.9649 | 0.4545 | 0.3537 |
| proper_name | 1.0000 | 0.5367 | 0.4886 |
| punctuation | 0.9921 | 0.4956 | 0.4857 |
| question | 0.9500 | 0.5128 | 0.4211 |
| softening | 0.8906 | 0.5240 | 0.1854 |
| suffix_chain | 0.8958 | 0.4858 | 0.3836 |
| verb_future | 0.8246 | 0.4735 | 0.3026 |
| verb_past | 0.9554 | 0.5634 | 0.3488 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
