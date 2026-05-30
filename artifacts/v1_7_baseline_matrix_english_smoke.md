# v1.7 Baseline Matrix: english_smoke

Dataset: `data/eval/en_smoke.tsv`
Config: `configs/v1_7_baselines.toml`

This visible-set report is for baseline tracking only. It must not be
used as hidden-eval evidence or as a downstream LLM-quality claim.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 8.5000 | 1.0897 | 0.9155 | 8/10 |  |
| unicode_char | ok | 39.6000 | 5.0769 | 0.2781 | 0/10 |  |
| toy_bpe_1000 | ok | 27.5000 | 3.5256 | 0.3735 | 0/10 |  |
| sp_bpe_1000 | ok | 27.2000 | 3.4872 | 0.3647 | 0/10 |  |
| sp_unigram_1000 | ok | 29.4000 | 3.7692 | 0.3533 | 0/10 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | toy_bpe_1000 F1 | sp_bpe_1000 F1 | sp_unigram_1000 F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| code_like | 1.0000 | 0.2243 | 0.2716 | 0.2857 | 0.2821 |
| english_apostrophe | 1.0000 | 0.2857 | 0.3721 | 0.3636 | 0.3556 |
| english_passthrough | 0.9697 | 0.3333 | 0.4156 | 0.4051 | 0.4103 |
| mixed_turkish_english | 0.7442 | 0.3600 | 0.5902 | 0.5625 | 0.4737 |
| technical | 1.0000 | 0.1915 | 0.2571 | 0.2154 | 0.2432 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
