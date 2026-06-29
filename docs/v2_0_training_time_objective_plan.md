# v2.0 Training-Time Morphology Objective Plan

Date: 2026-06-10

## Advisor Triage Update

This plan is directionally valid, but it is now gated by wrapper and
normalization repair.

Do not treat any new training-time objective result as a candidate result until
the active protected baseline is exact-roundtrip under a documented contract.

Immediate order:

1. Normalize/roundtrip contract.
2. Protected wrapper repair and re-audit. The finite protected floor now passes
   exact roundtrip on valid/test via route-only splitting plus UTF-8 fallback.
3. Baseline table re-emission. Repaired strict and numeric-SP floor reports have
   been emitted.
4. Rung-0 diagnostic: unconstrained SP64 path vs morphology-compliant path.
   Completed; hard no-cross paths are available but costly.
5. Stock SentencePiece partial-boundary experiment.
6. Only then custom boundary-weighted Unigram/BPE work.

Latest repaired numeric-SP floor:

```text
valid exact roundtrip: 1994/1994
test exact roundtrip: 1998/1998
protected stress: 25/25
challenge F1: 0.6755
challenge avg model tokens/word: 2.2977
```

This re-establishes the floor as a protected/lossless baseline, not as a
morphology-improving candidate.

Rung-0 diagnostic:

```text
challenge crossing share: 0.747059
challenge avg token delta constrained-unconstrained: 1.0647
challenge+valid200 crossing share: 0.928189
challenge+valid200 avg token delta: 1.5614
```

Interpretation:

```text
SP64 usually can represent morphology-compliant paths, but they are too costly
for a hard constraint. The next branch should be a stock SentencePiece
partial-boundary prior, not a hard decoder/objective.
```

Partial-boundary infrastructure:

```text
view script: scripts/materialize_v2_partial_boundary_sp_view.py
candidate runner updated: scripts/run_v2_candidate_sentencepiece_probe.py
rho=0.10 view:
  artifacts/private/v2_0_partial_boundary_sp/partial_boundary_rho010.train.txt
rho=0.10 config:
  configs/v2_0_partial_boundary_rho010_sentencepiece.toml
rho=0.10 view report:
  artifacts/v2_0_partial_boundary_rho010_view.md
rho=0.10 marked line rate: 0.097562
rho=0.10 view/raw bytes: 1.011619
rho=0.10 SP probe:
  artifacts/v2_0_partial_boundary_rho010_sentencepiece_probe.md
rho=0.10 intrinsic eval:
  artifacts/v2_0_partial_boundary_rho010_intrinsic_eval.md
rho=0.10 valid/test tokens/raw byte: 0.158404 / 0.159029
rho=0.10 bare Challenge F1: 0.7361
rho=0.10 finite-protected Challenge F1: 0.6750
rho=0.10 protected stress with finite wrapper: 25/25
rho=0.25 view:
  artifacts/private/v2_0_partial_boundary_sp/partial_boundary_rho025.train.txt
rho=0.25 config:
  configs/v2_0_partial_boundary_rho025_sentencepiece.toml
rho=0.25 view/raw bytes: 1.029451
rho=0.25 marked line rate: 0.246312
rho=0.50 view:
  artifacts/private/v2_0_partial_boundary_sp/partial_boundary_rho050.train.txt
rho=0.50 config:
  configs/v2_0_partial_boundary_rho050_sentencepiece.toml
rho=0.50 view/raw bytes: 1.058956
rho=0.50 marked line rate: 0.494125
rho=0.25 valid/test tokens/raw byte: 0.158458 / 0.159060
rho=0.25 bare Challenge F1: 0.7380
rho=0.25 finite-protected Challenge F1: 0.6782
rho=0.50 valid/test tokens/raw byte: 0.158676 / 0.159231
rho=0.50 bare Challenge F1: 0.7361
rho=0.50 finite-protected Challenge F1: 0.6777
```

Interpretation:

```text
rho=0.10, rho=0.25, and rho=0.50 kept compression near SP64, but did
not transfer a meaningful morphology signal. The stock SentencePiece
partial-boundary branch is closed.
```

Findings:

```text
docs/v2_0_partial_boundary_sp_findings.md
```

