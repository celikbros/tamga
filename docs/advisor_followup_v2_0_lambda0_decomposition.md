# Advisor Follow-Up: Lambda 0 Decomposition After Boundary-Biased Decode

Date: 2026-06-10

## Context

You warned that our boundary-biased lambda 4 result might be confounded because
lambda 0 already differs from official SentencePiece / the finite protected
floor.

We accepted that critique and ran the missing lambda 0 tiny-LM BPB row.

## New Result

Same tiny-LM setup:

```text
seq_len=128
batch_size=4
max_steps=300
d_model=256
n_layers=4
n_heads=4
```

| Candidate | Test tokens/raw byte | Test BPB | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | --- |
| SP64 bare | 0.159620 | 4.860352 | 0.7351 | 1/25 |
| finite protected numeric-SP floor | 0.172734 | 4.911037 | 0.6913 | 25/25 |
| boundary-biased lambda 0 | 0.163839 | 4.769027 | 0.7422 | 25/25 |
| boundary-biased lambda 4 | 0.164686 | 4.721480 | 0.7701 | 25/25 |
| boundary-biased lambda 8 | 0.179299 | 4.850946 | 0.8225 | 25/25 |

## Decomposition

| Step | Test tokens/raw byte delta | Test BPB delta | Challenge F1 delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| floor -> lambda 0 | -0.008895 | -0.142010 | +0.0509 | decoder/pipeline effect |
| lambda 0 -> lambda 4 | +0.000847 | -0.047547 | +0.0279 | morphology boundary penalty effect |
| lambda 4 -> lambda 8 | +0.014613 | +0.129466 | +0.0524 | high-F1 over-segmentation effect |

Our current honest interpretation:

```text
The advisor warning was correct: most of the protected-floor -> lambda4 BPB gain
is already present at lambda0.

However, lambda4 is not empty. Within the custom decoder family, lambda4 gives
a smaller but positive 300-step BPB gain and F1 gain over lambda0 at very small
extra token pressure.
```

## Alignment Audit Already Run

We also ran a valid-split decoder alignment audit:

```text
report: artifacts/v2_0_boundary_decoder_alignment_audit_valid.md
```

Summary:

| Comparison | Lines | Exact | Mismatch rate | Avg lhs tokens | Avg rhs tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| floor_vs_lambda0_all | 1994 | 0/1994 | 1.000000 | 244.1214 | 231.6434 |
| floor_vs_lambda0_no_protected | 484 | 0/484 | 1.000000 | 171.9669 | 163.4380 |
| official_sp_vs_lambda0_no_protected | 484 | 0/484 | 1.000000 | 164.2955 | 163.4380 |

Visible mismatches are often punctuation / dummy-prefix / segment-boundary
behavior, not only protected routing.

## Current Decision

We are not promoting lambda 4 yet.

We are also not returning to marker-dose tuning, broad UDS, or seed appendix.

## New Roundtrip Smoke

After preparing this decomposition, we added a first exact-roundtrip smoke:

```text
script: scripts/audit_v2_boundary_roundtrip.py
SP64 report: artifacts/v2_0_boundary_encoder_roundtrip_audit_sp64_smoke.md
lambda report: artifacts/v2_0_boundary_encoder_roundtrip_audit_smoke.md
```

First 20 valid lines:

| Tokenizer | Exact | Failures | Exact rate |
| --- | ---: | ---: | ---: |
| SP64 bare | 20/20 | 0 | 1.000000 |
| boundary-biased lambda 0 | 0/20 | 20 | 0.000000 |
| boundary-biased lambda 4 | 0/20 | 20 | 0.000000 |

Failures appear to involve whitespace / punctuation / apostrophe /
segment-boundary reconstruction. This suggests that the boundary-biased path is
not currently a valid lossless LLM tokenizer path, even though its BPB is
promising.

## Questions

Please be critical.

1. Does the lambda 0 result change your recommendation?

```text
lambda0 explains most BPB gain, but lambda4 still beats lambda0 by -0.047547
test BPB and +0.0279 Challenge F1 in the 300-step screen.
```

Is this enough to keep the morphology-bias branch alive, or should we treat it
as too small/noisy until longer runs?

2. Given the roundtrip smoke failure, should all longer BPB experiments be
blocked until this path is exact-roundtrip?

3. Should we now prioritize:

```text
A. roundtrip/stateless decode audit
B. official-SP parity work for lambda0
C. longer/seeded BPB: lambda0 vs lambda4
D. normal-text-only morphology F1
E. multilingual/noisy do-no-harm canary
```

What exact order would you run these in?

4. Is exact official-SP parity at lambda0 actually required if this is treated
as a new alternative encoder family, or is it enough to:

```text
document lambda0 as the in-family baseline,
prove lossless roundtrip,
prove determinism,
and compare lambda4 against lambda0?
```

5. If lambda4 continues to beat lambda0 on longer/seeded BPB, would you keep a
runtime boundary-biased encoder as a valid experimental tokenizer, or still move
the prior into a boundary-weighted Unigram trainer for production shape?

6. What would be your stop criterion now?

Candidate examples:

```text
roundtrip failure
lambda4 no longer beats lambda0 beyond seed noise
lambda4 hidden F1 drops sharply
non-Turkish / code-mixed token bloat exceeds a small threshold
decoder latency is unacceptable
```

7. What is the minimum package you would send to the LLM team as an
experimental candidate if this branch survives?

Please include required reports, not just high-level advice.
