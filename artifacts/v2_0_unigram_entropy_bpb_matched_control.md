# v2.0 Unigram Entropy BPB Decomposition

This is a zero-training decomposition. It tokenizes train/test exactly
through the configured tokenizer path, estimates a smoothed unigram
distribution from the train token stream, and evaluates test negative
log likelihood normalized by raw test bytes.

This answers whether the tiny-LM BPB gap is already present in static
token distribution geometry before any contextual modeling.

## Results

| Tokenizer | Vocab | Train tokens/byte | Test tokens/byte | Train seen types | Test unseen rate | Alpha | Test bits/token | Test unigram BPB | Known-token bits/token | Known coverage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 64630 | 0.159113 | 0.164497 | 64000 | 0.000111 | 0.1 | 12.322119 | 2.026952 | 12.320461 | 0.999889 |
| finite_protected_self_distilled_16000 | 64630 | 0.159508 | 0.164852 | 63496 | 0.000107 | 0.1 | 12.303881 | 2.028322 | 12.302263 | 0.999893 |
| finite_protected_teacher_distilled_16000 | 64630 | 0.172603 | 0.177859 | 56615 | 0.000129 | 0.1 | 11.873857 | 2.111869 | 11.871640 | 0.999871 |

## Delta Versus First Row

| Tokenizer | Test unigram BPB delta |
| --- | ---: |
| finite_protected_sp64_numeric_sp_floor | +0.000000 |
| finite_protected_self_distilled_16000 | +0.001370 |
| finite_protected_teacher_distilled_16000 | +0.084916 |

## Reading

If the teacher-distilled row already wins by roughly the same amount in
this table as in tiny-LM BPB, most of the gain is static distributional
geometry. If it does not win here but wins in tiny-LM, the evidence
points more toward contextual/morphological usefulness.
