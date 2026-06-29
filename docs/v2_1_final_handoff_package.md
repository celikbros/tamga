# v2.1 Final Handoff Package: Protected Passthrough Sidecar

Date: 2026-06-13

## Decision

The v2.1 practical protected-span baseline is:

```text
sp64_protected_passthrough_sidecar
```

This should be treated as the current experimental tokenizer contract for
protected spans. It is not a final production tokenizer recommendation.

## One-Line Summary

Use ordinary SP64-family model tokens plus exact byte-offset sidecar metadata
for protected spans. Do not force global token-boundary alignment unless a
downstream consumer explicitly requires exact token-index protected spans.

## Tokenizer Shape

```text
64000 SP64 Unigram pieces
+ 256 UTF-8 byte fallback ids
= 64256 model ids
```

There are no finite route-token ids in this v2.1 baseline.

Normal text:

```text
SP64 Unigram
```

True SP unknowns:

```text
UTF-8 byte fallback
```

Protected spans:

```text
recorded in sidecar metadata by exact byte offsets and route labels
model-token stream remains normal SP64 passthrough
```

## Guarantees

This baseline guarantees:

```text
exact roundtrip on the v1.8 valid/test filtered split
exact protected-span byte offsets in sidecar metadata
route labels for detected protected spans
stable model-token stream under detector metadata-only improvements
low token-pressure relative to bare SP64
```

Measured token pressure:

| Split | Tokens/raw byte | Exact roundtrip | Fallback source rate |
| --- | ---: | ---: | ---: |
| train | 0.154684 | n/a | 0.000028 |
| valid | 0.159026 | 1994/1994 | 0.000062 |
| test | 0.159660 | 1998/1998 | 0.000324 |

## Non-Guarantees

This baseline does not guarantee:

```text
protected spans start/end at model-token boundaries
no model token straddles a protected-span edge
exact token-index ranges for every protected span
base-model exact copy of protected spans
grammar/constrained decoding over protected token spans
```

Measured protected edge alignment:

| Split | Protected edge alignment |
| --- | ---: |
| valid | 0.453798 |
| test | 0.463721 |

Do not present this tokenizer as token-boundary protected. It is byte-sidecar
protected.

## Safe Consumer Policy

Recommended downstream behavior:

```text
1. Prefer raw-text redaction before tokenization when possible.
2. For output redaction, reconstruct text and apply sidecar byte offsets.
3. For training loss masking, map protected byte spans to all overlapping
   model tokens and conservatively over-mask boundary tokens.
4. Do not assume exact token-index span boundaries unless using a pre-split
   variant.
```

## Evidence

Detector adversarial battery:

| Cases | Expected spans | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: | ---: |
| 61 | 62 | 1.000000 | 1.000000 | 1.000000 |

Pilot route density on full v1.8 train/valid/test:

| Metric | Value |
| --- | ---: |
| lines | 19992 |
| raw bytes | 28445141 |
| protected spans | 95162 |
| protected bytes/raw byte | 0.016414 |
| protected line share | 0.743047 |

Pilot conservative masking simulation:

| Metric | Value |
| --- | ---: |
| extra mask bytes/raw byte | 0.004100 |
| extra/protected byte | 0.249802 |
| edge-aligned span rate | 0.073916 |
| crossing span rate | 0.926084 |
| max extra bytes/span | 9 |

Real-mix confirmation sample:

```text
sample: artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
sources: TRT news + academic + TTK JSONL text fields
```

| Metric | Value |
| --- | ---: |
| lines | 40388 |
| raw bytes | 44351801 |
| protected spans | 149999 |
| protected bytes/raw byte | 0.015398 |
| extra mask bytes/raw byte | 0.003983 |
| extra/protected byte | 0.258681 |
| edge-aligned span rate | 0.077861 |
| crossing span rate | 0.922139 |
| max extra bytes/span | 9 |

Interpretation:

```text
passthrough is not token-boundary aligned
conservative masking cost is low on both pilot and real-mix samples
global pre-split is not justified by masking/redaction cost alone
```

Real-mix token-pressure confirmation:

```text
report: artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
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
real-mix confirms the global pre-split tax; route-selective alignment should be
tested before any future global pre-split.
```

## Main Driver

Most conservative over-mask cost comes from `numeric_like`.

Real-mix extra-mask contribution:

