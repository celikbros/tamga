# v1.7 Baseline Matrix: multilingual_smoke

Dataset: `data/eval/multilingual_smoke.tsv`
Config: `configs/v1_7_baselines.toml`

This visible-set report is for baseline tracking only. It must not be
used as hidden-eval evidence or as a downstream LLM-quality claim.

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 7.3000 | 2.0000 | 0.9551 | 17/20 |  |
| unicode_char | ok | 28.1000 | 7.6986 | 0.3601 | 0/20 |  |
| toy_bpe_1000 | ok | 24.1500 | 6.6164 | 0.3368 | 0/20 |  |
| sp_bpe_1000 | ok | 17.9000 | 4.9041 | 0.4902 | 0/20 |  |
| sp_unigram_1000 | ok | 18.1500 | 4.9726 | 0.4848 | 0/20 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | toy_bpe_1000 F1 | sp_bpe_1000 F1 | sp_unigram_1000 F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2941 | 0.1765 | 0.6667 | 0.6667 |
| azerbaijani | 0.8571 | 0.3797 | 0.4138 | 0.5000 | 0.4918 |
| french | 1.0000 | 0.2903 | 0.2745 | 0.3462 | 0.3396 |
| german | 1.0000 | 0.3729 | 0.4400 | 0.4314 | 0.4400 |
| greek | 1.0000 | 0.3333 | 0.2500 | 0.6667 | 0.6667 |
| italian | 1.0000 | 0.2581 | 0.3200 | 0.3478 | 0.3200 |
| kazakh_cyrillic | 1.0000 | 0.3614 | 0.3133 | 0.6000 | 0.6000 |
| kyrgyz_cyrillic | 1.0000 | 0.5714 | 0.4762 | 0.7333 | 0.7333 |
| multilingual_mixed | 0.6250 | 0.2456 | 0.0889 | 0.3784 | 0.3684 |
| russian | 1.0000 | 0.3902 | 0.2927 | 0.5217 | 0.5217 |
| spanish | 1.0000 | 0.3871 | 0.4615 | 0.4444 | 0.4286 |
| tatar_cyrillic | 1.0000 | 0.5417 | 0.4583 | 0.7500 | 0.7500 |
| uzbek_latin | 1.0000 | 0.2857 | 0.3636 | 0.3636 | 0.3636 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
