# Advisor Feedback Triage: Lambda 0 Decomposition And Roundtrip Failure

Date: 2026-06-10

## Verdict

Advisor feedback is accepted.

The boundary-biased runtime decoder branch is not promoted. Longer BPB runs are
blocked until exact roundtrip is fixed, or the branch is explicitly demoted to
diagnostic-only evidence for a future training-time objective.

The current status is:

```text
boundary-biased lambda rows are scientifically suggestive
but not valid LLM-tokenizer candidates while exact roundtrip fails
```

## Consensus

All advisors converged on the same core point:

```text
decode(encode(text)) != text invalidates BPB as LLM-tokenizer evidence.
```

Current smoke:

| Tokenizer | Exact | Failures | Exact rate |
| --- | ---: | ---: | ---: |
| SP64 bare | 20/20 | 0 | 1.000000 |
| boundary-biased lambda 0 | 0/20 | 20 | 0.000000 |
| boundary-biased lambda 4 | 0/20 | 20 | 0.000000 |

Therefore:

```text
do not run longer/larger BPB on this runtime path yet
do not send lambda 4 to the LLM team
do not claim lambda 4 is a valid tokenizer candidate
```

## Accepted Interpretation

The lambda decomposition remains useful but provisional:

| Step | Test BPB delta | Challenge F1 delta | Current interpretation |
| --- | ---: | ---: | --- |
| floor -> lambda 0 | -0.142010 | +0.0509 | decoder/pipeline effect |
| lambda 0 -> lambda 4 | -0.047547 | +0.0279 | possible morphology penalty effect |
| lambda 4 -> lambda 8 | +0.129466 | +0.0524 | high-F1 over-segmentation effect |

Accepted claim:

```text
Within the custom decoder family, lambda 4 appears to add a morphology signal
over lambda 0 in the 300-step screen.
```

Rejected claim:

```text
lambda 4 is already a valid LLM tokenizer candidate.
```

Reason:

```text
roundtrip failure can artificially improve BPB by making the stream easier to
predict while the denominator remains raw bytes.
```

## Runtime Branch Decision

The runtime boundary-biased decoder is now treated as a research instrument,
not the production shape.

Preferred production shape, if the morphology effect survives:

```text
boundary-weighted Unigram trainer or constrained learned tokenizer objective
that emits a standard tokenizer artifact
```

The runtime decoder may be kept only for short diagnostic work if the
roundtrip issue is trivial. It should not become the default LLM-tokenizer path
unless it passes losslessness, determinism, latency, and do-no-harm gates.

## Wrapper Tax Finding

Fable5 identified a separate high-value issue:

```text
on no-protected valid lines, the protected floor averages 171.97 tokens while
official SP averages 164.30 tokens
```

This is about a 4.7% tax on clean text. It likely comes from segment-wise
encoding, dummy-prefix handling, or blocked cross-segment merges.

This matters because:

```text
fixing wrapper tax benefits every branch
it may shrink the floor -> lambda 0 gap
it is independent of morphology hype
```

## Immediate Plan

Do this next, in order:

1. Expand roundtrip/stateless audit and classify failures.
2. Audit and reduce wrapper tax on no-protected clean lines.
3. Compute normal-text-only morphology F1, excluding protected spans.
4. Run a small multilingual/noisy/code do-no-harm canary after losslessness is
   fixed or the runtime branch is demoted.
5. Only then consider longer/seeded lambda 0 vs lambda 4 BPB.

## Stop / Demote Criteria

Demote the runtime decoder branch if any of these holds:

```text
roundtrip cannot be fixed quickly and locally
lambda 4 no longer beats lambda 0 after the lossless fix
lambda 4 advantage falls within seed noise on longer runs
normal-text-only F1 gain collapses
non-Turkish/code token bloat exceeds a small threshold
decode latency or determinism is unacceptable
```

## LLM-Team Handoff Requirement

No handoff as an experimental tokenizer candidate until at least:

```text
large exact roundtrip audit passes
stateless decode is proven
wrapper-tax audit is resolved or documented
normal-text-only F1 is reported
multilingual/code do-no-harm is reported
post-fix lambda 0 vs lambda 4 BPB is re-run with seeds
claims are framed as experimental screening only
```

If the branch is demoted, the lighter handoff is not a tokenizer artifact. It
is a research note:

```text
runtime boundary bias showed a possible morphology signal,
but the runtime path failed exact roundtrip;
the signal should be moved into a boundary-weighted training objective.
```
