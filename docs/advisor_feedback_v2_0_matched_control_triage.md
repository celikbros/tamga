# Advisor Feedback Triage: Matched-Control Result

Date: 2026-06-11

## What Fable5 Accepted

The matched non-morph control killed the generic score re-estimation
explanation:

```text
self_distilled_16000:
  same SP64 vocab
  same finite protected wrapper
  same 16k train-line score re-estimation
  official SP segmentation counts
  no morphology teacher

result:
  test BPB 3.343937
  slightly worse than SP64 floor 3.326482

teacher_distilled_16000:
  test BPB 3.213530
```

Interpretation:

```text
The teacher-distilled gain is not reproduced by non-morph score
re-estimation. Morphology teacher signal is now the leading explanation.
```

Inference-path clarification:

```text
teacher_distilled_16000 is a static `.model` file with modified Unigram
piece scores over the fixed SP64 vocabulary.

Runtime does not call the morphology teacher.
Runtime path is:
  finite protected routing
  + standard SentencePiece encode using the modified `.model`
  + UTF-8 fallback where needed
```

## What Still Blocks Larger Confirmation

Fable5 rejected the explanation that high bits/token is merely "undertrained"
without further accounting. We accept this as a blocker for expensive runs.

Required before a 20M/40M learning curve:

```text
1. future tiny-LM runs must report eval bits/token, target-token counts, and
   evaluated byte denominator from the same eval pass
2. compute zero-training unigram-entropy BPB for the same token streams
3. log future learning curves on both byte axis and token axis
```

## Implemented After Feedback

Runner accounting:

```text
script updated: scripts/run_tiny_lm_bpb_probe.py
new metrics.jsonl fields:
  valid_bits_per_token
  valid_target_tokens
  valid_evaluated_bytes
  valid_evaluated_fraction
new public report section:
  Loss Accounting
```

Unigram decomposition:

```text
new script: scripts/report_v2_unigram_entropy_bpb.py
purpose:
  tokenize train/test exactly as the LM sees them
  estimate a smoothed train unigram distribution
  compute test unigram bits/token and BPB
```

Syntax check:

```text
python -m py_compile scripts/run_tiny_lm_bpb_probe.py scripts/report_v2_unigram_entropy_bpb.py scripts/materialize_v2_self_distilled_sp_model.py
status: passed
```

Unigram decomposition result:

```text
report: artifacts/v2_0_unigram_entropy_bpb_matched_control.md
alpha: 0.1
```

| Tokenizer | Test bits/token | Test unigram BPB | Delta vs SP64 |
| --- | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 12.322119 | 2.026952 | +0.000000 |
| finite_protected_self_distilled_16000 | 12.303881 | 2.028322 | +0.001370 |
| finite_protected_teacher_distilled_16000 | 11.873857 | 2.111869 | +0.084916 |

Reading:

```text
teacher_distilled_16000 has lower unigram bits/token, but its higher
tokens/byte makes its unigram BPB worse than SP64.

Therefore the 2M tiny-LM BPB win is not already present in static unigram BPB.
The current evidence points toward contextual/morphological usefulness, while
the undertrained-LM caveat remains.
```

## Immediate Next Step

Completed zero-training unigram decomposition before any more tiny-LM training:

```text
SP64 floor
self_distilled_16000
teacher_distilled_16000
```

Interpretation:

```text
Result:
  teacher_distilled_16000 is worse in unigram BPB but better in tiny-LM BPB.
  This supports contextual/morphological usefulness rather than static
  token-distribution geometry.
```

## Next Training Run, Not Yet Started

After unigram decomposition:

```text
three-row learning curve:
  SP64 floor
  self_distilled_16000
  teacher_distilled_16000

larger fixed-byte budget, preferably 20M raw bytes
eval checkpoints around every 500 steps
report BPB versus bytes, tokens, and bits/token
```

Do not interpret the result as production-quality unless models approach or
beat their own unigram BPB floors.

## 20M Learning Curve Progress

Completed rows:

```text
SP64 floor:
  report: artifacts/v2_0_tiny_lm_curve_sp64_floor_20mbytes.md
  private stats: artifacts/private/v2_0_tiny_lm_curve_sp64_floor_20mbytes/encoded_stats.jsonl

self-distilled 16k:
  report: artifacts/v2_0_tiny_lm_curve_self_distilled_16000_20mbytes.md
  private stats: artifacts/private/v2_0_tiny_lm_curve_self_distilled_16000_20mbytes/encoded_stats.jsonl
```

