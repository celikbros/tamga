# v2.0 Turkish Loan-Diacritic Pass-Through Findings

Date: 2026-06-10

## Change

Turkish-compatible loanword diacritics are now treated as normal Turkish text
letters instead of `non_turkish_latin_word` protected spans.

Characters added to the Turkish text alphabet:

```text
Â â Î î Û û Ô ô Ê ê
```

Examples now stay in normal text flow:

```text
hâlâ
imkân
Millî
ma'lûmat
```

True non-Turkish Latin words such as `Straße` and `niño` still remain
non-Turkish Latin.

## Route Quality Impact

Before:

```text
non_turkish_latin_word occurrences: 18984
turkish_loan_diacritic share: 91.30%
```

After:

```text
non_turkish_latin_word occurrences: 1644
legacy_turkish_encoding_artifact: 691
other_non_turkish_latin: 953
```

Report:

```text
artifacts/v2_0_non_turkish_latin_route_quality_audit_after_loan_pass.md
```

## Token-Pressure Impact

Finite protected wrapper test pressure improved:

| Metric | Before | After |
| --- | ---: | ---: |
| test SP64 tokens/raw byte | 0.159620 | 0.159620 |
| test finite protected tokens/raw byte | 0.183362 | 0.180564 |
| relative delta over SP64 | 14.87% | 13.12% |
| protected bytes share | 2.67% | 2.19% |

Report:

```text
artifacts/v2_0_finite_protected_wrapper_cost_audit_after_loan_pass.md
```

## Safety Check

Finite protected intrinsic behavior remains acceptable:

```text
protected stress: 25/25
challenge F1: 0.6913
```

Report:

```text
artifacts/v2_0_finite_protected_sp64_intrinsic_eval_after_loan_pass.md
```

## Decision

Keep the Turkish loan-diacritic pass-through.

This does not solve the whole wrapper cost problem, but it removes a clear
over-routing issue without hurting protected span preservation.

Next cost targets:

```text
1. numeric_like
2. file_like
3. apostrophe_surface
4. legacy_turkish_encoding_artifact handling
```

Do not move to constrained/MorphBPE until numeric/file/apostrophe protected
route costs have been reviewed.
