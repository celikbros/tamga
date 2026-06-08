# v2.0 Tiny-LM Marker Calibration Results

Date: 2026-06-08

## Scope

This calibration compares four bracketing tokenizer points with the same tiny
causal-LM setup:

```text
seq_len=128
batch_size=4
max_steps=300
d_model=256
n_layers=4
n_heads=4
```

The run is an early screening probe, not final LLM-tokenizer evidence. It is
useful because it checks whether visible morphology-boundary gains translate
into byte-normalized LM loss under a controlled small model.

## Results

| Tokenizer | Valid tokens/raw byte | Test tokens/raw byte | Valid BPB | Test BPB | Challenge F1 | Protected stress |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| sp_unigram_64000_train_only | 0.159020 | 0.159620 | 4.827723 | 4.860352 | 0.7351 | 1/25 |
| finite_protected_sp64_floor | 0.182112 | 0.183362 | 4.940256 | 4.976850 | 0.6913 | 25/25 |
| suffix_chain2_marker_stripped | 0.184500 | 0.185337 | 5.067901 | 5.094965 | 0.7632 | 25/25 |
| all_soft_marker_stripped | 0.196313 | 0.196954 | 5.133207 | 5.157444 | 0.7703 | 25/25 |

## Deltas

Against bare SP64:

| Tokenizer | Test tokens/raw byte delta | Test BPB delta |
| --- | ---: | ---: |
| finite_protected_sp64_floor | +0.023742 | +0.116498 |
| suffix_chain2_marker_stripped | +0.025717 | +0.234613 |
| all_soft_marker_stripped | +0.037334 | +0.297092 |

Against the true protected floor:

| Tokenizer | Test tokens/raw byte delta | Test BPB delta |
| --- | ---: | ---: |
| suffix_chain2_marker_stripped | +0.001975 | +0.118115 |
| all_soft_marker_stripped | +0.013592 | +0.180594 |

## Interpretation

The calibration gives a clear fixed-step/fixed-token signal:

```text
SP64 has the best BPB.
finite protected routing adds a measurable but understandable protection cost.
train-only morphology marker shaping improves visible boundary F1, but worsens
BPB relative to the finite protected floor.
more marker dose worsens both token pressure and BPB.
```

This means the current marker-shaping mechanism is not paying for its
morphology gains in tiny-LM BPB. Boundary F1 is still a useful diagnostic, but
for this candidate family it is not a sufficient promotion gate.

## Decision

Do not continue marker-dose tuning.

Do not promote `suffix_chain2_marker_stripped` or `all_soft_marker_stripped` to
larger LM probes as-is.

Keep finite protected routing as the non-negotiable protected-span mechanism.
Treat `finite_protected_sp64_floor` as the true deployable null baseline for
future v2.0 experiments, because bare SP64 does not preserve protected spans.

The next v2.0 branch should change the mechanism rather than the marker dose:

```text
selected suffix/morph seed vocabulary
curated high-value morph pieces
or a constrained Unigram/MorphBPE-style objective
```

Any new branch must beat or tie the finite protected floor on BPB while
preserving the protected stress set.

## Guardrails

This result does not prove that morphology-aware tokenization cannot help LLMs.
It only says that this train-only marker policy family did not convert its
visible boundary-F1 improvement into better tiny-LM BPB under this setup.

Before any LLM-team handoff, the candidate still needs:

```text
stateless decode
lossless roundtrip
protected stress 25/25
acceptable token pressure
byte-normalized LM-loss evidence against the finite protected floor
known-limitations note
```

