# Metric Confidence Intervals

Bootstrap samples: `500`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 0.4074 [0.3056, 0.5093] | 0.9220 [0.9043, 0.9382] | 2.1749 [2.0544, 2.3080] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.4949 [0.4829, 0.5077] | 6.6214 [6.2458, 7.0406] |  |
| toy_bpe_1000 | ok | 0.0000 [0.0000, 0.0000] | 0.6610 [0.6329, 0.6887] | 2.7572 [2.5988, 2.9089] |  |
| qwen | ok | 0.0000 [0.0000, 0.0000] | 0.3511 [0.3155, 0.3835] | 2.8590 [2.7242, 3.0014] |  |
| mistral | ok | 0.0000 [0.0000, 0.0000] | 0.5463 [0.5231, 0.5686] | 3.9426 [3.7500, 4.1805] |  |
| llama | ok | 0.0000 [0.0000, 0.0000] | 0.3501 [0.3166, 0.3824] | 2.5744 [2.4441, 2.7235] |  |
| sp_bpe | ok | 0.0000 [0.0000, 0.0000] | 0.6497 [0.6228, 0.6758] | 2.7807 [2.6365, 2.9459] |  |
| sp_unigram | ok | 0.0000 [0.0000, 0.0000] | 0.6225 [0.6005, 0.6452] | 2.9321 [2.7930, 3.0761] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