Post-hoc score-shift probe:

```text
script: scripts/materialize_v2_score_shifted_sp_model.py
lambda=0.5 materialization:
  artifacts/v2_0_score_shift_lambda05_materialization.md
lambda=0.5 intrinsic eval:
  artifacts/v2_0_score_shift_lambda05_intrinsic_eval.md
adjusted pieces: 4878
alignment failures: 0
lambda=0.5 bare Challenge F1: 0.7364
lambda=0.5 finite-protected Challenge F1: 0.6768
```

Interpretation:

```text
simple post-hoc score shifting is also weak at lambda=0.5. Do not run
tiny-LM on this candidate. If this idea is revisited, use a cached crossing
stats sweep with stronger lambdas; otherwise move to a real boundary-weighted
Unigram/constrained objective.
```

Fable5 triage:

```text
docs/advisor_feedback_v2_0_sp_compatible_hacks_triage.md
```

SP64 vocab oracle ceiling:

```text
script: scripts/audit_v2_sp_vocab_oracle_ceiling.py
report: artifacts/v2_0_sp_vocab_oracle_ceiling_challenge.md
lambda0 Challenge F1: 0.7422
no-cross Challenge F1: 0.8407
oracle-best-F1 Challenge F1: 0.8417
oracle-best-F1 avg tokens/word: 2.5457
```

Interpretation:

```text
SP64 vocabulary can express much better morphology-compatible paths, but the
paths are longer. Run one cached score-shift sweep before moving to a custom
boundary-weighted objective.
```

Cached score-shift sweep:

```text
findings: docs/v2_0_score_shift_sweep_findings.md
stats cache:
  artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json
lambda sweep: 1, 2, 4, 8
adjusted pieces: 4592
cap check: top delta grows from about -0.53 at lambda 1 to -4.24 at lambda 8
```

Result:

```text
lambda 1 bare/finite Challenge F1: 0.7351 / 0.6755
lambda 2 bare/finite Challenge F1: 0.7351 / 0.6755
lambda 4 bare/finite Challenge F1: 0.7351 / 0.6755
lambda 8 bare/finite Challenge F1: 0.7364 / 0.6768
```

Decision:

```text
Close the post-hoc score-shift branch. The SP64 vocabulary has a high
oracle ceiling, but shallow score patching does not move the deployed
SentencePiece path toward that ceiling. Move to a real boundary-weighted
Unigram/EM objective, after methodology chores.
```

Methodology chores:

```text
findings: docs/v2_0_methodology_chore_findings.md
CI report: artifacts/v2_0_sp_model_ci_challenge_current_frontier.md
wrapper-tax report: artifacts/v2_0_finite_wrapper_eval_tax_challenge.md
```

CI result:

```text
SP64 / partial-boundary / score-shift confidence intervals overlap heavily.
Small F1 deltas in this range are visible-eval noise.
```

Wrapper-tax result:

```text
overall bare -> finite F1 delta: -0.0597
no_protected delta: -0.0180
file_like delta: -0.3042
numeric_like delta: -0.4416
apostrophe/hard_suffix feature delta: -0.1587
```

Development metric adjustment:

```text
Use bare F1 for normal-text morphology objective development.
Track finite-wrapper tax separately.
Re-verify protected stress and finite-wrapper behavior at branch end.
```

Boundary-weighted Unigram/EM spec:

```text
docs/v2_0_boundary_weighted_unigram_em_spec.md
```

First implementation should be a prototype:

```text
SP64 candidate vocab + scores
per-word lattice
forward-backward with exp(-lambda * crossings)
2k/5k train-line smoke
lambda=0 sanity check before reading morphology gains
```

Initial prototype implementation:

```text
script: scripts/materialize_v2_boundary_weighted_unigram_em.py
sweep runner: scripts/run_v2_boundary_weighted_unigram_em_sweep.py
tests:
  tests/test_v2_boundary_weighted_unigram_em.py
  tests/test_v2_boundary_weighted_unigram_em_sweep.py
  latest targeted result: 9 passed
100-line lambda=1 smoke:
  report: artifacts/v2_0_boundary_weighted_unigram_em_lambda1_iter1_100lines.md
  segments: 25486
  skipped segments: 0
  changed scores: 15479
100-line lambda=0/lambda=1 CI:
  report: artifacts/v2_0_boundary_weighted_unigram_em_100lines_ci.md
  lambda0 bare Challenge F1: 0.7392 [0.7067, 0.7664]
  lambda1 bare Challenge F1: 0.7404 [0.7104, 0.7749]
```

