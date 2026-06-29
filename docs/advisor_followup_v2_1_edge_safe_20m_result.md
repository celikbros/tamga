# Advisor Follow-Up: v2.1 Edge-Safe Sidecar 20M Result

Date: 2026-06-12

> Superseded note: Fable5's response identified an avoidable implementation
> tax in the edge-safe byte-fallback artifact. The current follow-up is
> `docs/advisor_followup_v2_1_presplit_encode_only_result.md`.

## Context

You warned that all-route SP passthrough was not a safe protected tokenizer
contract unless protected span edges align with model-token boundaries.

We accepted that critique and built an edge-safe sidecar variant.

## Candidate

```text
sp64_protected_edge_safe_sidecar
```

Mechanism:

```text
normal text: full-line SP64
protected spans: sidecar/logical bookkeeping
SP pieces crossing protected span edges: UTF-8 byte fallback
SP <unk> pieces: UTF-8 byte fallback
```

## Safety Results

| Check | Valid | Test |
| --- | ---: | ---: |
| exact roundtrip | 1994/1994 | 1998/1998 |
| protected edge alignment | 1.000000 | 1.000000 |
| crossing pieces | 0 | 0 |

Token pressure:

| Split | Tokens/raw byte | Fallback source rate |
| --- | ---: | ---: |
| valid | 0.169341 | 0.080549 |
| test | 0.169791 | 0.078995 |

## 20M Fixed-Byte Tiny-LM Result

Same model family and seed as the previous 20M curve:

```text
seq_len=128
batch_size=4
d_model=256
n_layers=4
n_heads=4
seed=20260611
approximately 20M raw bytes seen
```

| Candidate | Test tokens/raw byte | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite protected numeric-SP floor | 0.164497 | 20,002,137 | 1.951192 | 1.962704 | 11.9316 |
| sp64 protected edge-safe sidecar | 0.169791 | 20,000,951 | 1.946651 | 1.957401 | 11.5283 |

Delta:

```text
test tokens/raw byte: +0.005294
test BPB: -0.005303
```

## Current Reading

The BPB win is small, so we do not read it as a strong LM-quality result.

But it is important that the semantically cleaner protected sidecar contract
does not lose BPB at 20M. It slightly beats the current numeric-SP floor while
also satisfying exact roundtrip and protected edge alignment.

## Questions

Please be critical.

1. Is this enough to promote `sp64_protected_edge_safe_sidecar` as the v2.1
   protected baseline candidate?

2. Is the fallback source rate of about 8% acceptable for an experimental LLM
   tokenizer baseline, given that the 20M BPB did not regress?

3. Should detector/protected stress be the only remaining blocker before we
   consolidate the v2.1 baseline, or would you require a second seed?

4. Does this change the roadmap?

Our current interpretation:

```text
baseline path: consolidate edge-safe protected sidecar
morphology path: keep as auxiliary/diagnostic, not as current tokenizer branch
```

5. What exact handoff contract would you write for the LLM team?

Please challenge this before we rename/consolidate the baseline.
