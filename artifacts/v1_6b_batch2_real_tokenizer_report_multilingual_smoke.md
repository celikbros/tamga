# Real Tokenizer Baseline Report

## Summary

| Model | Status | Avg tokens/example | Avg tokens/word | Boundary F1 | Exact match vs gold | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 8.4000 | 2.3014 | 0.8015 | 11/20 |  |
| unicode_char | ok | 28.1000 | 7.6986 | 0.3601 | 0/20 |  |
| toy_bpe_1000 | ok | 24.1500 | 6.6164 | 0.3368 | 0/20 |  |
| qwen | ok | 15.2500 | 4.1781 | 0.2079 | 0/20 |  |
| mistral | ok | 17.8000 | 4.8767 | 0.4835 | 0/20 |  |
| llama | ok | 15.2000 | 4.1644 | 0.2134 | 0/20 |  |
| sp_bpe | ok | 17.9000 | 4.9041 | 0.4902 | 0/20 |  |
| sp_unigram | ok | 18.1500 | 4.9726 | 0.4848 | 0/20 |  |

## Category Summary

| Category | custom_tr_morph F1 | unicode_char F1 | toy_bpe_1000 F1 | qwen F1 | mistral F1 | llama F1 | sp_bpe F1 | sp_unigram F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| arabic | 1.0000 | 0.2941 | 0.1765 | 0.0000 | 0.3030 | 0.0000 | 0.6667 | 0.6667 |
| azerbaijani | 0.8571 | 0.3797 | 0.4138 | 0.2264 | 0.5172 | 0.2353 | 0.5000 | 0.4918 |
| french | 0.5385 | 0.2903 | 0.2745 | 0.5600 | 0.5625 | 0.5600 | 0.3462 | 0.3396 |
| german | 0.5600 | 0.3729 | 0.4400 | 0.2222 | 0.8148 | 0.2222 | 0.4314 | 0.4400 |
| greek | 1.0000 | 0.3333 | 0.2500 | 0.0833 | 0.2857 | 0.0000 | 0.6667 | 0.6667 |
| italian | 0.6154 | 0.2581 | 0.3200 | 0.3077 | 0.5333 | 0.3077 | 0.3478 | 0.3200 |
| kazakh_cyrillic | 1.0000 | 0.3614 | 0.3133 | 0.1587 | 0.3692 | 0.1587 | 0.6000 | 0.6000 |
| kyrgyz_cyrillic | 1.0000 | 0.5714 | 0.4762 | 0.2000 | 0.5854 | 0.1818 | 0.7333 | 0.7333 |
| multilingual_mixed | 0.6250 | 0.2456 | 0.0889 | 0.1905 | 0.5385 | 0.1905 | 0.3784 | 0.3684 |
| russian | 1.0000 | 0.3902 | 0.2927 | 0.1000 | 0.5714 | 0.0000 | 0.5217 | 0.5217 |
| spanish | 0.2222 | 0.3871 | 0.4615 | 0.4706 | 0.6667 | 0.4444 | 0.4444 | 0.4286 |
| tatar_cyrillic | 1.0000 | 0.5417 | 0.4583 | 0.1304 | 0.3830 | 0.2083 | 0.7500 | 0.7500 |
| uzbek_latin | 1.0000 | 0.2857 | 0.3636 | 0.2000 | 0.4545 | 0.2222 | 0.3636 | 0.3636 |

## Notes

- External tokenizer boundary F1 is approximate unless offsets are available.
- Token count alone is not tokenizer quality.
- Skipped models mean optional dependencies or local model files were not available.
- This report must not be used to tune the frozen regression or hidden eval sets.
