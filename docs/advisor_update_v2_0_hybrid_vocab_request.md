# Advisor Review Request: v2.0 Hybrid/Vocabulary Direction

Date: 2026-06-02

## Context

We are building a Turkish-primary, multilingual-aware tokenizer.

v1.8 was a screening phase, not final LLM evidence. It compared:

```text
pure custom morphology-aware tokenizer
train-only SentencePiece baselines
hard-boundary hybrid SentencePiece baselines
tiny LM bits-per-byte smoke runs
```

## Key v1.8 Evidence

### Boundary / Intrinsic

On visible Turkish challenge:

| Tokenizer | Avg tokens/word | Boundary F1 | Exact |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 | 44/108 |
| sp_bpe_64000_train_only | 1.9817 | 0.6909 | 0/108 |
| sp_unigram_64000_train_only | 1.9840 | 0.7317 | 0/108 |
| hybrid_morph_pretok_unigram_64000_train_only | 2.5379 | 0.7633 | 0/108 |

### Canary

The public/synthetic canary found:

```text
custom_tr_morph_lossless: 0 roundtrip failures, 0/7 protected spans broken
SP/hybrid SP: 0 roundtrip failures, but 7/7 protected spans broken in diagnostic view
```

### Tiny LM BPB Smoke

Fixed-token / fixed-step view:

| Tokenizer | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| custom 500 step | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000 500 step | 1668920 | 3.729064 | 3.745292 |

Approx iso-byte view:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| sp_bpe_64000 step 500 | 1668920 | 3.729064 | 3.745292 |
| custom step 1258 | 1670292 | 2.943302 | 2.961183 |

Interpretation:

```text
pure custom has strong byte-exposure/data-efficiency signal
pure custom has serious token/context/compute pressure
```

## Current Internal Decision

We do not want to hand pure deterministic custom to the LLM team as the default
tokenizer.

We also do not want to discard the morphology-aware path.

Proposed v2.0 direction:

```text
hybrid learned vocabulary/tokenizer
custom morphology as hard/soft prior
protected spans as hard boundaries
byte fallback as lossless safety
reduce tokens/byte closer to SP
```

## Questions

Please be critical.

1. Is the conclusion fair: stop v1.8 tiny-LM experimentation and move to
   v2.0 hybrid/vocabulary design?

2. Does the tiny-LM smoke result support the claim that morphology is useful but
   pure custom is too token-expensive for an LLM default?

3. Which v2.0 candidate should be first?
   - hard morphology pretokenization + Unigram/BPE
   - soft morphology boundary hints
   - custom morph tokens + learned merges
   - protected-span-aware learned tokenizer

4. How should we make "soft boundary" operational without turning it into a
   large research detour?

5. What is the fairest next evaluation after a v2.0 prototype?
   - repeat visible boundary/canary
   - repeat tiny-LM BPB
   - larger corpus SP/hybrid training
   - small downstream task

6. What result would make you abandon pure custom entirely and keep only hybrid
   morphology as a prior?

7. What result would make this safe to send to the LLM team as an experimental
   tokenizer package?

## Proposed Next Step

Build a small prototype that:

```text
materializes custom morph token stream
marks protected boundaries as hard
marks morphology boundaries as soft
trains learned merges/subwords that may cross soft but not hard boundaries
compares tokens/byte, boundary F1, canary, and tiny-LM BPB
```
