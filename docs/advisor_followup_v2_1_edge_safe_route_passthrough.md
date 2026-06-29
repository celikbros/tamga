# Advisor Follow-Up: v2.1 Edge-Safe Protected Sidecar Candidate

Date: 2026-06-12

> Superseded note: the requested 20M fixed-byte run has now been completed.
> Send `docs/advisor_followup_v2_1_edge_safe_20m_result.md` for the current
> advisor question. This file is kept as pre-20M context.

## Context

You warned that our all-route SP passthrough row was semantically ambiguous:

```text
logical protected bookkeeping is not enough if SP pieces cross protected span
edges in the model-token stream
```

We accepted that critique and added boundary-alignment and exact-roundtrip
audits.

## New Findings

### Inline all-route SP passthrough

This row is almost as cheap as bare SP64:

```text
valid/test tokens/raw byte: 0.159027 / 0.159668
exact roundtrip: valid/test 100%
```

But it fails protected edge alignment:

| Split | Edge alignment rate | Misaligned edges | Crossing pieces |
| --- | ---: | ---: | ---: |
| valid | 0.453798 | 10427 | 9447 |
| test | 0.463721 | 9904 | 9014 |

We now treat it as a compression ablation only.

### Isolated all-route SP passthrough

This row fixes edge alignment:

```text
valid/test edge alignment: 1.000000
crossing pieces: 0
```

But it breaks IDs-only exact decode due SentencePiece dummy-prefix/whitespace
semantics:

```text
valid exact: 484/1994
test exact: 526/1998
```

We now treat it as an alignment ablation only.

### Edge-safe all-route SP passthrough

We added a third route mode:

```text
full-line SP64 encode
+ protected sidecar spans
+ UTF-8 byte fallback for SP pieces crossing protected span edges
+ UTF-8 byte fallback for SP <unk> pieces
```

Result:

| Split | Tokens/raw byte | Exact roundtrip | Edge alignment | Crossing pieces | Fallback source rate |
| --- | ---: | --- | ---: | ---: | ---: |
| valid | 0.169341 | 1994/1994 | 1.000000 | 0 | 0.080549 |
| test | 0.169791 | 1998/1998 | 1.000000 | 0 | 0.078995 |

Relevant reports:

```text
docs/v2_0_route_sp_passthrough_findings.md
docs/advisor_feedback_v2_0_route_sp_passthrough_triage.md
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
artifacts/v2_0_tiny_lm_route_sp_passthrough_all_routes_edge_safe_dry_run.md
artifacts/v2_0_route_sp_passthrough_all_routes_edge_safe_roundtrip_valid.md
artifacts/v2_0_route_sp_passthrough_all_routes_edge_safe_roundtrip_test.md
artifacts/v2_0_protected_boundary_alignment_all_routes_edge_safe_audit.md
```

## Current Interpretation

The edge-safe row is the first route-passthrough variant that satisfies:

```text
exact decode
protected edge alignment
no crossing SP pieces
near-acceptable token pressure
```

It is not a morphology-improving tokenizer. It is a cleaner protected-wrapper
baseline candidate for v2.1.

The cost is visible:

```text
test tokens/raw byte: 0.169791
fallback source rate: ~7.9% of tokens
```

This is higher than the current repaired numeric-SP floor, but semantically
cleaner under sidecar protection.

## Questions

Please be critical.

1. Is this edge-safe sidecar contract sufficient for an experimental LLM
   tokenizer baseline?

2. Is the byte-fallback crossing-piece policy acceptable, or is the fallback
   rate high enough that this should remain only an audit mechanism?

3. Should we rename/promote it as:

```text
sp64_protected_edge_safe_sidecar
```

rather than any `finite_protected_*` name?

4. Should the next step be a 20M fixed-byte tiny-LM row for edge-safe versus:

```text
bare SP64
finite_protected_sp64_numeric_sp_floor
```

or should we first run a detector stress battery?

5. Does this change your recommendation about the broader roadmap?

Our current plan:

```text
Do not reopen morphology-tokenizer sweeps.
Treat edge-safe sidecar as a v2.1 protected-baseline candidate.
Run detector stress + one 20M calibration before replacing the practical floor.
Keep morphology as auxiliary/diagnostic unless a selective mechanism avoids
static token-pressure tax.
```

Please challenge this plan.
