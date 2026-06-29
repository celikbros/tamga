# v2.0 Numeric Protected Encoder What-If Findings

Date: 2026-06-10

## Why This Step Happened

After the loan-diacritic, apostrophe, and glued-sentence route fixes, the
largest remaining finite protected wrapper cost was `numeric_like`.

Latest pre-numeric route state:

```text
SP64 test tokens/raw byte: 0.159620
finite protected test tokens/raw byte: 0.177726
relative delta over SP64: 11.34%
numeric_like protected-vs-SP route delta: +137885 tokens
```

So the question became:

```text
Can numbers remain logically protected without paying byte-like token cost?
```

## What Was Added

New audit:

```text
scripts/audit_v2_numeric_protected_encoder_whatif.py
artifacts/v2_0_numeric_protected_encoder_whatif.md
```

New experimental LM-probe tokenizer kind:

```text
finite_protected_marker_stripped_numeric_sp
```

New config row:

```text
finite_protected_sp64_numeric_sp_floor
configs/v2_0_tiny_lm_marker_calibration.toml
```

This candidate keeps the finite protected wrapper, but routes
`protected:numeric_like` model tokens through the underlying SP64 model instead
of the finite protected byte/subpiece path.

It is an experiment, not yet the final protected numeric design.

## What-If Results

Report:

```text
artifacts/v2_0_numeric_protected_encoder_whatif.md
```

Test split:

| Policy | Test tokens/raw byte |
| --- | ---: |
| current finite protected | 0.177726 |
| numeric via SP64 | 0.172734 |
| 2-digit chunk numeric codec | 0.175069 |
| 4-digit chunk upper-bound codec | 0.173904 |

The SP numeric route recovers about `0.004992` tokens/raw byte on test.

## Dry-Run Confirmation

Dry-run report:

```text
artifacts/v2_0_tiny_lm_marker_calibration_numeric_sp_dry_run.md
```

The actual LM-probe encoder matches the what-if estimate:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| finite protected after route fixes | 0.176643 | 0.177726 |
| finite protected + numeric SP | 0.171903 | 0.172734 |

## Tiny-LM BPB Calibration

300-step reports:

```text
artifacts/v2_0_tiny_lm_marker_calibration_numeric_sp_300steps.md
artifacts/v2_0_tiny_lm_marker_calibration_finite_protected_sp64_current_300steps.md
```

Current-code result:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite protected plain floor | 0.176643 | 0.177726 | 4.897577 | 4.939361 |
| finite protected + numeric SP | 0.171903 | 0.172734 | 4.875198 | 4.911037 |

This improves over the current plain finite protected floor:

```text
current finite_protected_sp64_floor test BPB: 4.939361
numeric-SP floor test BPB:                    4.911037
BPB gain:                                     0.028324
```

The earlier `finite_protected_sp64_floor` value `4.976850` is now historical;
it was measured before the latest route-cost fixes.

## Numeric Cost Concentration

Largest current-vs-SP numeric deltas:

| Numeric class | Current-SP delta |
| --- | ---: |
| `plain_integer_3_4_digit` | 49063 |
| `decimal_or_grouped_number` | 20710 |
| `year_range` | 20093 |
| `plain_integer_2_digit` | 18882 |
| `alnum_mixed_text` | 14555 |

## Interpretation

This is a meaningful reduction in wrapper pressure without touching the
morphology teacher.

But it also clarifies the design tradeoff:

```text
SP numeric passthrough is compression-efficient.
A finite digit codec is more explicitly protected, but not as cheap.
```

For a production tokenizer, we should not blindly declare SP numeric passthrough
as the final numeric design. Numeric/date/code-like spans may need clearer
decode and generation semantics than ordinary normal text. Still, as an
experimental floor, it is now the best protected null baseline.

## Updated Decision

Promote `finite_protected_sp64_numeric_sp_floor` as the active protected floor
for the next v2.0 experiments.

Do not build constrained/MorphBPE until this numeric route choice is either:

```text
accepted as the protected floor, or
replaced by a small finite numeric codec.
```

## Next Step

Resume the pre-MorphBPE diagnostics:

```text
1. SP64 / safe-UDS7 vocabulary coverage for teacher morph surfaces.
2. Decode-time boundary-biased Unigram/Viterbi lambda sweep.
3. Only then decide whether a constrained/MorphBPE trainer is justified.
```
