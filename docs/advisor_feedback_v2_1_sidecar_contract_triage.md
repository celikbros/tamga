# Advisor Feedback Triage: v2.1 Sidecar Contract

Date: 2026-06-13

## Question

We asked whether v2.1 should use:

```text
B. sp64_protected_passthrough_sidecar
   logical byte-span metadata, no token-boundary guarantee, cheaper

A. sp64_protected_presplit_sidecar
   token-boundary-aligned protected spans, about +3.8% tokens/raw byte
```

## Advisor Split

| Advisor | Pick | Main reason |
| --- | --- | --- |
| GeminiFlashExt | B | Byte sidecar is enough; detector/model-token decoupling matters more |
| GeminiPro | A | Token-index masking/redaction/constrained decoding should be exact |
| Grok43 | A | Training/inference tooling is token-indexed; alignment simplifies safety/copy |
| Qwen37Plus | B | Detector coupling and permanent compute tax are worse than dataloader complexity |
| Fable5 | B | Conservative choice is reversible; exact-copy/constrained decoding is the only real flip condition |

## Key Distinction

The disagreement is not about whether pre-split works. It does:

```text
roundtrip: valid/test 100%
protected edge alignment: 1.000000
detector adversarial battery: precision/recall/F1 = 1.000000
```

The disagreement is about whether token-boundary alignment is a base-tokenizer
requirement.

## Reading

A is justified if protected spans must be manipulated as exact token-index
regions during base-model training or generation:

```text
exact token-span copy
grammar/constrained decoding over protected entities
PII/security tooling that cannot tolerate over-masking boundary tokens
token-index-only infrastructure with no byte-offset reconciliation
```

B is justified if protected spans can be handled as exact byte spans in sidecar
metadata:

```text
raw-text redaction before tokenization
decode-then-redact output handling
training-time over-masking of straddling boundary tokens
byte-offset-aware dataloader/tooling
detector updates without changing model-token distribution
```

## Decision

Use `sp64_protected_passthrough_sidecar` as the v2.1 baseline.

Reasons:

```text
1. It is lossless and exact-roundtrip.
2. It has near-SP64 token pressure: test tokens/raw byte 0.159660.
3. It avoids the permanent +3.8% token tax.
4. It decouples the model-token stream from an evolving detector.
5. PII/redaction can be handled by byte-sidecar and conservative over-masking.
6. The only strong reason for A is committed base-model exact-copy/constrained
   decoding over protected spans, which is not yet a confirmed requirement.
```

Keep `sp64_protected_presplit_sidecar` as a documented optional variant for
pipelines that prove token-boundary alignment is required.

## Next Step

Do not run the pre-split 20M row now.

Instead:

```text
1. Consolidate passthrough sidecar as v2.1 practical baseline.
2. Run/record the 20M fixed-byte row only if we need an LM-loss baseline for
   passthrough sidecar itself.
3. If exact-copy/constrained decoding becomes a committed base capability,
   test selective pre-split by route class before global pre-split.
```

## Open Risk

The real pretraining mix may be more code/URL-heavy than the v1.8 pilot. If so,
global pre-split's +3.8% tax may be understated. This favors measuring route
density on the intended pretraining mix before any global edge-alignment
decision.
