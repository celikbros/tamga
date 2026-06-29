# v2.1 Pre-Split Protected Sidecar Findings

Date: 2026-06-12

## Context

Fable5 accepted the edge-safe sidecar safety result, but warned that replacing
every edge-crossing SP piece with UTF-8 byte fallback pays an avoidable
implementation tax.

We implemented the proposed encode-only pre-split sidecar:

```text
normal text: SP64
protected spans: sidecar/logical bookkeeping
span edges: split before SP encoding, so pieces cannot cross protected edges
segment-start dummy-prefix: rewritten to non-start piece when possible,
                            otherwise UTF-8 byte fallback for that segment piece
SP <unk>: UTF-8 byte fallback
route-token vocab: none
```

Current candidate:

```text
sp64_protected_presplit_sidecar
```

Config:

```text
configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml
```

## Encode-Only Result

| Candidate | Vocab | Valid tokens/raw byte | Test tokens/raw byte | Valid fallback token rate | Test fallback token rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| bare SP64 | 64000 | 0.159020 | 0.159620 | n/a | n/a |
| inline all-route passthrough, route-token vocab | 64630 | 0.159027 | 0.159668 | n/a | n/a |
| passthrough sidecar, byte-fallback vocab | 64256 | 0.159026 | 0.159660 | 0.000062 | 0.000324 |
| numeric-SP floor | 64630 | 0.163567 | 0.164497 | 0.000447 | 0.000780 |
| edge-safe sidecar | 64630 | 0.169341 | 0.169791 | 0.080549 | 0.078995 |
| pre-split sidecar | 64256 | 0.165261 | 0.165755 | 0.021135 | 0.021304 |

Reports:

```text
artifacts/v2_1_tiny_lm_presplit_sidecar_dry_run.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_dry_run.md
```

## Safety Checks

| Candidate | Check | Valid | Test |
| --- | --- | ---: | ---: |
| passthrough sidecar | exact roundtrip | 1994/1994 | 1998/1998 |
| passthrough sidecar | protected edge alignment | 0.453798 | 0.463721 |
| pre-split sidecar | exact roundtrip | 1994/1994 | 1998/1998 |
| pre-split sidecar | protected edge alignment | 1.000000 | 1.000000 |
| pre-split sidecar | crossing pieces | 0 | 0 |

Reports:

```text
artifacts/v2_1_passthrough_sidecar_roundtrip_valid.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test.md
artifacts/v2_1_presplit_sidecar_roundtrip_valid.md
artifacts/v2_1_presplit_sidecar_roundtrip_test.md
artifacts/v2_1_protected_boundary_alignment_presplit_sidecar_audit.md
```

## Detector Battery

Fable5 warned that pre-split couples model-token boundaries to detector
decisions. We therefore added a generated adversarial protected-span detector
battery before any 20M training row.

Initial failure:

```text
percent-encoded suffix spans such as `%20'si` were detected as `20`
```

Fix:

```text
add a narrow percent-encoded protected route for URL-encoding-like spans while
keeping `%25'lik` as `%` + `25` + suffix
```

Current battery result:

| Cases | Expected spans | Detected spans | TP | FP | FN | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 61 | 62 | 62 | 62 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |

Category coverage:

```text
protected suffix attachment
percent-encoded suffix
numeric suffix attachment
span-adjacent punctuation
line-edge spans
nested/comparator spans
```

Report:

```text
artifacts/v2_1_sidecar_detector_adversarial_battery.md
```

## Vocabulary Accounting

The pre-split and passthrough sidecar candidates use:

```text
64000 SP pieces + 256 UTF-8 byte fallback ids = 64256 vocab
```

They intentionally do not reserve the 630 finite route-token pieces used by the
older `finite_protected_*` family.

This means the clean comparator for pre-split is:

```text
sp64_protected_passthrough_sidecar
```

not the older 64630-vocab numeric-SP floor.

## Fallback Decomposition

Dry-run `fallback source rate` is a token-rate metric. The contract-relevant
metric is fallback byte coverage.

The dry-run token pressure includes one EOS token per line. The fallback
decomposition and roundtrip reports do not include EOS. This explains the
apparent test discrepancy:

```text
461129 dry-run tokens - 459131 no-EOS tokens = 1998 test lines
```

| Split | Tokens/raw byte | Fallback bytes | Fallback token rate | Fallback byte coverage |
| --- | ---: | ---: | ---: | ---: |
| valid | 0.164560 | 9931 | 0.021225 | 0.003493 |
| test | 0.165037 | 9824 | 0.021397 | 0.003531 |

Reason breakdown:

| Split | `dummy_prefix_missing_piece` bytes | `sp_unk` bytes |
| --- | ---: | ---: |
| valid | 9903 | 28 |
| test | 9680 | 144 |

Report:

```text
artifacts/v2_1_presplit_sidecar_fallback_decomposition_valid_test.md
```

## Current Reading

Fable5's implementation-tax critique was correct:

```text
edge-safe sidecar test tokens/raw byte: 0.169791
pre-split sidecar test tokens/raw byte: 0.165755
```

The pre-split sidecar preserves exact roundtrip and protected edge alignment
while recovering most of the edge-safe byte-fallback tax.

The measured alignment tax against the same 64256-vocab passthrough comparator
is:

```text
pre-split test tokens/raw byte: 0.165755
passthrough test tokens/raw byte: 0.159660
delta: +0.006095, about +3.8%
```

This is now a consumer/contract decision, not primarily a BPB decision:

```text
If downstream users need token-boundary-aligned protected spans, pre-split is
the candidate.

If logical byte spans with possible one-token edge fuzz are sufficient,
passthrough sidecar dominates on token pressure.
```

## Decision

Advisor feedback split on A vs B, but the stronger v2.1 baseline argument is
for:

```text
sp64_protected_passthrough_sidecar
```

Rationale:

```text
lossless exact roundtrip
near-SP64 token pressure
no permanent +3.8% token tax
model-token stream remains decoupled from detector changes
PII/redaction can use byte-sidecar plus conservative boundary-token over-masking
```

Do not run the pre-split 20M BPB check now.

Keep pre-split as an optional route for consumers that prove they need
token-boundary-aligned protected spans, especially exact-copy or constrained
decoding over protected entities.

Next consolidation gate:

```text
passthrough sidecar v2.1 handoff contract
optional 20M fixed-byte row for passthrough sidecar if an LM-loss baseline is needed
selective pre-split only if exact-copy/constrained decoding becomes a committed
base-model requirement
```

Advisor triage:

```text
docs/advisor_feedback_v2_1_sidecar_contract_triage.md
```

## Next Long Command

The pre-split train tokens/raw byte estimate is:

```text
0.161108
```

Approximate 20M fixed-byte steps:

```text
6294
```

But this run should wait until the detector battery and consumer alignment
decision are complete.
