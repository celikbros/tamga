# v2.0 Train-Only Marker Findings

Date: 2026-06-08

## Summary

Train-only marker shaping is the right mechanism direction, but the current
marker policies are not strong enough to justify another tiny-LM probe.

The key improvement is token pressure:

```text
all-soft in-stream markers:        test ~0.2522 tokens/raw byte
all-soft train-only marker model:  test ~0.1962 tokens/raw byte
suffix-chain2 train-only model:    test ~0.1846 tokens/raw byte
high-value suffix train-only model:test ~0.1911 tokens/raw byte
SP64 reference:                    test ~0.1596 tokens/raw byte
```

The problem is visible intrinsic strength:

```text
SP64 challenge F1:                 0.7351
all-soft train-only challenge F1:  0.7703
suffix-chain2 challenge F1:        0.7632
high-value suffix challenge F1:    0.7665
preferred gate: materially above SP64, ideally >= ~0.78-0.80
```

So the train-only approach is promising, but this exact policy family is still
below the preferred intrinsic gate.

## Frontier

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Challenge F1 | Protected stress | Decision |
| --- | ---: | ---: | ---: | --- | --- |
| SP64 reference | 0.159020 | 0.159620 | 0.7351 | 1/25 | null baseline |
| all-soft train-only marker-stripped | 0.195611 | 0.196236 | 0.7703 | 25/25 | promising, but below preferred F1 gate |
| suffix-chain2 train-only marker-stripped | 0.183799 | 0.184619 | 0.7632 | 25/25 | best pressure, weaker F1 |
| high-value suffix train-only marker-stripped | 0.190346 | 0.191068 | 0.7665 | 25/25 | slightly better F1 than suffix-chain2, worse pressure |

## Interpretation

The current frontier says:

```text
train-only marker shaping reduces token pressure enough to stay in the
candidate space, but current marker selection does not recover enough boundary
signal to justify another BPB/tiny-LM run.
```

This is not a failure of the whole v2.0 direction. It narrows the search:

```text
keep finite protected routing
keep marker-free normal encode
avoid in-stream all-soft markers
look for a better learned prior than the current simple marker policies
```

## Next Decision

Do not run tiny-LM yet.

The next useful step is either:

```text
1. design a stronger train-only shaping method, e.g. selected user-defined
   suffix/morph pieces, constrained seed vocabulary, or class-specific marker
   policies measured on train-only statistics; or
2. send this frontier to advisors and ask which shaping lever is most likely to
   move challenge F1 above ~0.78 without exceeding ~0.20 tokens/raw byte.
```

Do not tune directly against visible challenge examples.
