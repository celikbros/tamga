# v2.0 20M Learning Curve Findings

Date: 2026-06-12

## Question

The 2M-byte ladder showed a large BPB win for:

```text
finite_protected_teacher_distilled_16000
```

But the accounting audit showed the 2M runs were still in an early-learning
regime. We therefore ran a healthier 20M-byte learning curve across:

```text
finite_protected_sp64_numeric_sp_floor
finite_protected_self_distilled_16000
finite_protected_teacher_distilled_16000
```

## Final 20M Results

| Tokenizer | Test tokens/byte | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 20,002,137 | 1.951192 | 1.962704 | 11.9316 |
| finite_protected_self_distilled_16000 | 0.164852 | 20,000,713 | 1.951182 | 1.963184 | 11.9088 |
| finite_protected_teacher_distilled_16000 | 0.177859 | 20,002,006 | 1.971752 | 1.983360 | 11.1513 |

## Health Check

All three rows are now below the uniform-vocabulary reference:

```text
log2(vocab): 15.9799
```

All three also beat their own zero-training unigram BPB baselines:

| Tokenizer | Unigram BPB | 20M test BPB |
| --- | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 2.026952 | 1.962704 |
| finite_protected_self_distilled_16000 | 2.028322 | 1.963184 |
| finite_protected_teacher_distilled_16000 | 2.111869 | 1.983360 |

So the 20M checkpoint is a healthier comparison than the 2M endpoint.

## Interpretation

`teacher_distilled_16000` has much lower bits/token:

```text
SP64 floor: 11.9316
self_distilled_16000: 11.9088
teacher_distilled_16000: 11.1513
```

But it also has much higher tokens/byte:

```text
SP64 floor: 0.164497
self_distilled_16000: 0.164852
teacher_distilled_16000: 0.177859
```

At 2M bytes, lower bits/token more than compensated for token pressure.
At 20M bytes, it no longer does.

## Decision

Do not promote `teacher_distilled_16000` as a BPB-winning tokenizer candidate.

Current status:

```text
useful diagnostic / teacher target
not a deployable tokenizer candidate on BPB evidence
not a reason to build broad reranker work immediately
```

The morphology signal is not dead:

```text
it accelerates early learning
it lowers bits/token strongly
it improves morphology diagnostics
```

But the static tokenization tax is too high in this branch:

```text
20M test BPB loses by +0.020656 versus protected SP64 floor
```

## Learning Curve Delta Check

Fable5 asked whether the 20M endpoint was a misleading single point or whether
the teacher row's early advantage actually failed to persist across the curve.
We therefore matched validation checkpoints by nearest raw-byte targets inside
the 20M runs:

```text
report: artifacts/v2_0_20m_learning_curve_delta_report.md
```

Key deltas versus `finite_protected_sp64_numeric_sp_floor`:

| Target bytes | Self valid BPB delta | Teacher valid BPB delta |
| ---: | ---: | ---: |
| 2,000,000 | -0.008624 | -0.023506 |
| 6,000,000 | +0.002403 | +0.062556 |
| 10,000,000 | +0.000727 | +0.024832 |
| 16,000,000 | -0.006937 | +0.016182 |
| 20,000,000 | -0.000010 | +0.020560 |

Reading:

```text
The teacher row's early advantage is not durable within the 20M curve.
After the early checkpoints it remains worse than the SP64 protected floor.
The clean conclusion is therefore not based on a single final endpoint.
```

## Wrapper Tax Check

We also decomposed the active protected wrapper with numeric-like spans routed
through SP passthrough:

```text
report: artifacts/v2_0_finite_protected_numeric_sp_wrapper_cost_audit.md
```

| Split | SP tokens/raw byte | Finite tokens/raw byte | Delta | Protected bytes share |
| --- | ---: | ---: | ---: | ---: |
| valid | 0.159020 | 0.171903 | +0.012883 | 0.016455 |
| test | 0.159620 | 0.172734 | +0.013113 | 0.016956 |

Route reading:

```text
numeric_like is no longer the route-cost problem because numeric SP passthrough
matches SP token count on those surfaces.

The main wrapper token tax is concentrated in file_like, apostrophe_surface,
and non_turkish_latin_word routes.
```

This means the practical baseline is valid, but still has a route-tax
optimization backlog before any LLM-team handoff.

## Bootstrap Status

Fable5 also requested paired bootstrap over test documents. The current 20M
artifacts only save global checkpoint metrics, not model checkpoints or
per-document losses:

```text
available: metrics.jsonl
missing: checkpoint weights / per-document BPB records
```

So a real paired BPB bootstrap cannot be computed from the existing artifacts.
The runner should be extended to emit per-document eval losses if we need this
for a handoff-quality confidence interval.

## Next Direction

Stop static score-distillation as a primary tokenizer route.

Keep:

```text
finite_protected_sp64_numeric_sp_floor
```

as the strict finite protected tokenizer baseline.

After the wrapper-tax audit, we also found a lower-pressure protected wrapper
variant:

```text
finite_protected_sp64_all_sp_routes
```

Report:

```text
docs/v2_0_route_sp_passthrough_findings.md
```

It gives near-SP64 token pressure with exact valid/test roundtrip and 25/25
logical protected stress:

| Candidate | Test tokens/raw byte | Valid/test roundtrip | Protected stress |
| --- | ---: | --- | --- |
| bare SP64 | 0.159620 | exact | 1/25 |
| strict numeric protected floor | 0.164497 | exact | 25/25 |
| all-route SP passthrough | 0.159668 | exact | 25/25 logical |

The remaining decision is semantic:

```text
If protected preservation may be logical/wrapper-level, all-route SP
passthrough is the best practical protected SP64 floor.

If protected spans must remain non-SP finite model-token routes, keep the
strict numeric protected floor and optimize finite route classes separately.
```

Move morphology value toward one of:

```text
1. auxiliary LM/data objective
2. selective/contextual training signal
3. targeted wrapper/route improvements
4. hidden/code-mixed robustness evaluation
```

Do not run more broad tokenizer sweeps until the next hypothesis is narrower
than "more morphology pressure helps."
