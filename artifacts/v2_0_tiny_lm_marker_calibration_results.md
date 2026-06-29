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
| finite_protected_sp64_floor | 0.176643 | 0.177726 | 4.897577 | 4.939361 | 0.6913 | 25/25 |
| finite_protected_sp64_numeric_sp_floor | 0.171903 | 0.172734 | 4.875198 | 4.911037 | 0.6913* | 25/25* |
| boundary_biased_lambda0_numeric_sp | 0.163153 | 0.163839 | 4.726285 | 4.769027 | 0.7422 | 25/25 |
| boundary_biased_lambda4_numeric_sp | 0.164015 | 0.164686 | 4.686700 | 4.721480 | 0.7701 | 25/25 |
| boundary_biased_lambda8_numeric_sp | 0.178725 | 0.179299 | 4.816592 | 4.850946 | 0.8225 | 25/25 |
| suffix_chain2_marker_stripped | 0.184500 | 0.185337 | 5.067901 | 5.094965 | 0.7632 | 25/25 |
| all_soft_marker_stripped | 0.196313 | 0.196954 | 5.133207 | 5.157444 | 0.7703 | 25/25 |

## Deltas

Against bare SP64:

| Tokenizer | Test tokens/raw byte delta | Test BPB delta |
| --- | ---: | ---: |
| finite_protected_sp64_floor | +0.018106 | +0.079009 |
| finite_protected_sp64_numeric_sp_floor | +0.013114 | +0.050685 |
| boundary_biased_lambda0_numeric_sp | +0.004219 | -0.091325 |
| boundary_biased_lambda4_numeric_sp | +0.005066 | -0.138872 |
| boundary_biased_lambda8_numeric_sp | +0.019679 | -0.009406 |
| suffix_chain2_marker_stripped | +0.025717 | +0.234613 |
| all_soft_marker_stripped | +0.037334 | +0.297092 |

Against the true protected floor:

| Tokenizer | Test tokens/raw byte delta | Test BPB delta |
| --- | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | -0.004992 | -0.028324 |
| boundary_biased_lambda0_numeric_sp | -0.008895 | -0.142010 |
| boundary_biased_lambda4_numeric_sp | -0.013040 | -0.217881 |
| boundary_biased_lambda8_numeric_sp | +0.001573 | -0.060091 |
| suffix_chain2_marker_stripped | +0.001975 | +0.118115 |
| all_soft_marker_stripped | +0.013592 | +0.180594 |

## Lambda Decomposition

The missing lambda 0 control has now been run. It shows that most of the
protected-floor to lambda-4 BPB gain comes from the custom decoder/pipeline
path, while lambda 4 adds a smaller extra gain:

| Step | Test tokens/raw byte delta | Test BPB delta | Challenge F1 delta | Interpretation |
| --- | ---: | ---: | ---: | --- |
| finite protected numeric-SP floor -> lambda 0 | -0.008895 | -0.142010 | +0.0509 | decoder/pipeline effect |
| lambda 0 -> lambda 4 | +0.000847 | -0.047547 | +0.0279 | morphology boundary penalty effect |
| lambda 4 -> lambda 8 | +0.014613 | +0.129466 | +0.0524 | high-F1 over-segmentation effect |

This changes the claim. The strongest current statement is:

```text
The custom boundary-biased decoder family is promising.
Within that family, lambda 4 improves both F1 and 300-step BPB over lambda 0.
But most of the total BPB improvement over the protected floor is not yet
attributable to morphology; it comes from the lambda 0 decoder/pipeline path.
```

## Interpretation

The calibration gives a clear fixed-step/fixed-token signal:

```text
SP64 no longer has the best BPB in this screening table.
finite protected routing adds a measurable but understandable protection cost.
train-only morphology marker shaping improves visible boundary F1, but worsens
BPB relative to the finite protected floor.
more marker dose worsens both token pressure and BPB.
numeric-SP protected routing recovers a meaningful part of the current
finite-wrapper cost without adding morphology-marker pressure.
boundary-biased lambda 0 already improves tiny-LM BPB against bare SP64 and the
protected floor, so the decoder/pipeline effect is large.
boundary-biased lambda 4 further improves both visible morphology F1 and
tiny-LM BPB against lambda 0, but the extra BPB gain is much smaller than the
floor -> lambda 0 gain.
boundary-biased lambda 8 gives a much stronger visible morphology signal and
still slightly beats SP64 BPB, but it is worse than lambda 4 on BPB and token
pressure.
```

Important attribution caveat added after advisor review:

```text
The boundary-biased lambda 0 path is not equivalent to official SentencePiece
or to the finite protected floor. Therefore lambda 4 currently mixes a
decoder/pipeline effect with a morphology-boundary penalty effect.
```

The lambda 4 row is therefore promising, but it is not yet a promoted v2.0
candidate. The lambda 0 control confirms that the current result is a mixed
decoder/pipeline + morphology signal.

`*` The numeric-SP row changes model-token encoding for `numeric_like` spans,
not the logical protected wrapper. It is therefore expected to preserve the
same visible protected stress and challenge F1 as the finite floor; this row
should still be re-run in a dedicated intrinsic report if it becomes a handoff
candidate.

This means the current marker-shaping mechanism is not paying for its
morphology gains in tiny-LM BPB. Boundary F1 is still a useful diagnostic, but
for this candidate family it is not a sufficient promotion gate.

The boundary-biased decode result changes the active v2.0 branch hypothesis:
morphology signal may be useful when applied as a decoder/objective preference
rather than as marker-dose shaping or broad UDS forcing. Lambda 0 is now
measured, and lambda 4 does beat it in the 300-step screen; the remaining block
is correctness/generalization, especially decoder alignment, roundtrip, hidden
eval, and longer/seeded BPB.

Lambda 4 is the current balanced diagnostic point, not a promoted candidate.
Lambda 8 is a useful high-F1 reference, not the main efficiency candidate.

## Decision

Do not continue marker-dose tuning.

Do not promote `suffix_chain2_marker_stripped` or `all_soft_marker_stripped` to
larger LM probes as-is.

Keep finite protected routing as the non-negotiable protected-span mechanism.
Treat `finite_protected_sp64_floor` as the historical deployable null baseline.
Promote `finite_protected_sp64_numeric_sp_floor` as the active protected floor
for the next v2.0 experiments. It is not yet the final production numeric
design; it is the best experimental protected null baseline.

The next v2.0 branch should continue only after attribution controls:

```text
keep the floor -> lambda0 and lambda0 -> lambda4 decomposition explicit
audit roundtrip/stateless decode and no-protected SP alignment
then decide whether to keep decode bias or move the prior into training
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
