# v2.1 Passthrough Sidecar Runbook

Date: 2026-06-13

## Current Baseline

```text
sp64_protected_passthrough_sidecar
```

Use this as the v2.1 practical protected-span baseline unless a downstream
consumer proves token-boundary-aligned protected spans are required.

Contract:

```text
docs/v2_1_final_handoff_package.md
docs/v2_1_passthrough_sidecar_handoff_contract.md
```

## Already Completed

Dry-run/token pressure:

```text
artifacts/v2_1_tiny_lm_passthrough_sidecar_dry_run.md
```

Roundtrip:

```text
artifacts/v2_1_passthrough_sidecar_roundtrip_valid.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test.md
```

Detector battery:

```text
artifacts/v2_1_sidecar_detector_adversarial_battery.md
```

Pilot protected-route density:

```text
artifacts/v2_1_sidecar_route_density_audit_train_valid_test.md
```

Downstream operation simulation:

```text
artifacts/v2_1_sidecar_operation_simulation_train_valid_test.md
```

Real-mix route density with token pressure:

```text
artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
```

20M tiny-LM BPB:

```text
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

Regression checklist:

```text
docs/v2_1_regression_checklist.md
```

Latest regression lock:

| Check | Result |
| --- | ---: |
| targeted unit tests | 44 passed |
| detector battery | 61 cases, 62 expected spans, F1 1.000000 |
| valid roundtrip | 1994/1994 |
| test roundtrip | 1998/1998 |
| dry-run test tokens/raw byte | 0.159660 |
| 20M test BPB | 1.947129 |

Route invariant:

```text
percent_encoded and azerbaijani_word must remain in the sidecar passthrough
route lists.
```

Summary:

| Scope | Lines | Raw bytes | Protected spans | Protected bytes/raw byte | Protected line share |
| --- | ---: | ---: | ---: | ---: | ---: |
| train+valid+test | 19992 | 28445141 | 95162 | 0.016414 | 0.743047 |

Dominant routes:

| Route | Occurrences | Bytes/raw byte |
| --- | ---: | ---: |
| numeric_like | 80938 | 0.009804 |
| file_like | 8005 | 0.004528 |
| apostrophe_surface | 3662 | 0.001336 |

Conservative token-mask simulation:

| Metric | Value |
| --- | ---: |
| extra mask bytes/raw byte | 0.004100 |
| extra/protected byte | 0.249802 |
| edge-aligned span rate | 0.073916 |
| crossing span rate | 0.926084 |
| max extra bytes/span | 9 |

Reading:

```text
passthrough is not token-boundary aligned, but conservative masking only
over-masks about 0.41% of raw bytes on this pilot.
```

Real-mix token-pressure confirmation:

| Metric | Value |
| --- | ---: |
| SP tokens/raw byte | 0.167769 |
| passthrough tokens/raw byte | 0.167822 |
| pre-split tokens/raw byte | 0.173911 |
| pre-split tax tokens/raw byte | 0.006088 |
| pre-split relative tax | 0.036279 |

Relevant dry-run estimate:

```text
train tokens/raw byte: 0.154684
target raw bytes: 20,000,000
tokens per step: 512
estimated steps: 6042
```

## Do Not Run

Do not run this right now:

```text
sp64_protected_presplit_sidecar 20M
```

Reason:

```text
pre-split is no longer the v2.1 baseline
global token-boundary alignment is an optional downstream requirement, not the
default tokenizer contract
```

## Completed Long Run: Passthrough 20M BPB

The selected v2.1 baseline has a completed 20M fixed-byte row:

```text
report: artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
private stats: artifacts/private/v2_1_tiny_lm_passthrough_sidecar_20mbytes/encoded_stats.jsonl
```

| Metric | Value |
| --- | ---: |
| max steps | 6042 |
| approx bytes seen | 19998919 |
| final valid BPB | 1.935810 |
| test BPB | 1.947129 |
| valid bits/token | 12.1730 |
| test bits/token | 12.1955 |

Do not rerun this unless the tokenizer config or detector changes.

## Optional Comparator

If we later need to quantify the pre-split tax in BPB, run pre-split with the
same seed and approximately matched byte budget. Do not run this unless the
project explicitly re-opens the token-boundary-alignment question.

PowerShell:

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_1_tiny_lm_edge_safe_route_passthrough.toml `
  --tokenizer sp64_protected_presplit_sidecar `
  --max-steps 6294 `
  --eval-interval 500 `
  --encode-progress 5000 `
  --report-out artifacts\v2_1_tiny_lm_presplit_sidecar_20mbytes.md `
  --output-dir artifacts\private\v2_1_tiny_lm_presplit_sidecar_20mbytes
```

