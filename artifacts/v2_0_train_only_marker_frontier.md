# v2.0 Train-Only Marker Frontier

This report compares the first train-only marker shaping points. These are
intrinsic tokenizer diagnostics, not LLM results.

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress | Source reports |
| --- | ---: | ---: | ---: | --- | --- |
| SP64 reference | 0.159020 | 0.159620 | 0.7351 | 1/25 | `artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md` |
| all-soft train-only marker-stripped | 0.195611 | 0.196236 | 0.7703 | 25/25 | `artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md` |
| suffix-chain2 train-only marker-stripped | 0.183799 | 0.184619 | 0.7632 | 25/25 | `artifacts/v2_0_train_only_suffix_chain2_marker_stripped_diagnostic.md` |
| high-value suffix train-only marker-stripped | 0.190346 | 0.191068 | 0.7665 | 25/25 | `artifacts/v2_0_train_only_high_value_suffix_marker_stripped_diagnostic.md` |

## Decision

The current train-only marker policies pass the broad token-pressure target but
do not yet pass the preferred visible intrinsic gate.

```text
Do not run another tiny-LM probe yet.
Next: improve train-only shaping or ask advisors using this frontier.
```
