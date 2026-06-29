# v2.5 Wider Robustness Closeout

Date: 2026-06-14

## Status

v2.5 is closed as a decision phase.

We do not need to run another broad robustness sweep before preparing the v3.0
experimental handoff package.

## Evidence Already Covering v2.5 Risk

The v2.x hardening path already includes:

| Area | Evidence | Status |
| --- | --- | --- |
| exact encode/decode | full real-mix v2.2 smoke, 40388/40388 exact | PASS |
| sidecar offsets | full real-mix v2.2 smoke, sidecar failures 0 | PASS |
| schema contract | v2.3 schema audit, 40388 records / 149999 spans | PASS |
| consumer operations | v2.4 copy/redaction/token-mask simulation | PASS |
| masking overhead | extra mask bytes/raw byte 0.003983 | PASS |
| detector battery | 61 adversarial cases / 62 expected spans | PASS |
| LM-loss reference | v2.1 passthrough 20M BPB row | present |
| route regression | percent_encoded and azerbaijani_word invariants | locked |

## Why No Additional v2.5 Run

The remaining optional checks would be useful for production hardening but are
not required for an experimental LLM-team handoff:

```text
larger/private pretraining sample smoke
throughput benchmark
route-selective pre-split what-if
consumer simulation inside the real LLM dataloader
```

Those belong to either:

```text
LLM-team integration validation
production-readiness work after experimental handoff
```

They should not block v3.0 experimental packaging.

## Still Not Claimed

v2.5 does not claim:

```text
final production tokenizer readiness
token-boundary protected spans
exact constrained decoding/copy by token ids
morphology-improved tokenizer behavior
throughput suitability for a production tokenizer service
```

## Decision

The required v2.x path is now complete enough to prepare:

```text
v3.0 experimental LLM handoff package
```

If the LLM team later requires token-boundary span copy or constrained decoding,
open a new route-selective pre-split branch instead of changing the v3.0
passthrough baseline silently.
