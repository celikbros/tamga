# v2.1 Passthrough Protected Sidecar Handoff Contract

Date: 2026-06-13

## Decision

The practical v2.1 protected-span baseline is:

```text
sp64_protected_passthrough_sidecar
```

This is a lossless SP64-family tokenizer path with protected-span sidecar
metadata. It intentionally does not force protected spans to align with token
boundaries.

## Why This Is The Baseline

Advisor feedback split between global pre-split alignment and passthrough
sidecar. The project decision is to choose passthrough as the reversible,
lower-cost baseline.

Reasons:

```text
near-SP64 token pressure
exact roundtrip on valid/test
no permanent +3.8% token/raw-byte tax
model-token stream remains decoupled from detector changes
protected metadata can be patched without retraining the model
PII/redaction can use byte offsets plus conservative boundary-token over-mask
```

The pre-split sidecar remains a documented optional variant for consumers that
prove token-boundary alignment is required.

## Tokenizer Shape

Model token vocabulary:

```text
64000 SP64 Unigram pieces
+ 256 UTF-8 byte fallback ids
= 64256 ids
```

There are no finite route-token ids in this baseline.

Normal text:

```text
encoded with SP64
```

True SP unknowns:

```text
encoded with UTF-8 byte fallback
```

Protected spans:

```text
detected and recorded in sidecar metadata
SP64 tokenization is otherwise allowed to pass through
```

## Guarantees

This baseline guarantees:

```text
lossless reconstruction through tokenizer decode plus sidecar-aware text path
exact byte offsets for detected protected spans
route labels for detected protected spans
stable model-token stream under detector metadata-only improvements
```

Measured on the v1.8 filtered split:

| Metric | Valid | Test |
| --- | ---: | ---: |
| tokens/raw byte | 0.159026 | 0.159660 |
| exact roundtrip | 1994/1994 | 1998/1998 |
| fallback source token rate | 0.000062 | 0.000324 |

## Non-Guarantees

This baseline does not guarantee:

```text
protected spans start/end at token boundaries
no token straddles a protected-span edge
exact token-index ranges for every protected span without byte-offset mapping
base-model exact-copy or constrained decoding over protected spans
```

Measured protected edge alignment on the v1.8 filtered split:

| Split | Protected edge alignment |
| --- | ---: |
| valid | 0.453798 |
| test | 0.463721 |

## Safe Operation Policy

Recommended handling for protected spans:

```text
1. Prefer raw-text redaction before tokenization when possible.
2. For output redaction, decode/reconstruct text and apply sidecar byte offsets.
3. For training loss masking, map byte spans to overlapping token spans and
   conservatively over-mask any straddling boundary tokens.
4. Do not assume exact token-index span boundaries unless using a pre-split
   variant.
```

This policy is the reason passthrough is acceptable despite edge fuzz.

## Optional Pre-Split Variant

Optional variant:

```text
sp64_protected_presplit_sidecar
```

Use it only if a downstream consumer proves one of these is a committed
base-model requirement:

```text
exact token-span copy of protected entities
grammar/constrained decoding keyed to protected token spans
security policy that cannot tolerate over-masking boundary tokens
token-index-only infrastructure with no byte-offset reconciliation
```

Pre-split status:

| Metric | Valid | Test |
| --- | ---: | ---: |
| tokens/raw byte | 0.165261 | 0.165755 |
| exact roundtrip | 1994/1994 | 1998/1998 |
| protected edge alignment | 1.000000 | 1.000000 |

Measured tax versus passthrough:

```text
0.165755 - 0.159660 = +0.006095 tokens/raw byte
about +3.8%
```

## Detector Battery

The first generated adversarial detector battery now passes:

```text
cases: 61
expected protected spans: 62
precision/recall/F1: 1.000000 / 1.000000 / 1.000000
```

Covered categories:

```text
protected suffix attachment
percent-encoded suffix
numeric suffix attachment
span-adjacent punctuation
line-edge spans
nested/comparator spans
```

