# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| unicode_char | ok | 23.4815 | 6.6214 | 0.4949 | 0/108 |  |
| llama | ok | 9.1296 | 2.5744 | 0.3501 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | llama F1 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.5436 | 0.2963 |
| code_mixed | 0.9315 | 0.4695 | 0.3899 |
| informal | 0.8649 | 0.4444 | 0.2000 |
| negative_word | 0.8317 | 0.4291 | 0.1955 |
| numbers_dates | 0.9649 | 0.4545 | 0.4122 |
| proper_name | 1.0000 | 0.5367 | 0.4941 |
| punctuation | 0.9921 | 0.4956 | 0.4844 |
| question | 0.9500 | 0.5128 | 0.4228 |
| softening | 0.8906 | 0.5240 | 0.2069 |
| suffix_chain | 0.8958 | 0.4858 | 0.3317 |
| verb_future | 0.8246 | 0.4735 | 0.3165 |
| verb_past | 0.9554 | 0.5634 | 0.3750 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