| Tokenizer | Steps | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 6216 | 20,002,137 | 1.951192 | 1.962704 | 11.9316 |
| finite_protected_self_distilled_16000 | 6231 | 20,000,713 | 1.951182 | 1.963184 | 11.9088 |
| finite_protected_teacher_distilled_16000 | 6743 | 20,002,006 | 1.971752 | 1.983360 | 11.1513 |

Health check:

```text
log2(vocab): 15.9799
SP64 test bits/token: 11.9316
SP64 unigram BPB: 2.026952
SP64 20M tiny-LM test BPB: 1.962704
self-distilled test bits/token: 11.9088
self-distilled unigram BPB: 2.028322
self-distilled 20M tiny-LM test BPB: 1.963184
teacher-distilled test bits/token: 11.1513
teacher-distilled unigram BPB: 2.111869
teacher-distilled 20M tiny-LM test BPB: 1.983360
```

Reading:

```text
The 20M SP64 and self-distilled rows are no longer in the above-uniform
pathological regime.
Both beat their own zero-training unigram BPB floors, so these rows are
interpretable as healthier learning-curve checkpoints.

self_distilled_16000 does not beat the protected SP64 floor at 20M bytes.
It has slightly lower bits/token but slightly higher tokens/byte, leaving test
BPB essentially tied/slightly worse.

The non-morph score re-estimation control still does not explain the
teacher_distilled_16000 2M-byte gain.

However, the 20M curve does not preserve the teacher_distilled_16000 BPB
advantage. It has much lower bits/token, but its higher tokens/byte tax is no
longer compensated at 20M bytes.

Final 20M test BPB:
  SP64 floor: 1.962704
  self_distilled_16000: 1.963184
  teacher_distilled_16000: 1.983360

This turns the 2M positive result into an early-convergence signal rather than
a durable tokenizer-quality win for the static teacher-distilled model.
```

## 20M Valid Curve Reading

Approximate valid BPB checkpoints:

| Approx bytes | SP64 | Self-distilled | Teacher-distilled |
| ---: | ---: | ---: | ---: |
| ~1.5M-1.6M | 3.700883 | 3.692259 | 3.677377 |
| ~3.0M-3.2M | 2.716352 | 2.709774 | 2.734786 |
| ~6.0M-6.4M | 2.204375 | 2.206778 | 2.266931 |
| ~9.0M-9.6M | 2.047196 | 2.047923 | 2.096509 |
| ~12.0M-12.9M | 2.002634 | 2.001931 | 2.050466 |
| ~16.0M-16.3M | 1.984723 | 1.977787 | 2.014984 |
| ~20.0M | 1.951192 | 1.951182 | 1.971752 |

Decision:

```text
Do not promote teacher_distilled_16000 as a tokenizer candidate based on BPB.
It remains useful evidence that morphology can accelerate early learning and
lower bits/token, but the static segmentation/token-pressure tradeoff loses at
the healthier 20M checkpoint.
```

## Post-Fable5 Eval-Only Checks

After the 20M result, Fable5 asked for eval-only checks before any new training.

Completed:

```text
1. matched-byte validation delta trajectory
2. active numeric-SP protected wrapper token-tax decomposition
```

Delta trajectory:

```text
report: artifacts/v2_0_20m_learning_curve_delta_report.md
```

At matched validation checkpoints, `teacher_distilled_16000` is better only at
early bytes and ends worse:

| Target bytes | Teacher valid BPB delta vs SP64 floor |
| ---: | ---: |
| 2,000,000 | -0.023506 |
| 6,000,000 | +0.062556 |
| 10,000,000 | +0.024832 |
| 16,000,000 | +0.016182 |
| 20,000,000 | +0.020560 |

Wrapper tax:

```text
report: artifacts/v2_0_finite_protected_numeric_sp_wrapper_cost_audit.md
```

The active protected wrapper raises token pressure by about `+0.013`
tokens/raw byte on valid/test. Protected bytes are only about `1.6-1.7%` of
raw bytes, so the cost is concentrated. Numeric-like spans are no longer the
problem under SP passthrough; route cost is concentrated in:

```text
file_like
apostrophe_surface
non_turkish_latin_word
```

Not yet completed:

```text
paired bootstrap over per-document BPB deltas
```

Reason:

```text
The existing 20M artifacts contain only global metrics.jsonl checkpoints.
They do not contain checkpoint weights or per-document eval losses.
```

This should be implemented in the runner only if we need handoff-grade
confidence intervals.
