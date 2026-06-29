# Advisor Feedback Triage: v2.0 Boundary-Biased Decode

Date: 2026-06-10

## Verdict

The advisor feedback is accepted.

The boundary-biased lambda 4 result is promising, but it must not be promoted as
the v2.0 candidate yet. The reason is attribution:

```text
lambda 0 already differs from official SentencePiece / finite floor behavior.
```

Therefore the lambda 4 gain currently mixes:

```text
decoder/pipeline effect
+ morphology boundary penalty effect
```

The project should freeze promotion and run attribution/correctness audits
before any larger engineering or LLM-team handoff work.

## Advisor Points We Accept

1. `lambda 0` is the key control row.
2. The current custom Viterbi path is not SentencePiece-equivalent at lambda 0.
3. Tiny-LM BPB for lambda 4 is encouraging but not sufficient for promotion.
4. Protected-span correctness and morphology F1 should be reported separately.
5. Roundtrip/stateless decode and multilingual do-no-harm remain mandatory.
6. Lambda 8 should remain a high-F1/high-cost reference, not the main candidate.

## New Alignment Audit

Implemented:

```text
scripts/audit_v2_boundary_decoder_alignment.py
```

Full valid split report:

```text
artifacts/v2_0_boundary_decoder_alignment_audit_valid.md
```

Summary:

| Comparison | Lines | Exact | Mismatch rate | Avg lhs tokens | Avg rhs tokens | RHS shorter | RHS longer | Same-len diff |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| floor_vs_lambda0_all | 1994 | 0/1994 | 1.000000 | 244.1214 | 231.6434 | 1942 | 0 | 52 |
| floor_vs_lambda0_no_protected | 484 | 0/484 | 1.000000 | 171.9669 | 163.4380 | 447 | 0 | 37 |
| official_sp_vs_lambda0_no_protected | 484 | 0/484 | 1.000000 | 164.2955 | 163.4380 | 238 | 92 | 154 |

Interpretation:

```text
The lambda 0 custom Viterbi path is systematically different.
The difference is not only protected routing.
Even no-protected lines differ from official SP.
Many visible samples point to punctuation / dummy-prefix / segment-boundary
handling differences.
```

This validates the advisor warning.

## Revised Interpretation Of Earlier Results

Old interpretation:

```text
lambda 4 proves morphology-biased decoding improves BPB.
```

Revised interpretation:

```text
lambda 4 is promising, but the BPB gain is not yet attributable specifically
to morphology. It may be partly or mostly caused by the lambda 0 custom decoder
path.
```

What remains valid:

```text
SP64 morph-surface vocabulary coverage is high.
marker-dose / broad UDS / seed appendix are still not the next best levers.
decode/objective-level preference remains the most promising research direction.
```

What is now blocked:

```text
No promotion of lambda 4 as v2.0 main candidate.
No LLM-team handoff.
No constrained objective implementation based solely on lambda 4 BPB.
```

## Lambda 0 Tiny-LM Result

The missing lambda 0 control row has been run:

```text
report: artifacts/v2_0_tiny_lm_marker_calibration_boundary_lambda0_300steps.md
decomposition: artifacts/v2_0_boundary_biased_lambda_decomposition.md
```

| Candidate | Test tokens/raw byte | Test BPB | Challenge F1 | Protected |
| --- | ---: | ---: | ---: | --- |
| finite protected numeric-SP floor | 0.172734 | 4.911037 | 0.6913 | 25/25 |
| boundary-biased lambda 0 | 0.163839 | 4.769027 | 0.7422 | 25/25 |
| boundary-biased lambda 4 | 0.164686 | 4.721480 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.179299 | 4.850946 | 0.8225 | 25/25 |

Decomposition:

| Step | Test tokens/raw byte delta | Test BPB delta | Challenge F1 delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| floor -> lambda 0 | -0.008895 | -0.142010 | +0.0509 | decoder/pipeline effect |
| lambda 0 -> lambda 4 | +0.000847 | -0.047547 | +0.0279 | morphology boundary penalty effect |
| lambda 4 -> lambda 8 | +0.014613 | +0.129466 | +0.0524 | high-F1 over-segmentation effect |

Interpretation:

```text
Advisor concern confirmed: most of the protected-floor -> lambda4 BPB gain is
already present at lambda0.

Morphology signal is still visible: lambda4 improves over lambda0 in both BPB
and F1 in this 300-step screen, but the effect is smaller than the decoder /
pipeline effect.
```

## Roundtrip Smoke

Implemented:

```text
scripts/audit_v2_boundary_roundtrip.py
```

Smoke reports:

```text
artifacts/v2_0_boundary_encoder_roundtrip_audit_sp64_smoke.md
artifacts/v2_0_boundary_encoder_roundtrip_audit_smoke.md
```

Result on the first 20 valid lines:

| Tokenizer | Exact | Failures | Exact rate |
| --- | ---: | ---: | ---: |
| SP64 bare | 20/20 | 0 | 1.000000 |
| boundary-biased lambda 0 | 0/20 | 20 | 0.000000 |
| boundary-biased lambda 4 | 0/20 | 20 | 0.000000 |

Interpretation:

```text
The raw SP64 model is lossless on this smoke.
The boundary-biased mixed encoder path is not lossless.
Failures are concentrated around whitespace, punctuation, apostrophes, and
segment-boundary reconstruction.
```

This is now the main blocker. Longer BPB runs are not useful until the
boundary-biased path either becomes exact-roundtrip or is demoted to a
diagnostic-only mechanism for a future training-time objective.

## Follow-Up Advisor Consensus

Follow-up advisor feedback after the lambda 0 decomposition and roundtrip smoke
is accepted:

```text
the runtime boundary-biased decoder is demoted from candidate status
all longer BPB is blocked while roundtrip fails
lambda4 remains useful only as a diagnostic morphology-prior signal
production shape, if the signal survives, should be a boundary-weighted
Unigram/constrained learned objective rather than a custom runtime decoder
```

Additional high-priority issue:

```text
wrapper tax exists even on no-protected clean lines
```

The no-protected alignment audit showed the finite protected floor using about
171.97 tokens where official SP uses about 164.30 on the same lines. This
suggests segment-wise encoding / dummy-prefix / boundary handling is adding
avoidable token pressure. This should be audited and reduced independently of
the lambda branch.

## Immediate Next Steps

1. Keep the lambda decomposition explicit in every report:

```text
finite protected floor -> lambda 0: decoder/pipeline effect
lambda 0 -> lambda 4: morphology penalty effect
lambda 4 -> lambda 8: high-F1 over-segmentation effect
```

2. Classify boundary-biased roundtrip failures and decide whether the fix is
   local/trivial.
3. Audit and reduce wrapper tax on no-protected clean lines.
4. Separate morphology F1 from protected-span scoring.
5. Add a small multilingual/noisy do-no-harm canary before handoff.
6. Only after correctness audits, run longer/seeded BPB for lambda 0 vs lambda
   4.

## Decision Gate

Lambda 4 can be reconsidered only if:

```text
lambda 4 beats lambda 0 on BPB beyond noise,
lambda 4 keeps token pressure near lambda 0,
the visible F1 gain survives a hidden/heldout check,
roundtrip/stateless decode passes,
non-Turkish do-no-harm is acceptable.
```

If lambda 0 already explains most or all BPB improvement, then the claim must
change:

```text
not "morphology explains the whole BPB gain",
but "the custom decoder/pipeline explains most of the gain; within that decoder
family, morphology penalty improves F1 and gives a smaller extra 300-step BPB
gain."
```

That would still be research-useful, but it is a different claim.
