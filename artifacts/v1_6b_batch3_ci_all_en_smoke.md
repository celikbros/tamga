# Metric Confidence Intervals

Bootstrap samples: `500`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 0.8000 [0.5000, 1.0000] | 0.9155 [0.8047, 1.0000] | 1.0897 [0.8545, 1.3403] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.2781 [0.2304, 0.3263] | 5.0769 [4.5027, 5.7688] |  |
| toy_bpe_1000 | ok | 0.0000 [0.0000, 0.0000] | 0.3735 [0.3017, 0.4569] | 3.5256 [3.0130, 4.1268] |  |
| qwen | ok | 0.0000 [0.0000, 0.0000] | 0.5251 [0.4010, 0.6946] | 1.5641 [1.3441, 1.7665] |  |
| mistral | ok | 0.0000 [0.0000, 0.0000] | 0.5742 [0.4531, 0.7015] | 1.9487 [1.6959, 2.2299] |  |
| llama | ok | 0.0000 [0.0000, 0.0000] | 0.5434 [0.4151, 0.6989] | 1.4872 [1.3109, 1.6648] |  |
| sp_bpe | ok | 0.0000 [0.0000, 0.0000] | 0.3647 [0.2972, 0.4414] | 3.4872 [3.0181, 4.0128] |  |
| sp_unigram | ok | 0.0000 [0.0000, 0.0000] | 0.3533 [0.2907, 0.4238] | 3.7692 [3.4310, 4.2199] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
