# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| unicode_char | ok | 23.4815 | 6.6214 | 0.4949 | 0/108 |  |
| mistral | ok | 13.9815 | 3.9426 | 0.5463 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | mistral F1 |
| --- | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.5436 | 0.5278 |
| code_mixed | 0.9315 | 0.4695 | 0.5871 |
| informal | 0.8649 | 0.4444 | 0.5913 |
| negative_word | 0.8317 | 0.4291 | 0.5217 |
| numbers_dates | 0.9649 | 0.4545 | 0.4656 |
| proper_name | 1.0000 | 0.5367 | 0.6220 |
| punctuation | 0.9921 | 0.4956 | 0.5556 |
| question | 0.9500 | 0.5128 | 0.6173 |
| softening | 0.8906 | 0.5240 | 0.5567 |
| suffix_chain | 0.8958 | 0.4858 | 0.4655 |
| verb_future | 0.8246 | 0.4735 | 0.5189 |
| verb_past | 0.9554 | 0.5634 | 0.5744 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
