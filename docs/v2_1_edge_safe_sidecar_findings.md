# v2.1 Edge-Safe Protected Sidecar Findings

Date: 2026-06-12

> Superseded note: Fable5 correctly pointed out that edge-safe byte fallback
> pays an avoidable implementation tax. The current successor candidate is
> `sp64_protected_presplit_sidecar`; see
> `docs/v2_1_presplit_sidecar_findings.md`.

## Context

Fable5 pointed out that our earlier all-route SP passthrough result was
semantically under-specified. It preserved exact decode and logical protected
bookkeeping, but SP pieces often crossed protected span edges.

We split the problem into three separate properties:

```text
exact roundtrip
protected edge alignment
token pressure / BPB
```

## Candidate

Current v2.1 candidate:

```text
sp64_protected_edge_safe_sidecar
```

Mechanism:

```text
normal text: full-line SP64
protected spans: sidecar/logical bookkeeping
crossing SP pieces: UTF-8 byte fallback
SP <unk> pieces: UTF-8 byte fallback
```

This is not a morphology-improving tokenizer. It is a protected-wrapper
baseline candidate.

## Safety Checks

| Check | Valid | Test |
| --- | ---: | ---: |
| exact roundtrip | 1994/1994 | 1998/1998 |
| protected edge alignment | 1.000000 | 1.000000 |
| crossing pieces | 0 | 0 |

Token pressure:

| Split | Tokens/raw byte | Fallback source tokens | Fallback source rate |
| --- | ---: | ---: | ---: |
| train | 0.165138 | 313768 | 0.083263 |
| valid | 0.169341 | 38783 | 0.080549 |
| test | 0.169791 | 37314 | 0.078995 |

Reports:

```text
artifacts/v2_0_tiny_lm_route_sp_passthrough_all_routes_edge_safe_dry_run.md
artifacts/v2_0_route_sp_passthrough_all_routes_edge_safe_roundtrip_valid.md
artifacts/v2_0_route_sp_passthrough_all_routes_edge_safe_roundtrip_test.md
artifacts/v2_0_protected_boundary_alignment_all_routes_edge_safe_audit.md
```

## 20M Tiny-LM Result

Same tiny LM family as the previous 20M curve:

```text
seq_len=128
batch_size=4
d_model=256
n_layers=4
n_heads=4
fixed approximately 20M raw bytes seen
seed=20260611
```

| Candidate | Test tokens/raw byte | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 20,002,137 | 1.951192 | 1.962704 | 11.9316 |
| sp64_protected_edge_safe_sidecar | 0.169791 | 20,000,951 | 1.946651 | 1.957401 | 11.5283 |

Delta:

| Comparison | Test tokens/raw byte delta | Test BPB delta |
| --- | ---: | ---: |
| edge-safe sidecar vs numeric-SP floor | +0.005294 | -0.005303 |

## Reading

The BPB difference is small and should not be over-sold.

However:

```text
The semantically cleaner sidecar contract does not appear to hurt BPB at 20M.
It slightly beats the numeric-SP floor while providing stronger protected edge
alignment and exact roundtrip guarantees.
```

This changes the baseline decision more than the morphology decision.

## Decision

Do not promote `sp64_protected_edge_safe_sidecar` as the final v2.1 protected
baseline candidate. It proved the contract is implementable, but pre-splitting
achieves the same contract with lower token pressure.

Do not reopen broad morphology-tokenizer sweeps. The earlier 20M result still
says static morphology-heavy tokenization does not survive as a tokenizer
candidate.

## Next Steps

1. Run detector/protected stress for the edge-safe sidecar route.
2. Ask Fable5 whether the sidecar contract is sufficient for LLM-team
   experimental handoff.
3. If accepted, consolidate docs around v2.1:

```text
practical baseline: sp64_protected_edge_safe_sidecar
morphology: auxiliary/diagnostic path, not current tokenizer branch
```
