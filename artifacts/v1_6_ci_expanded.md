# Metric Confidence Intervals

Bootstrap samples: `1000`

| Model | Status | Exact match rate | Boundary F1 | Avg tokens/word | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| custom_tr_morph | ok | 1.0000 [1.0000, 1.0000] | 1.0000 [1.0000, 1.0000] | 2.7438 [2.4537, 3.1184] |  |
| unicode_char | ok | 0.0000 [0.0000, 0.0000] | 0.4947 [0.4780, 0.5135] | 7.5041 [6.6433, 8.5487] |  |

## Notes

- Intervals are non-parametric bootstrap 95% intervals over examples.
- These intervals reflect dataset sampling uncertainty, not annotation uncertainty.
- Small smoke sets can have wide or unstable intervals; interpret them cautiously.
