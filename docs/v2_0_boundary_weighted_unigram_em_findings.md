# v2.0 Boundary-Weighted Unigram/EM Findings

Date: 2026-06-10

## Purpose

Test whether a boundary-weighted Unigram/EM objective can move a standard-ish
SP64 Unigram artifact toward Turkish morphology-aligned paths without returning
to broad hard segmentation.

This is still an intrinsic diagnostic branch, not an LLM-ready tokenizer.

## Implementation

Prototype:

```text
scripts/materialize_v2_boundary_weighted_unigram_em.py
```

Sweep runner:

```text
scripts/run_v2_boundary_weighted_unigram_em_sweep.py
```

Tests:

```text
tests/test_v2_boundary_weighted_unigram_em.py
tests/test_v2_boundary_weighted_unigram_em_sweep.py
```

Latest targeted test result:

```text
9 passed
```

## 2k One-Iteration Sweep

Command:

```powershell
python scripts\run_v2_boundary_weighted_unigram_em_sweep.py `
  --lambdas 0,1,2,4 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --ci-samples 1000
```

All runs had full lattice coverage:

```text
lines: 2000
segments: 343822
skipped segments: 0
expected piece types: 40686
```

CI report:

```text
artifacts/v2_0_boundary_weighted_unigram_em_2000lines_ci.md
```

| Model | Bare Challenge F1 | Bare avg tokens/word | Finite Challenge F1 | Finite avg tokens/word |
| --- | ---: | ---: | ---: | ---: |
| lambda 0 | 0.7383 | 2.2402 | 0.6767 | 2.3368 |
| lambda 1 | 0.7396 | 2.2402 | 0.6780 | 2.3368 |
| lambda 2 | 0.7396 | 2.2402 | 0.6780 | 2.3368 |
| lambda 4 | 0.7391 | 2.2428 | 0.6802 | 2.3394 |

Interpretation:

```text
lambda 1/2/4 do not produce a material F1 movement over lambda 0.
All point estimates remain inside the visible-eval CI noise floor.
```

## Expected Crossing Diagnostic

After the 2k sweep, the prototype report was updated to include expected
crossings under the training lattice posterior.

100-line diagnostic:

| Lambda | Avg expected crossings/segment | Bare Challenge F1 | Bare avg tokens/word |
| ---: | ---: | ---: | ---: |
| 0 | 0.282770 | 0.7392 | 2.3133 |
| 4 | 0.256630 | 0.7308 | 2.3107 |
| 16 | 0.018998 | 0.7410 | 2.4230 |

Diagnostic reports:

```text
artifacts/v2_0_boundary_weighted_unigram_em_lambda0_iter1_100lines.md
artifacts/v2_0_boundary_weighted_unigram_em_lambda4_iter1_100lines.md
artifacts/v2_0_boundary_weighted_unigram_em_lambda16_iter1_100lines.md
artifacts/v2_0_boundary_weighted_unigram_em_100lines_high_lambda_ci.md
```

Interpretation:

```text
The boundary penalty is mechanically active.

Low lambda reduces expected crossings only mildly and does not move eval.
High lambda sharply reduces expected crossings but increases token pressure and
still does not produce a clear visible F1 gain at this smoke scale.
```

## Decision

Do not run tiny-LM on the current boundary-weighted EM models.

Do not run a 5k or multi-iteration sweep as the next default step unless we
first change the objective or add a stronger diagnostic reason.

Current branch status:

```text
mechanically valid
full lattice coverage
weak intrinsic transfer
not promoted
```

## Most Likely Explanation

The objective is affecting the training posterior, but the score changes do not
move the standard Unigram argmax path enough at deploy time unless lambda is
made very large. At large lambda, the model starts paying token-pressure cost
without a corresponding F1 gain.

This resembles the earlier post-hoc score-shift failure:

```text
SP64 vocab has morphology-compatible paths, but shallow score/probability
reshaping is not enough to select them reliably.
```

## Next Recommendation

Do not keep increasing lambda blindly.

The next useful move is one of:

```text
1. Ask advisors whether this EM result is enough to stop the shallow
   Unigram-score branch.
2. If continuing locally, change mechanism rather than just scale:
   - add aligned-piece reward as well as crossing penalty
   - prune high-crossing full-word pieces instead of only lowering probability
   - train a new candidate inventory, not only rescore SP64 inventory
3. Revisit a constrained BPE/MorphBPE trainer where boundary-crossing merge
   decisions are explicit and inspectable.
```

Current Codex recommendation:

```text
pause this EM branch here, document it as weak transfer, and ask Fable5 whether
to try aligned-piece reward/pruning or pivot to constrained MorphBPE.
```
