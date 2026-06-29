# v2.0 Boundary-Weighted Unigram/EM Runbook

Date: 2026-06-10

## Purpose

Run the first controlled boundary-weighted Unigram/EM sweep.

This is still an intrinsic/objective diagnostic. Do not run tiny-LM from these
models until the intrinsic frontier moves clearly beyond the visible-eval noise
floor.

## Current Smoke

Already completed:

```text
lambda0/lambda1
train lines: 100
iterations: 1
skipped segments: 0
```

Result:

```text
lambda0 bare Challenge F1: 0.7392
lambda1 bare Challenge F1: 0.7404
```

Interpretation:

```text
mechanical path works; 100 lines is not a quality result
```

## 2k Sweep Status

Completed:

```text
lambda: 0, 1, 2, 4
train lines: 2000
iterations: 1
```

Report:

```text
artifacts/v2_0_boundary_weighted_unigram_em_2000lines_ci.md
```

Result:

```text
lambda0/lambda1/lambda2/lambda4 bare F1:
  0.7383 / 0.7396 / 0.7396 / 0.7391
skipped segments: 0
```

Decision:

```text
do not repeat this exact sweep by default
do not run tiny-LM on these models
```

## Historical 2k Sweep Command

The command below is retained for reproducibility, not as the next default
action.

```text
lambda: 0, 1, 2, 4
train lines: 2000
iterations: 1
```

Stop early if any run reports non-zero skipped segments at meaningful scale, or
if runtime is unexpectedly high.

### One-Command Run

This command materializes all four models and then writes the CI report.

```powershell
python scripts\run_v2_boundary_weighted_unigram_em_sweep.py `
  --lambdas 0,1,2,4 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --ci-samples 1000
```

Expected output pattern:

```text
iteration=1 scanned 500 lines ...
iteration=1 scanned 1000 lines ...
iteration=1 scanned 1500 lines ...
iteration=1 scanned 2000 lines ...
sweep_complete
```

Expected final CI report:

```text
artifacts/v2_0_boundary_weighted_unigram_em_2000lines_ci.md
```

Use `--dry-run` first if you want to see the exact commands without running the
sweep.

### Materialize Models

Manual equivalent, if you prefer step-by-step execution:

```powershell
python scripts\materialize_v2_boundary_weighted_unigram_em.py `
  --boundary-lambda 0 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --out-model artifacts\private\v2_0_boundary_weighted_unigram_em\lambda0_iter1_2000lines_unigram_64000.model `
  --out-vocab artifacts\private\v2_0_boundary_weighted_unigram_em\lambda0_iter1_2000lines_unigram_64000.vocab `
  --report-out artifacts\v2_0_boundary_weighted_unigram_em_lambda0_iter1_2000lines.md
```

```powershell
python scripts\materialize_v2_boundary_weighted_unigram_em.py `
  --boundary-lambda 1 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --out-model artifacts\private\v2_0_boundary_weighted_unigram_em\lambda1_iter1_2000lines_unigram_64000.model `
  --out-vocab artifacts\private\v2_0_boundary_weighted_unigram_em\lambda1_iter1_2000lines_unigram_64000.vocab `
  --report-out artifacts\v2_0_boundary_weighted_unigram_em_lambda1_iter1_2000lines.md
```

```powershell
python scripts\materialize_v2_boundary_weighted_unigram_em.py `
  --boundary-lambda 2 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --out-model artifacts\private\v2_0_boundary_weighted_unigram_em\lambda2_iter1_2000lines_unigram_64000.model `
  --out-vocab artifacts\private\v2_0_boundary_weighted_unigram_em\lambda2_iter1_2000lines_unigram_64000.vocab `
  --report-out artifacts\v2_0_boundary_weighted_unigram_em_lambda2_iter1_2000lines.md
```

```powershell
python scripts\materialize_v2_boundary_weighted_unigram_em.py `
  --boundary-lambda 4 `
  --iterations 1 `
  --max-lines 2000 `
  --progress 500 `
  --out-model artifacts\private\v2_0_boundary_weighted_unigram_em\lambda4_iter1_2000lines_unigram_64000.model `
  --out-vocab artifacts\private\v2_0_boundary_weighted_unigram_em\lambda4_iter1_2000lines_unigram_64000.vocab `
  --report-out artifacts\v2_0_boundary_weighted_unigram_em_lambda4_iter1_2000lines.md
```

### Evaluate CI

```powershell
python scripts\report_v2_sp_model_ci.py `
  --dataset data\eval\tr_challenge.tsv `
  --numeric-sp-passthrough `
  --samples 1000 `
  --model em_l0_2k=artifacts\private\v2_0_boundary_weighted_unigram_em\lambda0_iter1_2000lines_unigram_64000.model `
  --model em_l1_2k=artifacts\private\v2_0_boundary_weighted_unigram_em\lambda1_iter1_2000lines_unigram_64000.model `
  --model em_l2_2k=artifacts\private\v2_0_boundary_weighted_unigram_em\lambda2_iter1_2000lines_unigram_64000.model `
  --model em_l4_2k=artifacts\private\v2_0_boundary_weighted_unigram_em\lambda4_iter1_2000lines_unigram_64000.model `
  --report-out artifacts\v2_0_boundary_weighted_unigram_em_2000lines_ci.md
```

## Reading

Promising:

```text
lambda > 0 improves bare F1 over lambda0 by a visible margin
tokens/word does not jump toward the hard no-cross oracle
skipped segments remain 0 or negligible
```

Not promising:

```text
lambda curve is flat inside CI
token pressure rises but F1 stays flat
lambda0 itself diverges so much that the family baseline is unstable
```
