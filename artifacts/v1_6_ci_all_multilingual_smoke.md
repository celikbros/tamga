# Metric Confidence Intervals

Bootstrap samples: `500`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 0.4000 [0.2000, 0.6000] | 0.6775 [0.5236, 0.8455] | 2.8493 [1.9140, 4.9080] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.3601 [0.3062, 0.4119] | 7.6986 [5.5117, 13.8545] |  |
| toy_bpe_1000 | ok | 0.0000 [0.0000, 0.0000] | 0.3368 [0.2629, 0.3984] | 6.6164 [4.4089, 10.7445] |  |
| qwen | ok | 0.0000 [0.0000, 0.0000] | 0.2079 [0.1523, 0.2680] | 4.1781 [2.5887, 7.4436] |  |
| mistral | ok | 0.0000 [0.0000, 0.0000] | 0.4835 [0.4241, 0.5485] | 4.8767 [3.0815, 9.1768] |  |
| llama | ok | 0.0000 [0.0000, 0.0000] | 0.2134 [0.1491, 0.2777] | 4.1644 [2.5878, 7.8087] |  |
| sp_bpe | ok | 0.0000 [0.0000, 0.0000] | 0.4902 [0.4232, 0.5699] | 4.9041 [3.9158, 7.0947] |  |
| sp_unigram | ok | 0.0000 [0.0000, 0.0000] | 0.4848 [0.4202, 0.5549] | 4.9726 [3.9399, 7.1964] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
