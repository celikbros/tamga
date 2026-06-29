# v2.0 Route SP Passthrough Findings

Date: 2026-06-12

## Question

After the 20M BPB curve closed `teacher_distilled_16000` as a tokenizer
candidate, Fable5 asked us to decompose the remaining protected-wrapper token
tax and to clarify what "protected" means.

The important distinction is now:

```text
logical/eval protected span preservation
vs
model-token boundary alignment
vs
model-token atomicity
```

Bare SP64 is compression-efficient but is not a lossless/protected tokenizer
contract in this project.

## Baselines

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Roundtrip | Protected boundary alignment |
| --- | ---: | ---: | --- | --- |
| bare SP64 | 0.159020 | 0.159620 | valid 1985/1994, test 1989/1998 | not protected |
| finite protected numeric-SP floor | 0.163567 | 0.164497 | valid/test 100% | not fully audited under v2.1 sidecar semantics |
| inline all-route SP passthrough | 0.159027 | 0.159668 | valid/test 100% | fails badly |
| isolated all-route SP passthrough | 0.165282 | 0.165776 | fails badly | valid/test 100% |
| edge-safe all-route SP passthrough | 0.169341 | 0.169791 | valid/test 100% | valid/test 100% |

## Wrapper Tax Audit

Report:

```text
artifacts/v2_0_finite_protected_numeric_sp_wrapper_cost_audit.md
```

The numeric route is no longer the main strict-route token-cost problem:

```text
numeric_like protected tokens == SP tokens on same surfaces
```

The remaining strict finite-route tax concentrates in:

```text
file_like
apostrophe_surface
non_turkish_latin_word
```

## Route SP Passthrough Ablations

We added:

```toml
sp_passthrough_routes = [...]
```

This lets selected protected route surfaces use normal SP64 ids while the
wrapper/evaluator can still track the surface as a logical protected span.

### Inline all-route passthrough

Inline passthrough is almost as cheap as bare SP64:

```text
valid/test tokens/raw byte: 0.159027 / 0.159668
roundtrip: valid/test 100%
```

But it fails Fable5's sidecar safety condition. Protected span edges are often
inside SP pieces:

| Split | Edge alignment rate | Misaligned edges | Crossing pieces |
| --- | ---: | ---: | ---: |
| valid | 0.453798 | 10427 | 9447 |
| test | 0.463721 | 9904 | 9014 |

Reports:

```text
artifacts/v2_0_tiny_lm_route_sp_passthrough_all_routes_dry_run.md
artifacts/v2_0_route_sp_passthrough_all_routes_roundtrip_valid.md
artifacts/v2_0_route_sp_passthrough_all_routes_roundtrip_test.md
artifacts/v2_0_protected_boundary_alignment_audit.md
```

Decision:

```text
Do not promote inline all-route passthrough as a protected tokenizer contract.
It is only a compression ablation.
```

### Isolated all-route passthrough

Isolating SP passthrough routes fixes boundary alignment:

```text
valid/test edge alignment: 1.000000
crossing pieces: 0
```

But it breaks IDs-only exact decode because isolated SentencePiece chunks carry
dummy-prefix whitespace semantics:

```text
valid exact: 484/1994
test exact: 526/1998
```

Reports:

```text
artifacts/v2_0_tiny_lm_route_sp_passthrough_all_routes_isolated_dry_run.md
artifacts/v2_0_route_sp_passthrough_all_routes_isolated_roundtrip_valid.md
artifacts/v2_0_route_sp_passthrough_all_routes_isolated_roundtrip_test.md
artifacts/v2_0_protected_boundary_alignment_all_routes_isolated_audit.md
```

Decision:

```text
Do not promote isolated passthrough. It is an alignment ablation only.
```

### Edge-safe all-route passthrough

Edge-safe passthrough keeps full-line SP behavior except when an SP piece would
cross a protected span edge. Crossing pieces, plus SP `<unk>` pieces, are encoded
with UTF-8 byte fallback ids.

This satisfies the current v2.1 contract:

```text
exact roundtrip
protected edge alignment
no crossing pieces
```

| Split | Tokens/raw byte | Fallback source tokens | Fallback source rate | Exact roundtrip | Edge alignment | Crossing pieces |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| valid | 0.169341 | 38783 | 0.080549 | 1994/1994 | 1.000000 | 0 |
| test | 0.169791 | 37314 | 0.078995 | 1998/1998 | 1.000000 | 0 |

Reports:

```text
artifacts/v2_0_tiny_lm_route_sp_passthrough_all_routes_edge_safe_dry_run.md
artifacts/v2_0_route_sp_passthrough_all_routes_edge_safe_roundtrip_valid.md
artifacts/v2_0_route_sp_passthrough_all_routes_edge_safe_roundtrip_test.md
artifacts/v2_0_protected_boundary_alignment_all_routes_edge_safe_audit.md
```

## Current Decision

The earlier "all-route SP passthrough is nearly free" reading was too weak
semantically. It preserved exact decode and logical bookkeeping, but not
protected model-token boundaries.

Current decision:

```text
inline all-route passthrough: closed as unsafe for sidecar protection
isolated all-route passthrough: closed as non-lossless
edge-safe all-route passthrough: keep as v2.1 candidate/baseline
```

Edge-safe is not a morphology improvement. It is a better protected-wrapper
contract candidate. It costs more than the repaired numeric-SP floor, but it is
the first route-passthrough row that satisfies exact roundtrip and protected
edge alignment at the same time.

## 20M Tiny-LM Check

We ran the requested fixed-byte check for the edge-safe row:

```text
report: artifacts/v2_1_tiny_lm_edge_safe_sidecar_20mbytes.md
config: configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
```

| Candidate | Test tokens/raw byte | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite protected numeric-SP floor | 0.164497 | 20,002,137 | 1.951192 | 1.962704 | 11.9316 |
| sp64 protected edge-safe sidecar | 0.169791 | 20,000,951 | 1.946651 | 1.957401 | 11.5283 |

Delta versus numeric-SP floor:

```text
test tokens/raw byte: +0.005294
test BPB: -0.005303
```

Reading:

```text
The BPB win is small, so this is not a language-modeling breakthrough.
But the semantically cleaner protected-sidecar row did not pay a BPB penalty at
20M; it slightly beats the current numeric-SP floor in this tiny-LM checkpoint.
```

## Next Gate

Before this replaces the practical baseline, complete the v2.1 safety checks:

```text
SP64 bare
finite_protected_sp64_numeric_sp_floor
sp64_protected_edge_safe_sidecar
```

Config:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
```

Required checks:

```text
exact roundtrip valid/test
protected boundary alignment valid/test
protected stress 25/25
detector stress battery
```

If detector stress passes, rename this family away from the overloaded
`finite_protected_*` label:

```text
sp64_protected_edge_safe_sidecar
```
