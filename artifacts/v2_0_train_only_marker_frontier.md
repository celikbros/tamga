# v2.0 Train-Only Marker Frontier

This report compares the first train-only marker shaping points. These are
intrinsic tokenizer diagnostics, not LLM results.

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress | Source reports |
| --- | ---: | ---: | ---: | --- | --- |
| SP64 reference | 0.159020 | 0.159620 | 0.7351 | 1/25 | `artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md` |
| finite protected + SP64 | n/a | n/a | 0.6913 | 25/25 | `artifacts/v2_0_finite_protected_sp64_intrinsic_eval.md` |
| all-soft train-only marker-stripped | 0.195611 | 0.196236 | 0.7703 | 25/25 | `artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md` |
| suffix-chain2 train-only marker-stripped | 0.183799 | 0.184619 | 0.7632 | 25/25 | `artifacts/v2_0_train_only_suffix_chain2_marker_stripped_diagnostic.md` |
| high-value suffix train-only marker-stripped | 0.190346 | 0.191068 | 0.7665 | 25/25 | `artifacts/v2_0_train_only_high_value_suffix_marker_stripped_diagnostic.md` |

## Follow-Up Audits

Marker vocabulary audit:

```text
report: artifacts/v2_0_sentencepiece_marker_vocab_audit.md
SP64 marker pieces: 0
all-soft marker pieces: 1 exact marker only
suffix-chain2 marker pieces: 1 exact marker only
high-value suffix marker pieces: 1 exact marker only
decision: no marker+surface vocab capacity artifact found
```

Challenge F1 confidence intervals:

```text
report: artifacts/v2_0_train_only_marker_frontier_ci.md
SP64: 0.7351 [0.7036, 0.7648]
finite protected + SP64: 0.6913 [0.6537, 0.7280]
all-soft marker-stripped: 0.7703 [0.7326, 0.8046]
suffix-chain2: 0.7632 [0.7273, 0.7962]
high-value suffix: 0.7665 [0.7306, 0.7977]
decision: train-only marker F1 rankings overlap heavily; prefer lower token
pressure unless BPB calibration says otherwise
```

## Decision

The current train-only marker policies pass the broad token-pressure target but
their small F1 differences are not reliable enough to rank confidently.

```text
Do not add more marker-dose variants.
Next: either calibrate BPB on the bracketing candidates or move to a genuinely
different mechanism such as seed vocabulary / curated morph pieces.
```