Interpretation:

```text
The mechanical EM path works and produces a loadable SP model. This is not yet
a quality result. The next meaningful run is a lambda0/lambda>0 controlled
2k-or-5k smoke, not tiny-LM.
```

2k controlled sweep result:

```text
report: artifacts/v2_0_boundary_weighted_unigram_em_2000lines_ci.md
findings: docs/v2_0_boundary_weighted_unigram_em_findings.md
lambda0/lambda1/lambda2/lambda4 bare F1:
  0.7383 / 0.7396 / 0.7396 / 0.7391
skipped segments: 0
```

Crossing diagnostic:

```text
lambda0 avg expected crossings/segment: 0.282770
lambda4 avg expected crossings/segment: 0.256630
lambda16 avg expected crossings/segment: 0.018998
```

Updated interpretation:

```text
The boundary penalty is mechanically active, but the current shallow EM score
branch has weak transfer to the deployed Unigram path. Do not run tiny-LM on
these models. Ask advisors whether to add aligned-piece reward/pruning or pivot
to constrained MorphBPE.
```

Fable5 follow-up probes:

```text
deployed crossing audit:
  scripts/audit_v2_deployed_sp_crossings.py
teacher-distilled score probe:
  scripts/materialize_v2_teacher_distilled_sp_model.py
findings:
  docs/v2_0_distilled_score_bound_findings.md
advisor update:
  docs/advisor_update_v2_0_distilled_score_bound.md
```

2k result:

```text
EM lambda0/1/2/4 deployed crossings are flat at 157/305 after SP64's 170/305.
Teacher-distilled 2k reduces challenge crossings to 119/305, but only reaches
0.7447 bare F1 at 2.5065 tokens/word.
```

Attribution:

```text
about 95% of remaining teacher-distilled challenge crossings come from pieces
with crossing rate >=0.70
```

Current fork:

```text
score-only global Unigram is weak
targeted inventory/pruning is not killed
next decision: full 16k teacher-distilled bound or high-rate crossing-piece
pruning/inventory probe
```

Full 16k teacher-distilled bound and first pruning probe are now complete:

```text
findings:
  docs/v2_0_distilled_score_bound_findings.md
  docs/v2_0_pruned_sp_probe_findings.md

teacher-distilled 16k:
  bare Challenge F1: 0.7509
  bare tokens/word: 2.3525
  finite Challenge F1: 0.7219
  finite tokens/word: 2.4413
  deployed crossing: 139/305

all-scope high-rate pruning:
  selected pieces: 4329
  bare F1: 0.7447
  finite F1: 0.6582
  decision: too blunt

non-word-start high-rate pruning:
  selected pieces: 403
  bare F1: 0.7486
  finite F1: 0.6875
  deployed crossing: 151/305
  decision: best small inventory probe so far, but not enough
```

Updated decision:

```text
Do not run tiny-LM.
Do not continue score-only Unigram EM/distillation.
If continuing inventory work, run only a small predeclared non-word-start
threshold sweep, then ask advisor review.
```

Rationale:

```text
The runtime boundary-biased path showed promising BPB, but failed roundtrip.
The active protected floor also failed roundtrip. That makes trainer choice
secondary until the wrapper contract is correct.
```

## Why This Plan Exists

The runtime boundary-biased decoder branch is demoted.

Reason:

```text
boundary-biased lambda0 / lambda4 failed exact roundtrip
```

The morphology signal is still useful as research evidence, but the production
shape should not be a custom runtime decoder. The next candidate should move
the prior into training-time tokenizer learning.

## Current Lessons

Accepted:

```text
finite protected routing is required
plain SP64 is compression-efficient but breaks protected spans
custom deterministic morphology is a useful teacher, not a final LLM tokenizer
markers and broad UDS improve visible F1 but do not pay enough in BPB
simple seed appendix does not transfer enough morphology signal
safe UDS7 is useful but too weak
runtime boundary-biased decode is diagnostic only until/unless lossless
```

