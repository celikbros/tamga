# v2.0 Methodology Chore Findings

Date: 2026-06-10

## Purpose

Before implementing a real boundary-weighted Unigram/EM objective, we closed
two methodology gaps flagged by Fable5:

```text
1. visible challenge noise floor / bootstrap CI
2. finite protected wrapper tax decomposition
```

## Bootstrap CI / Noise Floor

Script:

```text
scripts/report_v2_sp_model_ci.py
```

Report:

```text
artifacts/v2_0_sp_model_ci_challenge_current_frontier.md
```

Models:

```text
SP64
partial-boundary rho=0.25
score-shift mass lambda=8
```

Key result:

| Model | Boundary F1 95% CI |
| --- | ---: |
| sp64_bare | 0.7351 [0.7047, 0.7633] |
| partial_rho025_bare | 0.7380 [0.7094, 0.7676] |
| score_shift_mass_l8_bare | 0.7364 [0.7045, 0.7658] |
| sp64_finite | 0.6755 [0.6366, 0.7156] |
| partial_rho025_finite | 0.6782 [0.6391, 0.7190] |
| score_shift_mass_l8_finite | 0.6768 [0.6356, 0.7152] |

Interpretation:

```text
The small point-estimate differences among SP-compatible hacks are within the
visible challenge noise floor. They should not be treated as real gains.
```

## Wrapper-Tax Decomposition

Script:

```text
scripts/audit_v2_finite_wrapper_eval_tax.py
```

Report:

```text
artifacts/v2_0_finite_wrapper_eval_tax_challenge.md
```

Overall:

| Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 108 | 0.7351 | 0.6755 | -0.0597 | 2.2010 | 2.2977 |

By route tag:

| Route tag | Examples | Bare F1 | Finite F1 | F1 delta |
| --- | ---: | ---: | ---: | ---: |
| no_protected | 94 | 0.7483 | 0.7303 | -0.0180 |
| file_like | 5 | 0.5859 | 0.2817 | -0.3042 |
| numeric_like | 9 | 0.7119 | 0.2703 | -0.4416 |

By feature tag:

| Feature | Examples | Bare F1 | Finite F1 | F1 delta |
| --- | ---: | ---: | ---: | ---: |
| apostrophe | 27 | 0.7674 | 0.6087 | -0.1587 |
| hard_suffix | 27 | 0.7674 | 0.6087 | -0.1587 |
| file_like | 5 | 0.5859 | 0.2817 | -0.3042 |
| numeric_like | 9 | 0.7119 | 0.2703 | -0.4416 |

Interpretation:

```text
The finite wrapper loss is not mostly a generic normal-text problem. It is
concentrated in protected-tail / apostrophe / numeric/file routes.
```

This matters because normal-text morphology objectives should not be blamed
for wrapper-specific losses.

## Decision

For objective development:

```text
use bare F1 as the primary development metric for normal-text morphology
track finite-wrapper tax separately
re-verify protected stress at branch end
```

Do not use finite-protected F1 alone as the main objective-development gate,
because it mixes normal-text morphology with protected-tail wrapper behavior.

## Next

Proceed to:

```text
boundary-weighted Unigram/EM objective spec
```

But keep a parallel small task:

```text
protected-tail wrapper redesign for numeric/file/apostrophe suffix cases
```

This route work can improve the protected frontier independently of the learned
normal-text objective.
