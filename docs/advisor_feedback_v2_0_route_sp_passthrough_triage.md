# Advisor Feedback Triage: Route SP Passthrough Semantics

Date: 2026-06-12

## Advisor Point

Fable5's core correction was that we had overloaded "protected" with three
different meanings:

```text
1. vocab-training hygiene
2. logical/eval span bookkeeping
3. model-token stream safety
```

Inline all-route SP passthrough was numerically attractive, but calling it
`finite_protected_*` was misleading unless model-token boundaries also align
with protected-span edges.

## What We Tested After The Feedback

We added two audits:

```text
scripts/audit_v2_protected_boundary_alignment.py
scripts/audit_v2_boundary_roundtrip.py
```

We also added an edge-safe route mode to the tiny-LM encoder:

```toml
byte_fallback_crossing_pieces = true
```

Meaning:

```text
Use normal SP ids unless an SP piece crosses a protected span edge.
If it crosses, encode that piece with UTF-8 byte fallback ids.
Also byte-fallback SP <unk> pieces to keep exact decode.
```

## Results

| Candidate | Test tokens/raw byte | Exact roundtrip | Protected edge alignment | Reading |
| --- | ---: | --- | --- | --- |
| inline all-route SP passthrough | 0.159668 | 1998/1998 | 0.463721 | cheap but unsafe for sidecar protection |
| isolated all-route SP passthrough | 0.165776 | 526/1998 | 1.000000 | aligned but non-lossless |
| edge-safe all-route SP passthrough | 0.169791 | 1998/1998 | 1.000000 | viable v2.1 semantics candidate |

Valid split for edge-safe:

```text
tokens/raw byte: 0.169341
exact roundtrip: 1994/1994
edge alignment: 1.000000
crossing pieces: 0
```

## Decision

The advisor correction was right. The near-SP64 inline row is not a valid
protected tokenizer contract.

The current survivor is:

```text
sp64_protected_edge_safe_sidecar
```

But the name should change if promoted, because this is not "finite protected"
in the old atomic-token sense. It is better described as:

```text
SP64 + protected sidecar + edge-safe byte fallback
```

## Impact On Roadmap

This does not reopen morphology-tokenizer sweeps.

It creates a cleaner v2.1 baseline question:

```text
Can edge-safe sidecar protection replace strict finite route protection as the
practical LLM tokenizer baseline?
```

Before asking that question with BPB, we need:

```text
detector stress battery
protected stress 25/25
one 20M fixed-byte tiny-LM row for edge-safe
clear handoff contract
```

Prepared config:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
```
