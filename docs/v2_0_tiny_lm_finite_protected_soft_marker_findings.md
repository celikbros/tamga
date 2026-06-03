# v2.0 Tiny-LM Finite Protected Soft-Marker Findings

Date: 2026-06-03

## Status

```text
early smoke only
not final LLM tokenizer evidence
not an LLM handoff recommendation
```

This note records the first narrow tiny-LM BPB screen for:

```text
finite_protected_soft_marker
sp_unigram_64000_train_only
```

The candidate combines:

```text
normal text: train-only soft-marker Unigram model
protected spans: finite protected pieces + UTF-8 byte fallback
```

## Encoding Pressure

```text
finite protected soft-marker valid/test tokens/raw byte: 0.251658 / 0.252212
SP64 valid/test tokens/raw byte: 0.159020 / 0.159620
```

Interpretation:

```text
the candidate uses about 1.58x as many model tokens per raw byte as SP64
at a fixed token/step budget, SP64 sees about 1.60x more raw bytes
```

## Fixed-Token Smoke

Report:

```text
artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_200steps.md
```

At 200 steps:

| Tokenizer | Steps | Tokens seen | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_soft_marker | 200 | 102400 | 412573 | 7.067777 |
| sp_unigram_64000_train_only | 200 | 102400 | 662011 | 5.966637 |

Interpretation:

```text
fixed-token / fixed-step view favors SP64
SP64 sees substantially more raw text under the same token budget
```

## Approx Iso-Byte Smoke

Report:

```text
artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_finite_321_iso_byte.md
```

At 321 candidate steps:

| Tokenizer | Steps | Tokens seen | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_soft_marker | 321 | 164352 | 662180 | 5.263920 |
| sp_unigram_64000_train_only reference | 200 | 102400 | 662011 | 5.966637 |

Interpretation:

```text
approx iso-byte view favors finite_protected_soft_marker
this is not iso-compute: the candidate used more tokens/steps to see the same bytes
```

## Same-Step SP64 Control

Report:

```text
artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_sp64_321steps.md
```

At 321 SP64 steps:

| Tokenizer | Steps | Tokens seen | Approx bytes seen | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_soft_marker | 321 | 164352 | 662180 | 5.263920 |
| sp_unigram_64000_train_only | 321 | 164352 | 1062527 | 4.629442 |

Interpretation:

```text
same-token/same-step view strongly favors SP64
SP64 uses its lower token pressure to see more raw text at the same compute step count
the candidate's iso-byte gain is real but currently too expensive in tokens
```

## Current Read

```text
positive: morphology/protection signal can improve BPB after equal raw-byte exposure
negative: the candidate pays a large token-pressure/compute/context cost
net: current candidate is promising as a research direction but not efficient
enough for LLM handoff or larger LM probes
```

This is a useful research signal, not a final tokenizer decision.

## Decision

```text
do not hand this tokenizer to the LLM team as final
do not discard the morphology-aware path
do not run a broad tiny-LM matrix for this candidate
make token-pressure reduction the next v2.0 design target
```

The next design pressure is clear:

```text
keep the protected-span and boundary gains
reduce token pressure toward SP64
avoid broader tiny-LM matrices until the compression gap is addressed or accepted
```
