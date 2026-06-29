# v2.0 Protected Route Cost Reduction Findings

Date: 2026-06-10

## Why This Step Happened

Fable5 correctly pointed out that the finite protected wrapper was adding a
large token-pressure cost before we had explained it:

```text
SP64 test tokens/raw byte: 0.159620
finite protected test tokens/raw byte before route fixes: 0.183362
relative delta: 14.87%
```

The right next step was therefore not constrained MorphBPE. It was to audit and
reduce avoidable protected-route cost.

## Changes Made

### Turkish Loan-Diacritic Pass-Through

Turkish-compatible loan diacritics are now treated as Turkish text rather than
as `non_turkish_latin_word`:

```text
Â â Î î Û û Ô ô Ê ê
```

Effect:

```text
non_turkish_latin_word route occurrences: 18984 -> 1644
test finite tokens/raw byte: 0.183362 -> 0.180564
relative delta over SP64: 14.87% -> 13.12%
```

### Buffered Turkish Apostrophe Suffixes

The guarded apostrophe suffix parser now recognizes common buffered Turkish
suffix forms such as:

```text
ne, na, nde, nda, nden, ndan, yla, yle, nce
```

This moves forms like `Üniversitesi'nde`, `Mahkemesi'ne`, and
`Mütarekesi'nden` out of the expensive `apostrophe_surface` protected route and
into normal apostrophe + suffix handling.

Effect:

```text
apostrophe_surface delta after loan pass: 54055
apostrophe_surface delta after apostrophe pass: 20662
test finite tokens/raw byte: 0.180564 -> 0.179465
relative delta over SP64: 13.12% -> 12.43%
```

### Glued Sentence Boundary Split For File-Like False Positives

The pretokenizer now splits narrow false-positive `file_like` cases such as:

```text
değerlendirildi.Bulgular
amaçlanmıştır.Gereç
```

It keeps true file/code-ish examples such as:

```text
README.md
Prof.Dr
System.Console
```

Effect:

```text
file_like delta after apostrophe pass: 120800
file_like delta after glued-boundary pass: 72043
test finite tokens/raw byte: 0.179465 -> 0.177726
relative delta over SP64: 12.43% -> 11.34%
```

## Current Cost Position

Latest report:

```text
artifacts/v2_0_finite_protected_wrapper_cost_audit_after_file_glue_pass.md
```

Current test split:

| Candidate | Test tokens/raw byte | Relative delta vs SP64 |
| --- | ---: | ---: |
| SP64 | 0.159620 | 0.00% |
| finite protected before route fixes | 0.183362 | 14.87% |
| finite protected after route fixes | 0.177726 | 11.34% |

Latest high-cost route deltas:

| Route | Delta tokens vs SP on same surface |
| --- | ---: |
| `numeric_like` | 137885 |
| `file_like` | 72043 |
| `apostrophe_surface` | 20662 |
| `non_turkish_latin_word` | 9792 |

## Regression Checks

Latest intrinsic report:

```text
artifacts/v2_0_finite_protected_sp64_intrinsic_eval_after_file_glue_pass.md
```

No visible protection regression:

```text
protected stress: 25/25
challenge F1: 0.6913
```

Targeted tests:

```text
56 passed
```

## Interpretation

The wrapper still costs too much, but the work is moving in the right direction.
We reduced finite protected test token pressure by about 3.1% relative without
touching morphology learning and without losing protected-span preservation.

This supports the current roadmap:

```text
Keep auditing and optimizing protected routing before implementing a new
constrained/MorphBPE trainer.
```

## Numeric Follow-Up

The next high-value target was `numeric_like`.

Most numeric cost comes from:

```text
plain_integer_3_4_digit
decimal_or_grouped_number
year_range
plain_integer_2_digit
```

The current finite protected encoder often pays about one token per digit/byte.
The numeric what-if audit tested cheaper alternatives:

```text
artifacts/v2_0_numeric_protected_encoder_whatif.md
docs/v2_0_numeric_protected_encoder_whatif_findings.md
```

Result on test:

| Policy | Test tokens/raw byte |
| --- | ---: |
| current finite protected | 0.177726 |
| numeric via SP64 | 0.172734 |
| 2-digit finite numeric codec what-if | 0.175069 |

The next decision is whether to accept `finite_protected_sp64_numeric_sp_floor`
as the protected null baseline, or to build a small finite numeric codec before
returning to morphology-prior work.
