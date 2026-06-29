# Advisor Follow-Up: Route SP Passthrough Semantics

Date: 2026-06-12

> Superseded note: after Fable5's response, we added protected boundary
> alignment and edge-safe byte-fallback audits. The current follow-up to send is
> `docs/advisor_followup_v2_1_edge_safe_route_passthrough.md`. This older file
> is kept as historical context for the pre-audit question.

## Context

After the 20M learning curve, we closed `teacher_distilled_16000` as a tokenizer
candidate:

```text
SP64 protected floor test BPB: 1.962704
teacher_distilled_16000 test BPB: 1.983360
```

We accepted that static morphology-heavy scoring helps early learning and
lowers bits/token, but its token-pressure tax does not survive a healthier 20M
checkpoint.

You then asked us to inspect the protected-wrapper tax before doing any more
training.

## Strict Protected Baseline Before This Follow-Up

The active strict baseline was:

```text
finite_protected_sp64_numeric_sp_floor
```

Meaning:

```text
normal text: SP64
numeric_like protected spans: SP passthrough
other protected spans: finite selected pieces + UTF-8 fallback
```

It is exact-roundtrip and preserves protected stress:

```text
valid exact roundtrip: 1994/1994
test exact roundtrip: 1998/1998
protected stress: 25/25
```

But it still costs token pressure:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| bare SP64 | 0.159020 | 0.159620 |
| finite protected numeric-SP floor | 0.163567 | 0.164497 |

## Wrapper Tax Decomposition

Report:

```text
artifacts/v2_0_finite_protected_numeric_sp_wrapper_cost_audit.md
```

Findings:

```text
numeric_like is no longer a route-cost problem under SP passthrough.
remaining route tax concentrates in file_like, apostrophe_surface,
and non_turkish_latin_word.
```

## New Route SP Passthrough Experiment

We added:

```toml
sp_passthrough_routes = [...]
```

Mechanism:

```text
For selected protected route classes, encode the surface inline with normal
SP64 ids in the model-token stream, while the wrapper/evaluator can still
record the surface as a logical protected span.
```

This is not a morphology mechanism. It is a protected-wrapper semantics probe.

## Results

Config:

```text
configs/v2_0_tiny_lm_route_sp_passthrough.toml
```

Token pressure:

| Candidate | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: |
| bare SP64 | 0.159020 | 0.159620 |
| finite protected numeric-SP floor | 0.163567 | 0.164497 |
| high-cost route SP passthrough | 0.159067 | 0.159729 |
| all-route SP passthrough | 0.159027 | 0.159668 |

Roundtrip for all-route SP passthrough:

| Split | Exact | Failures |
| --- | ---: | ---: |
| valid | 1994/1994 | 0 |
| test | 1998/1998 | 0 |

Protected stress for all-route SP passthrough:

```text
25/25 logical protected spans preserved
```

Intrinsic:

```text
Challenge F1 remains 0.6755.
This branch removes token pressure but does not improve Turkish morphology.
```

Reports:

```text
docs/v2_0_route_sp_passthrough_findings.md
artifacts/v2_0_tiny_lm_route_sp_passthrough_all_routes_dry_run.md
artifacts/v2_0_route_sp_passthrough_all_routes_roundtrip_valid.md
artifacts/v2_0_route_sp_passthrough_all_routes_roundtrip_test.md
artifacts/v2_0_finite_protected_all_sp_routes_intrinsic_eval.md
```

## Critical Caveat

All-route SP passthrough preserves:

```text
exact decode
logical/eval protected-span preservation
near-SP64 token pressure
```

But it does not preserve protected spans as atomic/non-SP model-token routes:

```text
the LM still sees SP pieces inside file/code/URL/non-Turkish protected surfaces
```

So the central question is semantic, not numeric.

## Questions

Please be critical.

1. Is logical protected preservation plus exact roundtrip sufficient for an
   experimental LLM tokenizer handoff, or must protected spans remain protected
   in the model-token stream itself?

2. Is the all-route SP passthrough row a valid "protected SP64 floor", or is it
   misleading because protected stress is now partly an evaluator/wrapper
   abstraction rather than a property of the raw model-token stream?

3. If model-token atomicity is required, which routes truly need finite
   treatment?

```text
file_like
URL/package/code-ish spans
apostrophe_surface
non_turkish_latin_word
numeric_like
Arabic/Cyrillic/Greek/etc.
```

4. Would you recommend:

```text
A. promote all-route SP passthrough as the practical baseline
B. keep strict finite protected numeric-SP floor as the baseline
C. maintain both: one logical-protected baseline and one strict model-token baseline
D. redesign protected routing around a sidecar/span table rather than token IDs
E. something else
```

5. Does this change the next research step?

Our current thinking:

```text
Do not run more morphology-tokenizer BPB sweeps.
First decide protected-span semantics.
If logical protection is enough, consolidate all-route SP passthrough as the
practical protected SP64 floor.
If strict model-token protection is required, optimize finite route classes
separately and keep morphology work out of the tokenizer for now.
```

Please challenge this framing.