## Next Non-Training Check

Before any future global pre-split decision, measure protected-route density on
the intended real pretraining mix. The v1.8 pilot may understate or overstate
the true alignment tax depending on code/URL/file-like density.

The fast train/valid/test pilot audit is complete:

```powershell
python scripts\audit_v2_1_sidecar_route_density.py `
  --split-dir artifacts\private\v1_8_local_lm_probe\celik_tr_primary_multilingual_mix_lm_probe_pilot_20k\filtered_split `
  --split train --split valid --split test `
  --progress 5000 `
  --report-out artifacts\v2_1_sidecar_route_density_audit_train_valid_test.md
```

Next useful density check is a large real pretraining sample. Point `--input`
at the sampled raw text:

```powershell
python scripts\audit_v2_1_sidecar_route_density.py `
  --input path\to\real_pretraining_sample.txt `
  --progress 5000 `
  --report-out artifacts\v2_1_sidecar_route_density_audit_real_mix.md
```

Use `--with-token-pressure` only on small samples or when the extra encoding
cost is acceptable:

```powershell
python scripts\audit_v2_1_sidecar_route_density.py `
  --split-dir artifacts\private\v1_8_local_lm_probe\celik_tr_primary_multilingual_mix_lm_probe_pilot_20k\filtered_split `
  --split valid --split test `
  --with-token-pressure `
  --progress 500 `
  --report-out artifacts\v2_1_sidecar_route_density_audit_valid_test_with_pressure.md
```

## Optional Stronger Simulation

Do not pass a placeholder path such as `path\to\real_pretraining_sample.txt`.
Use a real UTF-8 text file. For JSONL corpus files, first materialize the
`text` field into a raw text sample.

Example: create a mixed JSONL-derived sample:

```powershell
python scripts\materialize_v2_1_real_mix_text_sample.py `
  --source data\train\private\celik_ai\trt_news_corpus.jsonl:20000:trt_news `
  --source data\train\private\celik_ai\academic_corpus.jsonl:20000:academic `
  --source data\train\private\celik_ai\ttk_corpus.jsonl:20000:ttk `
  --out artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --report-out artifacts\v2_1_real_mix_text_sample_materialization_60k.md
```

This 60k command has been run once:

```text
report: artifacts/v2_1_real_mix_text_sample_materialization_60k.md
output: artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
scanned/written lines: 40388 / 40388
output bytes: 44392189
sources:
  trt_news: 388 lines, 1083409 bytes
  academic: 20000 lines, 27009371 bytes
  ttk: 20000 lines, 16299409 bytes
```

Then run the downstream mask simulation:

```powershell
python scripts\audit_v2_1_sidecar_operation_simulation.py `
  --input artifacts\private\v2_1_real_mix\real_mix_60k_sample.txt `
  --progress 5000 `
  --report-out artifacts\v2_1_sidecar_operation_simulation_real_mix.md `
  --samples-out artifacts\private\v2_1_sidecar_operation_simulation_real_mix.samples.jsonl
```

Use this before changing the tokenizer contract. If extra mask bytes/raw byte
stays small, passthrough remains the practical baseline. If one route dominates,
test selective pre-split for that route before global pre-split.

Real-mix simulation completed:

```text
sample:
  artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
materialization report:
  artifacts/v2_1_real_mix_text_sample_materialization_60k.md
operation report:
  artifacts/v2_1_sidecar_operation_simulation_real_mix.md
lines: 40388
raw bytes: 44351801
protected bytes/raw byte: 0.015398
extra mask bytes/raw byte: 0.003983
extra/protected byte: 0.258681
max extra bytes/span: 9
dominant extra-mask route:
  numeric_like: 160582 extra bytes
```

Smoke check also completed:

```text
sample:
  artifacts/private/v2_1_real_mix/real_mix_smoke.txt
materialization report:
  artifacts/v2_1_real_mix_text_sample_materialization_smoke.md
operation report:
  artifacts/v2_1_sidecar_operation_simulation_real_mix_smoke.md
```
