# Metric Confidence Intervals

Bootstrap samples: `500`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 2.7438 [2.4542, 3.1402] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.4947 [0.4766, 0.5125] | 7.5041 [6.5660, 8.6016] |  |
| toy_bpe_1000 | ok | 0.0200 [0.0000, 0.0600] | 0.6277 [0.5938, 0.6602] | 2.7438 [2.4802, 3.1095] |  |
| qwen | ok | 0.0000 [0.0000, 0.0000] | 0.3317 [0.2822, 0.3753] | 3.0661 [2.7003, 3.4983] |  |
| mistral | ok | 0.0000 [0.0000, 0.0000] | 0.5423 [0.5087, 0.5744] | 4.3306 [3.8539, 4.8845] |  |
| llama | ok | 0.0000 [0.0000, 0.0000] | 0.3259 [0.2809, 0.3728] | 2.9008 [2.5901, 3.2699] |  |
| sp_bpe | ok | 0.0200 [0.0000, 0.0600] | 0.6263 [0.5852, 0.6641] | 2.7273 [2.4654, 3.1476] |  |
| sp_unigram | ok | 0.0000 [0.0000, 0.0000] | 0.6325 [0.6009, 0.6645] | 3.0744 [2.7984, 3.4611] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
