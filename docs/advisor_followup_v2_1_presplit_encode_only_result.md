# Advisor Follow-Up: v2.1 Pre-Split Sidecar Encode-Only Result

Date: 2026-06-12

## Context

You warned that our edge-safe sidecar proved the protected-sidecar contract but
paid an avoidable implementation tax:

```text
edge-safe sidecar test tokens/raw byte: 0.169791
bare SP64 test tokens/raw byte: 0.159620
```

You suggested a pre-split encoder:

```text
run detector first
split at protected span edges
SP64-encode each segment carefully
avoid byte-fallbacking whole edge-crossing pieces
```

We implemented that encode-only experiment.

## Candidate

```text
sp64_protected_presplit_sidecar
```

Mechanism:

```text
normal text: SP64
protected spans: sidecar/logical bookkeeping
span edges: split before SP encoding
dummy-prefix at interior segment starts: rewritten to non-start piece if possible,
                                        otherwise byte fallback for that piece
SP <unk>: UTF-8 byte fallback
route-token vocab: none
```

## Encode-Only Result

| Candidate | Vocab | Valid tokens/raw byte | Test tokens/raw byte |
| --- | ---: | ---: | ---: |
| bare SP64 | 64000 | 0.159020 | 0.159620 |
| inline all-route passthrough, route-token vocab | 64630 | 0.159027 | 0.159668 |
| passthrough sidecar, byte-fallback vocab | 64256 | 0.159026 | 0.159660 |
| numeric-SP floor | 64630 | 0.163567 | 0.164497 |
| edge-safe sidecar | 64630 | 0.169341 | 0.169791 |
| pre-split sidecar | 64256 | 0.165261 | 0.165755 |

## Safety

| Check | Valid | Test |
| --- | ---: | ---: |
| exact roundtrip | 1994/1994 | 1998/1998 |
| protected edge alignment | 1.000000 | 1.000000 |
| crossing pieces | 0 | 0 |

## Fallback Decomposition

| Split | Tokens/raw byte | Fallback bytes | Fallback token rate | Fallback byte coverage |
| --- | ---: | ---: | ---: | ---: |
| valid | 0.164560 | 9931 | 0.021225 | 0.003493 |
| test | 0.165037 | 9824 | 0.021397 | 0.003531 |

Reason breakdown:

| Split | `dummy_prefix_missing_piece` bytes | `sp_unk` bytes |
| --- | ---: | ---: |
| valid | 9903 | 28 |
| test | 9680 | 144 |

Reports:

```text
docs/v2_1_presplit_sidecar_findings.md
artifacts/v2_1_tiny_lm_presplit_sidecar_dry_run.md
artifacts/v2_1_presplit_sidecar_roundtrip_valid.md
artifacts/v2_1_presplit_sidecar_roundtrip_test.md
artifacts/v2_1_protected_boundary_alignment_presplit_sidecar_audit.md
artifacts/v2_1_presplit_sidecar_fallback_decomposition_valid_test.md
artifacts/v2_1_sidecar_detector_adversarial_battery.md
```

## Current Reading

Your critique was correct. Pre-splitting recovers most of the edge-safe
byte-fallback tax:

```text
edge-safe test tokens/raw byte: 0.169791
pre-split test tokens/raw byte: 0.165755
```

The pre-split row still costs more than bare SP64 and inline all-route
passthrough, but those rows do not satisfy the protected-sidecar contract.

Update after same-vocab comparator:

```text
passthrough sidecar test tokens/raw byte: 0.159660
pre-split sidecar test tokens/raw byte: 0.165755
alignment tax: +0.006095, about +3.8%
```

The dry-run/no-EOS discrepancy is explained by EOS:

```text
461129 dry-run tokens - 459131 no-EOS tokens = 1998 test lines
```

## Detector Battery Update

We followed your warning that detector validation must precede any pre-split
training row.

The first generated adversarial battery initially found one real issue:

```text
percent-encoded suffix spans such as `%20'si` were detected as `20`
```

We added a narrow percent-encoded protected route and re-ran the battery:

| Cases | Expected spans | Detected spans | TP | FP | FN | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 61 | 62 | 62 | 62 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |

This does not decide passthrough vs pre-split. It only removes the first
detector-battery blocker for pre-split.

## Questions

Please be critical.

1. Is this pre-split sidecar now the correct v2.1 candidate for the 20M
   fixed-byte BPB run?

2. Is the fallback byte coverage acceptable for an experimental tokenizer
   baseline?

```text
valid: 0.3493%
test: 0.3531%
```

3. Would you require further encode-only optimization before the 20M run?

4. Should the detector adversarial battery be run before or after the 20M row?

Our current plan:

```text
Do not run 20M yet.
Run detector/protected adversarial stress first.
Ask the LLM/downstream consumer whether token-boundary-aligned protected spans
are required.
Then run 20M for the chosen artifact: passthrough sidecar or pre-split sidecar.
```

Please challenge this before we spend the training run.
