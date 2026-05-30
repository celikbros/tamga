# Metric Confidence Intervals

Bootstrap samples: `1000`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 0.4074 [0.3056, 0.5093] | 0.9220 [0.9027, 0.9377] | 2.1749 [2.0529, 2.3011] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.4949 [0.4819, 0.5077] | 6.6214 [6.2219, 7.0354] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