This battery is not proof of final detector robustness. It is the first
pre-split safety gate and an ongoing regression suite.

## Route Density Pilot Audit

Pilot density on the full v1.8 filtered train/valid/test split:

```text
artifact: artifacts/v2_1_sidecar_route_density_audit_train_valid_test.md
token pressure mode: false
```

| Split | Lines | Raw bytes | Protected spans | Protected bytes/raw byte | Protected line share |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 16000 | 22819852 | 76373 | 0.016343 | 0.742125 |
| valid | 1994 | 2843294 | 9552 | 0.016460 | 0.757272 |
| test | 1998 | 2781995 | 9237 | 0.016954 | 0.736236 |
| all | 19992 | 28445141 | 95162 | 0.016414 | 0.743047 |

Dominant route classes on train+valid+test:

| Route | Occurrences | Bytes/raw byte | Line share |
| --- | ---: | ---: | ---: |
| numeric_like | 80938 | 0.009804 | 0.665316 |
| file_like | 8005 | 0.004528 | 0.208033 |
| apostrophe_surface | 3662 | 0.001336 | 0.092537 |
| non_turkish_latin_word | 1644 | 0.000615 | 0.015256 |
| percent_encoded | 163 | 0.000017 | 0.006403 |

Interpretation:

```text
protected material is common by line but small by byte share on this pilot
the largest exposure is numeric_like, followed by file_like
train, valid, and test have similar protected-byte density
future alignment work should be selective by route class, not global by default
```

## Downstream Mask Simulation

We simulated the safe training-mask policy for passthrough sidecar:

```text
protected byte span -> all overlapping SP tokens -> conservative over-mask
artifact: artifacts/v2_1_sidecar_operation_simulation_train_valid_test.md
private samples:
  artifacts/private/v2_1_sidecar_operation_simulation_train_valid_test.samples.jsonl
```

Full v1.8 train/valid/test result:

| Metric | Value |
| --- | ---: |
| lines | 19992 |
| raw bytes | 28445141 |
| protected spans | 95162 |
| protected bytes/raw byte | 0.016414 |
| conservative mask bytes | 583535 |
| extra mask bytes | 116633 |
| extra mask bytes/raw byte | 0.004100 |
| extra/protected byte | 0.249802 |
| edge-aligned span rate | 0.073916 |
| crossing span rate | 0.926084 |
| avg tokens/protected span | 1.835123 |
| max extra bytes/span | 9 |

Route contribution to extra over-mask:

| Route | Spans | Extra bytes | Extra/protected byte |
| --- | ---: | ---: | ---: |
| numeric_like | 80938 | 106852 | 0.383150 |
| file_like | 8005 | 7790 | 0.060487 |
| apostrophe_surface | 3662 | 3201 | 0.084259 |
| non_turkish_latin_word | 1644 | 1368 | 0.078176 |
| percent_encoded | 163 | 262 | 0.535787 |

Interpretation:

```text
passthrough is not suitable for exact token-index protected spans
conservative token masking is operationally cheap on this pilot:
  about 0.41% extra raw bytes masked
numeric_like accounts for most extra masking
if token-boundary alignment becomes necessary, test selective alignment by
route class before global pre-split
```

Real-mix confirmation:

```text
sample:
  artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
materialization:
  artifacts/v2_1_real_mix_text_sample_materialization_60k.md
operation simulation:
  artifacts/v2_1_sidecar_operation_simulation_real_mix.md
private samples:
  artifacts/private/v2_1_sidecar_operation_simulation_real_mix.samples.jsonl
```

| Metric | 20k pilot | Real mix sample |
| --- | ---: | ---: |
| lines | 19992 | 40388 |
| raw bytes | 28445141 | 44351801 |
| protected spans | 95162 | 149999 |
| protected bytes/raw byte | 0.016414 | 0.015398 |
| extra mask bytes/raw byte | 0.004100 | 0.003983 |
| extra/protected byte | 0.249802 | 0.258681 |
| edge-aligned span rate | 0.073916 | 0.077861 |
| crossing span rate | 0.926084 | 0.922139 |
| max extra bytes/span | 9 | 9 |

