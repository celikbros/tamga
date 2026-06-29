# v2.0 Finite Protected Wrapper Cost Findings

Date: 2026-06-10

## Summary

The finite protected wrapper cost is now decomposed with the same token
accounting used by the tiny-LM BPB probe.

Report:

```text
artifacts/v2_0_finite_protected_wrapper_cost_audit.md
```

Private line examples:

```text
artifacts/private/v2_0_finite_protected_wrapper_cost_top_delta.jsonl
```

## Main Result

The wrapper reproduces the known finite-protected token pressure:

| Split | SP64 tokens/raw byte | Finite protected tokens/raw byte | Relative delta | Protected bytes share |
| --- | ---: | ---: | ---: | ---: |
| train | 0.154680 | 0.178591 | 15.46% | 2.61% |
| valid | 0.159020 | 0.182112 | 14.52% | 2.61% |
| test | 0.159620 | 0.183362 | 14.87% | 2.67% |

This confirms Fable5's critique: protected spans are a small byte share, but
the wrapper adds a large token-pressure cost.

## Where The Cost Comes From

The highest-cost routes are not Turkish morphology. They are protected route
encoding choices:

| Route | Protected tokens | SP tokens on same surface | Delta |
| --- | ---: | ---: | ---: |
| `numeric_like` | 260245 | 122438 | +137807 |
| `file_like` | 165506 | 44926 | +120580 |
| `non_turkish_latin_word` | 133982 | 39321 | +94661 |
| `apostrophe_surface` | 74811 | 23608 | +51203 |

The private top-delta examples are dominated by dense
`non_turkish_latin_word`, `numeric_like`, and `file_like` lines.

Manual inspection of the private top-delta examples shows a likely
data-quality/router interaction: many of the highest-cost
`non_turkish_latin_word` lines are Turkish prose with legacy/incorrect Turkish
encoding artifacts mixed in. Examples contain characters such as `ý`, `þ`,
`ð`, and `Ý`, which often correspond to Turkish `ı`, `ş`, `ğ`, and `İ` in
misdecoded ISO-8859-9 / Windows-1254-like text.

That means part of the wrapper cost may be caused by the route guard protecting
corrupted Turkish spans as if they were genuine non-Turkish Latin spans.

A follow-up route-quality audit refined this further:

```text
artifacts/v2_0_non_turkish_latin_route_quality_audit.md
docs/v2_0_non_turkish_latin_route_quality_findings.md
```

The dominant `non_turkish_latin_word` subtype is actually Turkish loan-diacritic
text, not legacy corruption:

```text
turkish_loan_diacritic: 91.30%
other_non_turkish_latin: 5.06%
legacy_turkish_encoding_artifact: 3.64%
```

## Interpretation

The finite protected wrapper is doing the right semantic job:

```text
protected stress: 25/25
decode remains stateless
fallback is finite
```

But it is too conservative in model-token accounting. It often replaces a
compact SP64 segmentation with protected-piece/byte segmentation that is 2x-4x
more expensive on the same surface.

This means the next move should not be constrained MorphBPE yet. The immediate
target is protected-route optimization.

## Next Decision

Before any MorphBPE trainer work:

```text
1. Reroute Turkish loan-diacritic words back to normal learned text flow.
2. Keep reviewing legacy-encoding-like rows as data-quality/routing cases.
3. Optimize numeric/file/apostrophe protected encoders.
4. Re-evaluate finite_protected_sp64_floor pressure and stress preservation.
5. Only then continue to vocab coverage and boundary-biased Viterbi.
```

Success target for the optimized protected floor:

```text
protected stress: 25/25
test tokens/raw byte materially below 0.183362
no regression in decode/lossless assumptions
```

The project is still on the hybrid path, but this finding changes the order:
reduce protected-wrapper cost first, then revisit morphology-prior mechanisms.
