# Metric Confidence Intervals

Bootstrap samples: `1000`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 0.8500 [0.7000, 1.0000] | 0.9551 [0.8990, 1.0000] | 2.0000 [1.3980, 3.4753] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.3601 [0.3083, 0.4108] | 7.6986 [5.5325, 13.0468] |  |
| toy_bpe_1000 | ok | 0.0000 [0.0000, 0.0000] | 0.3368 [0.2724, 0.3993] | 6.6164 [4.4639, 10.7628] |  |
| qwen | ok | 0.0000 [0.0000, 0.0000] | 0.2079 [0.1499, 0.2685] | 4.1781 [2.6245, 7.3211] |  |
| mistral | ok | 0.0000 [0.0000, 0.0000] | 0.4835 [0.4236, 0.5487] | 4.8767 [3.1086, 9.1812] |  |
| llama | ok | 0.0000 [0.0000, 0.0000] | 0.2134 [0.1542, 0.2769] | 4.1644 [2.6750, 7.5764] |  |
| sp_bpe | ok | 0.0000 [0.0000, 0.0000] | 0.4902 [0.4225, 0.5703] | 4.9041 [3.8817, 7.1744] |  |
| sp_unigram | ok | 0.0000 [0.0000, 0.0000] | 0.4848 [0.4185, 0.5551] | 4.9726 [3.9495, 7.3096] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
