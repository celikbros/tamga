# v2.0 Safe UDS Findings

Date: 2026-06-10

## Summary

The safe UDS probe produced a real morphology signal without materially
increasing token pressure.

Reports:

```text
symbols: artifacts/v2_0_safe_uds_symbols.md
SP pressure: artifacts/v2_0_safe_uds_sentencepiece_probe.md
finite-protected intrinsic: artifacts/v2_0_safe_uds_finite_protected_intrinsic_eval.md
```

## Token Pressure

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| SP64 reference | 0.159020 | 0.159620 |
| safe_uds_unigram_64000 | 0.159109 | 0.159684 |

The 7 user-defined symbols did not meaningfully increase learned-tokenizer
pressure.

## Intrinsic Result

Challenge F1:

| Model | Challenge F1 | Protected stress |
| --- | ---: | --- |
| custom_tr_morph | 0.9220 | 25/25 |
| safe_uds_unigram_64000, bare | 0.7556 | 1/25 |
| finite protected + safe_uds_unigram_64000 | 0.7081 | 25/25 |

Gold Expanded F1:

| Model | Gold F1 |
| --- | ---: |
| safe_uds_unigram_64000, bare | 0.7971 |
| finite protected + safe_uds_unigram_64000 | 0.7743 |

The strongest gains appear in categories directly covered by the safe symbols:

```text
verb_future challenge F1, bare: 0.7846
suffix_chain challenge F1, bare: 0.7403
```

## Interpretation

Safe UDS is more effective than train-only seed appendix:

```text
strong seed-bias bare challenge F1: 0.7356
safe UDS bare challenge F1:        0.7556
```

This means direct symbol enforcement is a stronger lever than repeating suffix
surfaces in a synthetic appendix. It also stays far cheaper than marker-based
training views.

However, the finite-protected wrapper still lowers visible boundary F1 because
protected-span routing changes logical segmentation around code/file/URL-like
cases. The protected route is still required, but the next improvement should
focus on combining finite protected routing with a better normal-text morphology
mechanism.

## Decision

Keep safe UDS as the current best cheap structural morphology prior.

Do not run tiny-LM yet. The current finite-protected Challenge F1 is improved
but still too low to treat as a serious LLM tokenizer candidate.

The next branch should either:

```text
1. audit and cautiously expand UDS beyond the 7-symbol pool, or
2. move to a constrained/MorphBPE objective that can use the custom morphology
   teacher without forcing many suffixes as hard user-defined symbols.
```

Do not return to seed appendix or marker-dose tuning.