| Route | Spans | Extra bytes | Extra/protected byte |
| --- | ---: | ---: | ---: |
| numeric_like | 127588 | 160582 | 0.369251 |
| file_like | 10309 | 9588 | 0.068213 |
| apostrophe_surface | 7579 | 6477 | 0.092804 |
| non_turkish_latin_word | 3228 | 2395 | 0.079210 |
| percent_encoded | 171 | 278 | 0.541910 |

If a future consumer requires stricter alignment, test route-selective
alignment first, especially for `numeric_like`, before global pre-splitting.

## Rejected Default

Do not use global pre-split as the v2.1 default.

Pre-split optional variant:

```text
sp64_protected_presplit_sidecar
```

It guarantees protected edge alignment:

| Metric | Valid | Test |
| --- | ---: | ---: |
| tokens/raw byte | 0.165261 | 0.165755 |
| exact roundtrip | 1994/1994 | 1998/1998 |
| protected edge alignment | 1.000000 | 1.000000 |

Tax versus passthrough:

```text
+0.006095 tokens/raw byte
about +3.8%
```

Use pre-split only if exact token-span protected operations become a committed
base-model requirement.

## Open Risks

Remaining risks:

```text
detector battery is synthetic and small
real-mix sample is stronger than pilot but not the full future pretraining mix
byte-sidecar consumers must implement byte-offset reconciliation correctly
constrained decoding / exact copy requirements would need a different contract
```

These risks do not block v2.1 baseline consolidation. They define when to
reopen the decision.

## Reopen Criteria

Reopen global or selective alignment only if one of these becomes true:

```text
LLM/SFT pipeline requires exact token-index protected spans
security policy forbids conservative boundary-token over-mask
constrained decoding or exact-copy logic must operate on protected token spans
real future pretraining mix shows materially higher extra mask bytes/raw byte
one protected route dominates enough to justify route-selective pre-splitting
```

## 20M BPB Row

The 20M tiny-LM BPB row for the selected contract is complete:

```text
report: artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
```

| Metric | Value |
| --- | ---: |
| steps | 6042 |
| approx bytes seen | 19998919 |
| final valid BPB | 1.935810 |
| test BPB | 1.947129 |
| valid bits/token | 12.1730 |
| test bits/token | 12.1955 |

Do not run pre-split 20M unless the alignment question is reopened.

## Regression Lock

Before handoff or any route/detector change, rerun:

```text
docs/v2_1_regression_checklist.md
```

Latest locked result:

| Check | Result |
| --- | ---: |
| targeted unit tests | 44 passed |
| detector battery | 61 cases, 62 expected spans, F1 1.000000 |
| valid roundtrip | 1994/1994 |
| test roundtrip | 1998/1998 |
| dry-run test tokens/raw byte | 0.159660 |

Important invariant:

```text
percent_encoded must remain in the v2.1 sidecar passthrough route lists.
```

## Required Handoff Artifacts

Primary docs:

```text
docs/v2_1_final_handoff_package.md
docs/v2_1_passthrough_sidecar_handoff_contract.md
docs/v2_1_passthrough_sidecar_runbook.md
docs/v2_1_regression_checklist.md
docs/v2_1_closure_gauntlet_findings.md
docs/advisor_feedback_v2_1_sidecar_contract_triage.md
```

Core reports:

```text
artifacts/v2_1_tiny_lm_passthrough_sidecar_dry_run.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test.md
artifacts/v2_1_sidecar_detector_adversarial_battery.md
artifacts/v2_1_sidecar_route_density_audit_train_valid_test.md
artifacts/v2_1_sidecar_operation_simulation_train_valid_test.md
artifacts/v2_1_real_mix_text_sample_materialization_60k.md
artifacts/v2_1_sidecar_operation_simulation_real_mix.md
artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
artifacts/v2_1_sidecar_detector_adversarial_battery_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test_regression.md
```

Private diagnostic sample:

```text
artifacts/private/v2_1_sidecar_operation_simulation_real_mix.samples.jsonl
```

## Final Recommendation

Freeze v2.1 around:

```text
sp64_protected_passthrough_sidecar
```

Do not spend more effort on global pre-split unless a downstream requirement
changes. Next work should either be packaging/regression for this baseline or
separate v2.2 research on morphology as a model-side or auxiliary signal.