New objective direction:

```text
learned tokenizer
+ hard protected/span routing
+ morphology-aware training-time preference
+ standard-ish encode/decode behavior
```

## Non-Negotiables

1. `decode(encode(text)) == text` must pass before any BPB claim.
2. No side-channel payload.
3. Protected spans must be preserved or explicitly represented by a finite
   lossless route.
4. Morphology must be a soft preference, not broad hard segmentation.
5. The candidate must compete against `finite_protected_sp64_numeric_sp_floor`,
   not only bare SP64.

## Small Objective Smoke Already Done

Toy implementation:

```text
src/tr_tokenizer/boundary_weighted_bpe.py
scripts/run_v2_boundary_weighted_bpe_probe.py
```

Objective:

```text
score(pair) = pair_count - lambda * morph_boundary_crossing_count
```

Smoke:

```text
train lines: 100
vocab size: 120
lambdas: 0, 4, 8
```

Challenge result:

| Model | Avg tokens/word | Boundary F1 | Crossing merges |
| --- | ---: | ---: | ---: |
| lambda 0 | 5.4856 | 0.5431 | 20 |
| lambda 4 | 5.5587 | 0.5406 | 17 |
| lambda 8 | 5.6214 | 0.5507 | 17 |

Interpretation:

```text
the boundary penalty is wired correctly
F1 moves only weakly at this tiny scale
toy Python BPE is too slow for serious sweeps
```

## Candidate Objective Options

### Option A: Boundary-Weighted BPE

Mechanism:

```text
merge_score = frequency - lambda * boundary_crossing_count
```

Pros:

```text
simplest objective to reason about
matches the toy smoke
easy to inspect crossing merges
```

Cons:

```text
BPE may be less aligned with existing SP64 Unigram baseline
custom trainer work may grow quickly
toy implementation is too slow
hard to directly produce a standard SentencePiece artifact
```

### Option B: Boundary-Weighted Unigram

Mechanism:

```text
prefer pieces aligned with high-confidence morph surfaces
penalize segmentation paths whose pieces cross teacher boundaries
learn piece scores/probabilities with boundary-aware prior
```

Pros:

```text
closer to the strongest current baseline: SP64 Unigram
aligns with lambda decoder evidence
potentially produces a standard-ish Unigram artifact
fits advisors' production-shape recommendation
```

Cons:

```text
harder to implement correctly
requires careful EM/objective design
more ways to create train/inference mismatch
```

### Option C: Two-Stage Standard SP + Post-Hoc Morph-Aware Rescore

Mechanism:

```text
train standard SP64
adjust selected piece scores or prune/replace pieces post hoc using morph stats
```

Pros:

```text
lower implementation risk
keeps closer to SentencePiece ecosystem
```

Cons:

```text
may be too weak, similar to seed appendix
can distort probabilities without a principled objective
```

## Recommended Next Step

Do not expand the toy BPE now.

Recommended order:

1. Ask advisors to choose between boundary-weighted BPE and boundary-weighted
   Unigram as the first real implementation.
2. In parallel, draft a minimal boundary-weighted Unigram spec:
   - exact boundary source
   - confidence classes
   - penalty/reward formula
   - training/encoding parity
   - lossless decode requirements
3. Build only a small prototype after this objective choice is clear.

## Stop Criteria

Stop or redesign if:

```text
candidate cannot be exact-roundtrip
candidate cannot preserve protected spans
token pressure approaches marker/UDS22 band without large F1/BPB gain
hidden/normal-text-only F1 does not improve over protected floor
non-Turkish/code bloat exceeds a small threshold
implementation requires a large custom runtime decoder
```

## Success Criteria For First Real Prototype

Before tiny-LM:

```text
exact roundtrip passes on eval/probe split
protected stress remains 25/25
tokens/raw byte <= finite_protected_sp64_numeric_sp_floor + small margin
normal-text-only F1 materially improves over protected floor
no multilingual/code smoke regression
```

Before LLM-team experimental handoff:

```text
large roundtrip audit
protected/do-no-harm report
normal-text-only and hidden F1
token pressure table
seeded tiny-LM BPB
clear caveats: experimental, not production
```
