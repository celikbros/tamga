# Advisor Feedback Triage: v1.8 -> v2.0

Date: 2026-06-02

## Status

```text
advisor feedback received
v2.0 direction remains hybrid/vocabulary design
v1.8 BPB interpretation must be tightened before it is used as evidence
```

## What We Accept

The advisors agree on the main practical conclusion:

```text
do not hand pure custom morphology to the LLM team as the default tokenizer
do not discard the morphology signal
move toward a learned hybrid/vocabulary design
```

They also raised one important blocker:

```text
the v1.8 token accounting must be audited before claiming data efficiency
```

The apparent mismatch:

| Measurement | Custom tokens/byte | SP64 tokens/byte | Ratio |
| --- | ---: | ---: | ---: |
| earlier prep view | ~0.170 | ~0.157 | ~1.08x |
| tiny-LM lossless view | ~0.386 train / ~0.416 valid | ~0.153 train / ~0.157 valid | ~2.5x |

This is probably an encoding-mode difference:

```text
older prep likely used non-lossless / no-whitespace custom tokens
tiny-LM used whitespace-preserving custom tokens + 64k cap + byte fallback
```

But it must be measured directly rather than assumed.

## Immediate Decision

Before presenting v1.8 BPB as evidence:

```text
1. audit token accounting on the same filtered split
2. distinguish standard custom vs lossless custom vs lossless+byte-fallback
3. record SP64 on the same raw split
4. only compare BPB using the lossless generation-safe mode
```

Implementation added:

```text
scripts/audit_v1_8_token_accounting.py
```

## Accounting Audit Result

The audit was run on the same filtered v1.8 split:

```text
artifacts/v1_8_token_accounting_audit.md
```

The discrepancy is resolved. The earlier near-SP fertility view used the
standard, non-whitespace-preserving custom encoding. The tiny-LM BPB probe used
the generation-safe lossless custom encoding with a 64k train-only vocabulary
and UTF-8 byte fallback for source tokens outside that vocabulary.

Key valid/test rows:

| Mode | Split | Tokens/byte | Bytes/token | Notes |
| --- | --- | ---: | ---: | --- |
| custom_standard_no_whitespace | valid | 0.170863 | 5.852639 | older intrinsic/fertility-style view |
| custom_lossless_open_vocab | valid | 0.280095 | 3.570219 | whitespace-preserving, no vocab cap |
| custom_lossless_64000_byte_fallback | valid | 0.416206 | 2.402658 | tiny-LM custom mode |
| sp_bpe_64000_train_only | valid | 0.156571 | 6.386899 | SP64 baseline |
| custom_standard_no_whitespace | test | 0.170504 | 5.864981 | older intrinsic/fertility-style view |
| custom_lossless_open_vocab | test | 0.279405 | 3.579031 | whitespace-preserving, no vocab cap |
| custom_lossless_64000_byte_fallback | test | 0.419445 | 2.384101 | tiny-LM custom mode |
| sp_bpe_64000_train_only | test | 0.157028 | 6.368278 | SP64 baseline |

Result:

```text
standard custom is close to SP64 in token pressure
lossless whitespace preservation raises token pressure substantially
64k byte fallback raises it further on held-out splits
the tiny-LM custom mode is about 2.66x-2.67x SP64 tokens/byte on valid/test
```

This validates the concern: the pure custom LLM serialization is too expensive
as a final tokenizer candidate. It also clarifies the useful path: v2.0 should
not try to ship pure custom; it should preserve morphology/protection signal
while learning a compact vocabulary and reducing fallback pressure.

## v1.8 Interpretation Update

The current v1.8 finding should be framed as:

```text
fixed-token view: SP64 wins
approx iso-byte view: custom looks promising
but iso-byte custom used more optimization steps, so it is not iso-compute
therefore the result is a screening signal, not a data-efficiency proof
```

The next optional v1.8 control, if we need it:

```text
run SP64 to the same 1258 steps and inspect the full learning curve
```

This should be done only after the accounting audit, because the accounting
audit is cheaper and answers the most confusing discrepancy first.

## v2.0 Design Decision

Hard morphology pretokenization is no longer the preferred main design.

Use it only as a baseline:

```text
hybrid_hard_unigram_64000 = baseline / control
```

The primary v2.0 direction should be:

```text
protected spans are hard boundaries
morphology boundaries are soft hints / seeded priors
learned merges may cross morphology boundaries when frequency supports it
byte fallback remains lossless
```

This resolves the advisor disagreement:

```text
Grok43ML: hard pretok is simple and useful as first control
Opus48ML: hard pretok risks worst-of-both-worlds
project decision: keep hard pretok as a baseline, make soft morphology the main candidate
```

## Next Actions

1. Update the v1.8 findings with the audit result.
2. Decide whether an SP64 1258-step iso-compute run is still necessary.
3. Prototype the v2.0 soft-morph learned vocabulary path.

## Guardrail

Do not start a large v2.0 tokenizer rewrite. The accounting audit is now
recorded, so the next safe step is a small v2.0 prototype that targets the
specific pressure sources found here: whitespace serialization and byte fallback
from a capped custom vocabulary.
