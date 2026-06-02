# v2.0 Hybrid Vocabulary Plan

Date: 2026-06-02

## Status

```text
planning document
not an implementation
v1.8 tiny-LM screening complete enough for direction-setting
```

## Decision From v1.8

v1.8 appears to show two things at the same time:

```text
pure custom morphology has a promising byte-exposure signal
pure custom morphology has serious token/context/compute pressure
```

The best tiny-LM smoke evidence:

| Comparison view | Result |
| --- | --- |
| fixed token/step budget | `sp_bpe_64000_train_only` beats pure custom |
| approximate iso-byte budget | `custom_tr_morph_lossless` beats `sp_bpe_64000_train_only` |

Key iso-byte checkpoint:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| sp_bpe_64000 step 500 | 1668920 | 3.729064 | 3.745292 |
| custom step 1258 | 1670292 | 2.943302 | 2.961183 |

But pure custom needs about 2.5x more tokens/steps to see the same raw byte
exposure as the 64k SP baseline in the tiny-LM lossless encoding. Advisors
also flagged a token-accounting discrepancy: earlier prep metrics reported
custom near the 32k/64k SP fertility band, while the tiny-LM lossless mode is
much more expensive. The audit resolved this as an encoding-mode difference.
The iso-byte result should still be treated as a screening signal rather than a
data-efficiency proof because it is not iso-compute.

Therefore:

```text
do not hand pure custom to the LLM team as the default tokenizer
do not throw away the morphology-aware signal
move to hybrid/vocabulary design
```

Accounting audit result:

| Mode | Valid tokens/byte | Test tokens/byte |
| --- | ---: | ---: |
| custom_standard_no_whitespace | 0.170863 | 0.170504 |
| custom_lossless_open_vocab | 0.280095 | 0.279405 |
| custom_lossless_64000_byte_fallback | 0.416206 | 0.419445 |
| sp_bpe_64000_train_only | 0.156571 | 0.157028 |

Conclusion:

```text
the older custom view was not generation-safe
the lossless LLM mode is the expensive one
v2.0 must reduce whitespace/fallback pressure while keeping lossless decode
```

## v2.0 Goal

Design a tokenizer that keeps the useful morphology/protection signal while
reducing sequence pressure.

Target:

```text
boundary/protection behavior closer to custom
tokens/byte closer to learned SP
lossless byte fallback
no Turkish morphology leakage into non-Turkish spans
```

## Non-Goals

v2.0 should not start by:

```text
writing hand-built morphology for every Turkic language
training a full LLM
claiming production readiness
optimizing only visible boundary F1
running more v1.8 full-matrix tiny-LM experiments
```

## Candidate Designs

### A. Hard Morph Pretokenization + Unigram/BPE

Process:

```text
raw text
-> protected-span pass
-> custom morphology hard segmentation
-> train SP Unigram/BPE on segmented corpus
```

What v1.8 says:

```text
already tested intrinsically
improves some learned boundary metrics
does not close the gap to pure custom
still has token-pressure risk
```

Use as a baseline/control, not the main v2.0 design. Advisors flagged this as
a possible worst-of-both-worlds path: it can preserve some boundary signal but
still carry high token pressure.

### B. Soft Boundary Hints

Process:

```text
custom morphology proposes candidate boundaries
SP/Unigram can merge across soft boundaries when frequency supports it
protected spans remain hard boundaries
```

Why promising:

```text
keeps morphology signal
lets frequent forms compress
may reduce the 2.5x token-pressure penalty
```

This is the most promising v2.0 direction and should be the first main
prototype after the token-accounting audit.

### C. Protected-Span-Aware Learned Tokenizer

Process:

```text
protect URL/file/code/number/date spans
train learned tokenizer on remaining text
represent protected bases compactly
handle Turkish suffix tails explicitly
```

Why needed:

```text
canary showed custom preserves protected spans
SP baselines split protected spans in the diagnostic view
LLM/code-mixed text needs protected-span integrity
```

### D. Custom Morph Tokens + Learned Surface Merges

Process:

```text
use custom tokens as atomic training alphabet
learn merges over frequent token sequences
allow merges such as root+common suffix chains
forbid merges that cross protected hard boundaries
```

ASCII example:

```text
WORD_START kitap +lar +im +dan
```

This could become a compact learned piece when frequent, while still preserving
the underlying morphology map for analysis/debugging.

This direction directly attacks the v1.8 token-pressure problem.

## Required Metrics

Every v2.0 candidate must report:

```text
decode(encode(x)) == x
tokens/byte
avg tokens/word
protected span break rate
byte fallback rate
boundary F1 on visible eval
canary diagnostics
tiny-LM BPB under both fixed-token and iso-byte views
```

Do not optimize a candidate on one metric alone.

## Initial v2.0 Experiment Matrix

Keep the first v2.0 matrix small:

| Candidate | Purpose |
| --- | --- |
| `custom_tr_morph_lossless` | high-F1, high-token-pressure reference |
| `sp_bpe_64000_train_only` | strong compression baseline |
| `hybrid_hard_unigram_64000` | current hard-boundary hybrid baseline |
| `hybrid_soft_unigram_64000` | main v2.0 candidate |
| `protected_sp_unigram_64000` | protected-span-aware learned baseline |

Avoid adding more candidates until these answer the main question.

## Kill Criteria

Deprioritize a v2.0 candidate if:

```text
roundtrip fails
protected span break rate is nonzero on stress/canary
tokens/byte stays close to pure custom with no BPB advantage
fixed-token BPB is much worse and iso-byte BPB does not compensate
implementation requires large hand-written Turkic morphology expansion
```

## Success Criteria

A candidate becomes worth handing to the LLM team as experimental, not final, if:

```text
it is lossless
it preserves protected spans
it materially reduces custom tokens/byte
it keeps a meaningful boundary-F1 advantage over SP
it is at least competitive on tiny-LM BPB under documented budget views
```

## Next Implementation Step

Do not implement a full tokenizer rewrite first.

The accounting blocker is now closed:

```text
artifacts/v1_8_token_accounting_audit.md
```

Build a small v2.0 prototype path:

```text
1. materialize custom-morph token stream with explicit hard/soft boundary markers
2. train a learned model that may merge soft boundaries but not protected hard boundaries
3. compare against pure custom, SP 64k, and hard hybrid on the existing v1.8 split
```

This should be a prototype artifact, not a public production API.
