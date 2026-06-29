# v2.1 Regression Checklist

Date: 2026-06-13

## Purpose

This checklist locks the current v2.1 protected sidecar baseline:

```text
sp64_protected_passthrough_sidecar
```

Use it before changing protected-span routes, detector behavior, decode logic,
or the v2.1 handoff docs.

## Current Required Result

The baseline must satisfy:

| Check | Required result |
| --- | ---: |
| valid exact roundtrip | 1994/1994 |
| test exact roundtrip | 1998/1998 |
| detector battery precision/recall/F1 | 1.000000 / 1.000000 / 1.000000 |
| targeted unit tests | pass |
| dry-run train tokens/raw byte | 0.154684 |
| dry-run valid tokens/raw byte | 0.159026 |
| dry-run test tokens/raw byte | 0.159660 |
| 20M test BPB | 1.947129 |

## Important Regression Caught

After adding `percent_encoded` as a protected route, the v2.1 passthrough config
briefly failed exact roundtrip:

```text
valid: 1979/1994
test: 1989/1998
```

Root cause:

```text
percent_encoded was detected as protected, but was missing from the
sp_passthrough_routes list. Percent-encoded spans such as %20 fell back to byte
ids, and the following SP dummy-prefix space could decode as an extra space.
```

Fix:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml now includes
percent_encoded in the sidecar passthrough route lists.

scripts/audit_v2_1_sidecar_route_density.py includes percent_encoded in its
default passthrough route set.

tests/test_tiny_lm_bpb_probe.py includes a regression test that verifies all
v2.1 sidecar tokenizer configs include percent_encoded.
```

The v2.2 full real-mix smoke caught the same bug class for `azerbaijani_word`:

```text
route detected as protected
route missing from sp_passthrough_routes
byte fallback decoded with an extra SP dummy-prefix space
```

Fix:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml now includes
azerbaijani_word in the sidecar passthrough route lists.

scripts/audit_v2_1_sidecar_route_density.py includes azerbaijani_word in its
default passthrough route set.

tests/test_tiny_lm_bpb_probe.py verifies both percent_encoded and
azerbaijani_word are present in all v2.1 sidecar tokenizer configs.
```

## Regression Commands

Compile helpers:

```powershell
python -m py_compile scripts\audit_v2_sidecar_detector_battery.py scripts\audit_v2_1_sidecar_route_density.py scripts\audit_v2_1_sidecar_operation_simulation.py scripts\materialize_v2_1_real_mix_text_sample.py
```

Targeted unit tests:

```powershell
$env:TEMP='C:\tmp'; $env:TMP='C:\tmp'; python -m pytest tests\test_pretok.py tests\test_tiny_lm_bpb_probe.py tests\test_v2_1_sidecar_operation_simulation.py tests\test_v2_1_real_mix_text_sample.py
```

Detector battery:

```powershell
python scripts\audit_v2_sidecar_detector_battery.py `
  --report-out artifacts\v2_1_sidecar_detector_adversarial_battery_regression.md `
  --jsonl-out artifacts\private\v2_1_sidecar_detector_adversarial_battery_regression.jsonl
```

Passthrough roundtrip, valid:

```powershell
python scripts\audit_v2_boundary_roundtrip.py configs\v2_1_tiny_lm_edge_safe_route_passthrough.toml `
  --tokenizer sp64_protected_passthrough_sidecar `
  --split valid `
  --progress 500 `
  --report-out artifacts\v2_1_passthrough_sidecar_roundtrip_valid_regression.md `
  --private-out artifacts\private\v2_1_passthrough_sidecar_roundtrip_valid_regression.failures.jsonl
```

Passthrough roundtrip, test:

```powershell
python scripts\audit_v2_boundary_roundtrip.py configs\v2_1_tiny_lm_edge_safe_route_passthrough.toml `
  --tokenizer sp64_protected_passthrough_sidecar `
  --split test `
  --progress 500 `
  --report-out artifacts\v2_1_passthrough_sidecar_roundtrip_test_regression.md `
  --private-out artifacts\private\v2_1_passthrough_sidecar_roundtrip_test_regression.failures.jsonl
```

Passthrough dry-run/token pressure:

```powershell
python scripts\run_tiny_lm_bpb_probe.py configs\v2_1_tiny_lm_edge_safe_route_passthrough.toml `
  --tokenizer sp64_protected_passthrough_sidecar `
  --dry-run `
  --encode-progress 5000 `
  --report-out artifacts\v2_1_tiny_lm_passthrough_sidecar_dry_run.md `
  --output-dir artifacts\private\v2_1_tiny_lm_passthrough_sidecar_dry_run
```

## Latest Regression Result

Latest run:

| Check | Result |
| --- | ---: |
| helper py_compile | pass |
| targeted unit tests | 44 passed |
| `tests/test_tiny_lm_bpb_probe.py` after route-lock test | 20 passed |
| detector battery | 61 cases, 62 expected spans, F1 1.000000 |
| valid roundtrip | 1994/1994 |
| test roundtrip | 1998/1998 |
| dry-run train tokens/raw byte | 0.154684 |
| dry-run valid tokens/raw byte | 0.159026 |
| dry-run test tokens/raw byte | 0.159660 |
| real-mix pre-split tax | +0.006088 tokens/raw byte |
| real-mix pre-split relative tax | 0.036279 |
| 20M test BPB | 1.947129 |

Artifacts:

```text
artifacts/v2_1_sidecar_detector_adversarial_battery_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test_regression.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_dry_run.md
artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

## Fail Conditions

Do not freeze or hand off v2.1 if any of these occur:

```text
valid/test exact roundtrip drops below 1.000000
detector battery has any false positive or false negative
percent_encoded is removed from sidecar passthrough route lists
fallback source tokens increase without a route-level explanation
token pressure changes without updating the handoff docs
```
