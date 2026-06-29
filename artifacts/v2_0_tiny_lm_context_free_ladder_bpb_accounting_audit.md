# v2.0 Tiny-LM BPB Accounting Audit

This audit checks whether the context-free BPB ladder is being read as
a mature language-model result. It converts BPB back to implied bits per
token and compares it with the uniform-vocabulary reference.

Important: cross-entropy can exceed the uniform reference during early
training if the random/tied-output model assigns extremely low
probability to the observed token. Therefore, exceeding the uniform
reference is not a mathematical impossibility. It is evidence that the
2M-byte runs are still in an undertrained / early-convergence regime.

## Summary

| Tokenizer | Vocab | Uniform bits/token | Valid bits/token | Test bits/token | Final train bits/token | Test BPB | Test tokens/byte | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| finite_protected_sp64_numeric_sp_floor | 64630 | 15.9799 | 20.2231 | 20.2221 | 20.6888 | 3.326482 | 0.164497 | above uniform; undertrained regime |
| finite_protected_pruned_ge070_nonword | 64630 | 15.9799 | 19.8938 | 19.9407 | 21.1268 | 3.324067 | 0.166698 | above uniform; undertrained regime |
| finite_protected_teacher_distilled_16000 | 64630 | 15.9799 | 18.0269 | 18.0679 | 20.1665 | 3.213530 | 0.177859 | above uniform; undertrained regime |
| finite_protected_teacher_distilled_2000 | 64630 | 15.9799 | 16.9718 | 17.0457 | 19.0999 | 3.259261 | 0.191208 | above uniform; undertrained regime |

## Reading

The ladder is useful as an early learning-curve calibration, but the
absolute BPB endpoints should not be treated as converged tokenizer
quality. The high implied bits/token values support the advisors'
warning that the current 2M-byte runs mostly measure early learning
speed and estimation geometry.

The teacher-distilled 16k row remains interesting because its BPB is
better under the same early-regime harness. However, attribution is
not settled until a non-morphology matched-control score model is run.

## Next Control

Run a same-vocabulary self-distilled control:

```text
fixed SP64 vocabulary
same finite protected wrapper
same 16k train-line score re-estimation
official SP segmentation counts instead of morphology-teacher counts
```

If teacher_distilled_16000 beats this matched control materially, the
gain is more likely morphology-specific. If not, the BPB gain is
probably score concentration / estimation geometry rather than
morphology.
