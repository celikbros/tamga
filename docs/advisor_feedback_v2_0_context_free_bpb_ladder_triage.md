# Advisor Feedback Triage: v2.0 Context-Free BPB Ladder

Date: 2026-06-11

## What Changed

The 2M-byte context-free ladder produced the first strong positive BPB signal:

```text
finite_protected_teacher_distilled_16000
test BPB: 3.213530
protected SP64 floor test BPB: 3.326482
delta: -0.112952
```

Advisors agree this is important enough to continue investigating morphology-
aware scoring. They do not agree that it is ready to become the default v2.0
architecture.

## Advisor Consensus

Keep the branch alive:

```text
the result is too large to ignore
morphology may be reducing LM entropy, not just improving boundary F1
```

Do not promote yet:

```text
single seed
tiny undertrained LM
small byte budget
pilot-domain risk
teacher-distilled path is a bound/target, not a deployable tokenizer
```

## Fable5 Red Flags Accepted

Two warnings are now treated as blockers before more expensive runs:

```text
1. BPB accounting / undertraining audit:
   implied bits/token are above the uniform-vocab reference, so these runs are
   early learning-curve measurements, not converged LM-quality estimates.

2. Matched non-morph control:
   teacher_distilled_16000 uses the same 64k vocabulary as SP64, but it also
   re-estimates score geometry. We need a same-vocab, same-score-estimation
   control using official SP segmentation counts instead of morphology-teacher
   counts.
```

Important clarification:

```text
`teacher_distilled_16000` does not mean a 16k vocabulary.
It means teacher-distilled scores collected from 16k train lines.
The tiny-LM vocab size is still 64630 for all finite-protected rows.
```

## Immediate Decision

Do not run second seed, longer budget, or larger model yet.

First run:

```text
1. BPB accounting audit
2. matched non-morph self-distilled control
3. dry-run token pressure for the matched control
4. 2M-byte matched-control tiny-LM row
```

Then compare:

```text
SP64 protected floor
self_distilled_16000
teacher_distilled_16000
```

## New Artifacts

Scripts:

```text
scripts/audit_v2_tiny_lm_bpb_accounting.py
scripts/materialize_v2_self_distilled_sp_model.py
```

Config:

```text
configs/v2_0_tiny_lm_matched_control.toml
```

Completed quick audits:

```text
BPB accounting:
  report: artifacts/v2_0_tiny_lm_context_free_ladder_bpb_accounting_audit.md
  result: all 2M-byte rows imply bits/token above the uniform-vocab reference
  reading: the ladder is early-learning calibration, not converged LM quality

self-distilled matched control:
  model: artifacts/private/v2_0_self_distilled_sp/self_distilled_16000lines_unigram_64000.model
  vocab: artifacts/private/v2_0_self_distilled_sp/self_distilled_16000lines_unigram_64000.vocab
  report: artifacts/v2_0_self_distilled_16000lines_materialization.md
  lines: 16000
  segments: 2854463
  counted tokens: 3509481
  counted piece types: 60120
  changed scores: 63997

matched-control dry-run:
  report: artifacts/v2_0_tiny_lm_matched_control_dry_run.md
  private stats: artifacts/private/v2_0_tiny_lm_matched_control_dry_run/encoded_stats.jsonl
  self_distilled_16000 train/valid/test tokens_per_byte:
    0.159508 / 0.163942 / 0.164852
  teacher_distilled_16000 train/valid/test tokens_per_byte:
    0.172603 / 0.177073 / 0.177859
  2M-byte self-distilled step count:
    623

matched-control 2M-byte tiny-LM:
  report: artifacts/v2_0_tiny_lm_matched_control_self_distilled_16000_2mbytes.md
  private stats: artifacts/private/v2_0_tiny_lm_matched_control_self_distilled_16000_2mbytes/encoded_stats.jsonl
  steps: 623
  approx bytes seen: 1999750
  valid BPB: 3.312045
  test BPB: 3.343937
```

Accounting detail:

| Tokenizer | Uniform bits/token | Test bits/token | Reading |
| --- | ---: | ---: | --- |
| finite_protected_sp64_numeric_sp_floor | 15.9799 | 20.2221 | undertrained |
| finite_protected_pruned_ge070_nonword | 15.9799 | 19.9407 | undertrained |
| finite_protected_teacher_distilled_16000 | 15.9799 | 18.0679 | undertrained |
| finite_protected_teacher_distilled_2000 | 15.9799 | 17.0457 | undertrained |

## Success / Stop Logic

If teacher_distilled_16000 beats self_distilled_16000 materially:

```text
the morphology teacher is carrying signal beyond score re-estimation
next: confirm with second seed and/or longer learning curve
```

If self_distilled_16000 matches teacher_distilled_16000:

```text
the BPB gain is probably score concentration / effective-vocab geometry
next: demote morphology scoring as tokenizer path and rethink objective/data side
```

If both are above uniform bits/token:

```text
interpret the result as early-convergence calibration only
do not present endpoint BPB as final LM quality
```

## Matched-Control Result

| Tokenizer | Test tokens/byte | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: | ---: |
| finite_protected_sp64_numeric_sp_floor | 0.164497 | 2,001,501 | 3.307829 | 3.326482 |
| finite_protected_self_distilled_16000 | 0.164852 | 1,999,750 | 3.312045 | 3.343937 |
| finite_protected_teacher_distilled_16000 | 0.177859 | 2,002,277 | 3.192085 | 3.213530 |

Reading:

```text
self_distilled_16000 does not reproduce the teacher_distilled_16000 BPB gain.
It is slightly worse than the protected SP64 floor.

Therefore the 16k teacher-distilled gain is not explained by generic
same-vocabulary score re-estimation alone.

The result still lives in an undertrained tiny-LM regime, but the attribution
now points more strongly toward morphology-aware scoring.
```