Real-mix route contribution to extra over-mask:

| Route | Spans | Extra bytes | Extra/protected byte |
| --- | ---: | ---: | ---: |
| numeric_like | 127588 | 160582 | 0.369251 |
| file_like | 10309 | 9588 | 0.068213 |
| apostrophe_surface | 7579 | 6477 | 0.092804 |
| non_turkish_latin_word | 3228 | 2395 | 0.079210 |
| percent_encoded | 171 | 278 | 0.541910 |

Real-mix reading:

```text
the stronger mixed-domain sample confirms the pilot result
conservative masking remains below 0.4% extra raw bytes
numeric_like is still the main extra-mask driver
global pre-split is not justified by masking/redaction cost alone
```

Real-mix token-pressure confirmation:

```text
artifact: artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
```

| Metric | Value |
| --- | ---: |
| SP tokens/raw byte | 0.167769 |
| passthrough tokens/raw byte | 0.167822 |
| pre-split tokens/raw byte | 0.173911 |
| pre-split tax tokens/raw byte | 0.006088 |
| pre-split relative tax | 0.036279 |

Interpretation:

```text
real-mix token pressure confirms the pilot estimate; global pre-split costs
about 3.6% additional tokens on this stronger sample.
```

## 20M Tiny-LM BPB

The selected v2.1 baseline now has a completed 20M fixed-byte tiny-LM row:

```text
artifact: artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

| Metric | Value |
| --- | ---: |
| steps | 6042 |
| approx bytes seen | 19998919 |
| final valid BPB | 1.935810 |
| test BPB | 1.947129 |
| valid bits/token | 12.1730 |
| test bits/token | 12.1955 |

This is a model-loss reference for the chosen sidecar contract. It is not a
claim that this is a final production tokenizer.

## Current Artifacts

Config:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
```

Reports:

```text
artifacts/v2_1_tiny_lm_passthrough_sidecar_dry_run.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test.md
artifacts/v2_1_tiny_lm_presplit_sidecar_dry_run.md
artifacts/v2_1_presplit_sidecar_roundtrip_valid.md
artifacts/v2_1_presplit_sidecar_roundtrip_test.md
artifacts/v2_1_protected_boundary_alignment_presplit_sidecar_audit.md
artifacts/v2_1_sidecar_detector_adversarial_battery.md
artifacts/v2_1_sidecar_route_density_audit_valid_test.md
artifacts/v2_1_sidecar_route_density_audit_train_valid_test.md
artifacts/v2_1_sidecar_operation_simulation_train_valid_test.md
artifacts/v2_1_real_mix_text_sample_materialization_60k.md
artifacts/v2_1_sidecar_operation_simulation_real_mix.md
artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

Decision docs:

```text
docs/advisor_feedback_v2_1_sidecar_contract_triage.md
docs/v2_1_presplit_sidecar_findings.md
docs/v2_1_passthrough_sidecar_runbook.md
docs/v2_1_regression_checklist.md
docs/v2_1_closure_gauntlet_findings.md
```

Regression artifacts:

```text
artifacts/v2_1_sidecar_detector_adversarial_battery_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test_regression.md
```

## Next Gates

Do not run global pre-split training unless a consumer commits to token-boundary
protected spans.

Recommended next sequence:

```text
1. Treat passthrough sidecar as v2.1 practical baseline.
2. If an LM-loss row is needed, run a 20M fixed-byte tiny-LM row for passthrough
   sidecar only.
3. Real-mix operation simulation is complete and supports the passthrough
   baseline for masking/redaction. If the future pretraining mix changes
   substantially, rerun the same audit before reopening global alignment.
4. If exact-copy/constrained decoding becomes required, test selective pre-split
   by route class before global pre-split.
```
