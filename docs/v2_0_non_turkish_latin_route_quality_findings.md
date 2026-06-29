# v2.0 Non-Turkish Latin Route Quality Findings

Date: 2026-06-10

## Summary

The `non_turkish_latin_word` protected route is not mostly true foreign text.
It is mostly Turkish prose containing loanword diacritics such as `â`, `î`,
and `û`.

Report:

```text
artifacts/v2_0_non_turkish_latin_route_quality_audit.md
```

Private examples:

```text
artifacts/private/v2_0_non_turkish_latin_route_quality_examples.jsonl
```

## Result

Across the v1.8 filtered train/valid/test split:

| Class | Occurrences | Share | Bytes | Unique surfaces |
| --- | ---: | ---: | ---: | ---: |
| `turkish_loan_diacritic` | 17333 | 91.30% | 145382 | 5742 |
| `other_non_turkish_latin` | 960 | 5.06% | 9065 | 675 |
| `legacy_turkish_encoding_artifact` | 691 | 3.64% | 8506 | 453 |

This explains a large part of the finite protected wrapper cost. The route is
over-protecting normal Turkish-compatible words.

## Interpretation

Current behavior:

```text
hâlâ / imkân / ma'lûmat / Millî
  -> protected:non_turkish_latin_word
  -> finite protected subword/byte encoder
  -> high token pressure
```

Preferred behavior for the next prototype:

```text
Turkish loan-diacritic words should remain in normal learned text flow.
They should not be protected like URLs/files/code/foreign spans.
```

Legacy artifacts such as `ý`, `þ`, `ð`, and `Ý` are a separate data-quality
case. They are present but do not dominate the route.

## Decision

Before MorphBPE or boundary-biased Viterbi:

```text
1. Add a Turkish loan-diacritic pass-through/reroute rule.
2. Re-run finite_protected_sp64_floor token-pressure audit.
3. Confirm protected stress remains 25/25.
4. Then continue with vocab coverage and decode-time boundary bias.
```

Expected effect:

```text
lower finite protected tokens/raw byte
little or no harm to protected stress
better separation between true protected spans and normal Turkish prose
```
