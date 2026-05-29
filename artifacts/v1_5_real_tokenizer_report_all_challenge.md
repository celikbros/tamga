# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.7130 | 2.1749 | 0.9220 | 44/108 |  |
| unicode_char | ok | 23.4815 | 6.6214 | 0.4949 | 0/108 |  |
| toy_bpe_1000 | ok | 9.7778 | 2.7572 | 0.6610 | 0/108 |  |
| qwen | ok | 10.1389 | 2.8590 | 0.3511 | 0/108 |  |
| mistral | ok | 13.9815 | 3.9426 | 0.5463 | 0/108 |  |
| llama | ok | 9.1296 | 2.5744 | 0.3501 | 0/108 |  |
| sp_bpe | ok | 9.8611 | 2.7807 | 0.6497 | 0/108 |  |
| sp_unigram | ok | 10.3981 | 2.9321 | 0.6225 | 0/108 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | toy_bpe_1000 F1 | qwen F1 | mistral F1 | llama F1 | sp_bpe F1 | sp_unigram F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ambiguity | 0.8866 | 0.5436 | 0.6667 | 0.2957 | 0.5278 | 0.2963 | 0.6720 | 0.6032 |
| code_mixed | 0.9315 | 0.4695 | 0.6792 | 0.4331 | 0.5871 | 0.3899 | 0.6335 | 0.6044 |
| informal | 0.8649 | 0.4444 | 0.7595 | 0.2376 | 0.5913 | 0.2000 | 0.7750 | 0.6364 |
| negative_word | 0.8317 | 0.4291 | 0.7442 | 0.1898 | 0.5217 | 0.1955 | 0.7634 | 0.6767 |
| numbers_dates | 0.9649 | 0.4545 | 0.5316 | 0.3537 | 0.4656 | 0.4122 | 0.5125 | 0.5576 |
| proper_name | 1.0000 | 0.5367 | 0.6957 | 0.4886 | 0.6220 | 0.4941 | 0.6995 | 0.7033 |
| punctuation | 0.9921 | 0.4956 | 0.6364 | 0.4857 | 0.5556 | 0.4844 | 0.6536 | 0.5882 |
| question | 0.9500 | 0.5128 | 0.7903 | 0.4211 | 0.6173 | 0.4228 | 0.7742 | 0.7200 |
| softening | 0.8906 | 0.5240 | 0.6519 | 0.1854 | 0.5567 | 0.2069 | 0.6331 | 0.5833 |
| suffix_chain | 0.8958 | 0.4858 | 0.5326 | 0.3836 | 0.4655 | 0.3317 | 0.5241 | 0.5918 |
| verb_future | 0.8246 | 0.4735 | 0.6071 | 0.3026 | 0.5189 | 0.3165 | 0.5833 | 0.5714 |
| verb_past | 0.9554 | 0.5634 | 0.7439 | 0.3488 | 0.5744 | 0.3750 | 0.7044 | 0.6627 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
