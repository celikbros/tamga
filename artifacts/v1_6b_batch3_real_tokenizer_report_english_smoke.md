# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 8.5000 | 1.0897 | 0.9155 | 8/10 |  |
| unicode_char | ok | 39.6000 | 5.0769 | 0.2781 | 0/10 |  |
| toy_bpe_1000 | ok | 27.5000 | 3.5256 | 0.3735 | 0/10 |  |
| qwen | ok | 12.2000 | 1.5641 | 0.5251 | 0/10 |  |
| mistral | ok | 15.2000 | 1.9487 | 0.5742 | 0/10 |  |
| llama | ok | 11.6000 | 1.4872 | 0.5434 | 0/10 |  |
| sp_bpe | ok | 27.2000 | 3.4872 | 0.3647 | 0/10 |  |
| sp_unigram | ok | 29.4000 | 3.7692 | 0.3533 | 0/10 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | toy_bpe_1000 F1 | qwen F1 | mistral F1 | llama F1 | sp_bpe F1 | sp_unigram F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| code_like | 1.0000 | 0.2243 | 0.2716 | 0.3784 | 0.3913 | 0.3784 | 0.2857 | 0.2821 |
| english_apostrophe | 1.0000 | 0.2857 | 0.3721 | 0.7273 | 0.5926 | 0.7273 | 0.3636 | 0.3556 |
| english_passthrough | 0.9697 | 0.3333 | 0.4156 | 0.9412 | 0.8649 | 0.9412 | 0.4051 | 0.4103 |
| mixed_turkish_english | 0.7442 | 0.3600 | 0.5902 | 0.3415 | 0.7347 | 0.3415 | 0.5625 | 0.4737 |
| technical | 1.0000 | 0.1915 | 0.2571 | 0.4000 | 0.3600 | 0.4615 | 0.2154 | 0.2432 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
