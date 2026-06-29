# Advisor Feedback Triage: v2.1 Pre-Split Sidecar

Date: 2026-06-13

## Fable5 Main Points

Fable5 accepted the pre-split encode-only success but warned against running
20M immediately.

The useful points:

```text
1. Explain the vocab change.
2. Reconcile dry-run token pressure vs no-EOS fallback decomposition.
3. Compare pre-split against a same-vocab passthrough sidecar, not the old
   64630 numeric-SP floor.
4. Run detector adversarial battery before any pre-split training.
5. Decide whether consumers actually need token-boundary alignment.
```

## Checks We Ran

### Vocab accounting

Confirmed:

```text
passthrough sidecar vocab: 64256 = 64000 SP + 256 byte fallback
pre-split sidecar vocab: 64256 = 64000 SP + 256 byte fallback
```

Both have:

```text
route-token vocab: none
```

### Same-vocab passthrough comparator

| Candidate | Vocab | Valid tokens/raw byte | Test tokens/raw byte | Exact roundtrip |
| --- | ---: | ---: | ---: | --- |
| passthrough sidecar | 64256 | 0.159026 | 0.159660 | valid/test 100% |
| pre-split sidecar | 64256 | 0.165261 | 0.165755 | valid/test 100% |

Alignment:

```text
passthrough sidecar: not edge-aligned
pre-split sidecar: edge-aligned 1.000000
```

Measured alignment tax:

```text
test tokens/raw byte delta: +0.006095
relative: about +3.8%
```

### EOS reconciliation

The pre-split dry-run includes per-line EOS tokens; fallback decomposition does
not.

```text
test dry-run tokens: 461129
test no-EOS tokens: 459131
difference: 1998 test lines
```

So the two token-pressure numbers differ only by EOS accounting.

## Decision

Do not run the pre-split 20M row yet.

The next decision is semantic:

```text
passthrough sidecar:
  cheaper, exact roundtrip, detector metadata can be patched later,
  but protected span edges are not guaranteed token-boundary aligned

pre-split sidecar:
  exact roundtrip and token-boundary-aligned spans,
  but costs about +3.8% tokens/raw byte and couples model tokens to detector
  decisions
```

Run detector adversarial battery before any pre-split training.

Then ask the LLM/downstream consumer whether token-boundary-aligned protected
spans are required for copy, PII redaction, masking, or constrained decoding.

## Detector Battery Result

We added and ran a generated adversarial detector battery before any 20M
pre-split training row.

Initial issue found:

```text
percent-encoded suffix spans such as `%20'si`, `%3A'de`, `%C3%BC'yi`
were detected without the leading `%`
```

Patch:

```text
added a narrow percent-encoded protected route
kept `%25'lik` as percent-number text, not a protected URL-encoding span
```

Current result:

| Cases | Expected spans | Detected spans | TP | FP | FN | Precision | Recall | F1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 61 | 62 | 62 | 62 | 0 | 0 | 1.000000 | 1.000000 | 1.000000 |

Report:

```text
artifacts/v2_1_sidecar_detector_adversarial_battery.md
```

Updated reading:

```text
pre-split is no longer blocked by the first detector battery
pre-split is still blocked by the semantic contract decision
```
