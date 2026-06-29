# v2.0 Roundtrip And Wrapper Tax Findings

Date: 2026-06-10

## Purpose

This audit follows the lambda 0 advisor review. It checks two blockers:

```text
1. exact roundtrip for the protected / boundary-biased runtime paths
2. wrapper tax on clean lines without protected routes
```

Script:

```text
scripts/audit_v2_roundtrip_wrapper_tax.py
```

Main report:

```text
artifacts/v2_0_roundtrip_wrapper_tax_audit_valid.md
```

Route-only repair report:

```text
artifacts/v2_0_roundtrip_wrapper_tax_audit_valid_after_route_only.md
artifacts/v2_0_roundtrip_wrapper_tax_audit_valid_after_route_only_byte_fallback.md
artifacts/v2_0_roundtrip_wrapper_tax_audit_test_after_route_only_byte_fallback.md
```

Private samples:

```text
artifacts/private/v2_0_roundtrip_wrapper_tax_audit_valid.samples.jsonl
```

## Valid Split Result

| Tokenizer | Lines | Exact | Exact rate | Tokens/raw byte |
| --- | ---: | ---: | ---: | ---: |
| SP64 bare | 1994 | 1985 | 0.995486 | 0.158319 |
| finite protected numeric-SP floor | 1994 | 17 | 0.008526 | 0.171202 |
| boundary-biased lambda 0 | 1994 | 0 | 0.000000 | 0.162451 |
| boundary-biased lambda 4 | 1994 | 0 | 0.000000 | 0.163313 |

The SP64 failures are a small number of corpus/line-edge cases. The custom
runtime paths fail systematically.

## Route-Only Protected Wrapper Repair

The root cause was segment-wise SP encoding:

```text
normal text was being split at whitespace / punctuation / apostrophe /
morphology hard boundaries, but the emitted token stream did not preserve SP
segment boundaries. On decode, internal SentencePiece dummy-prefix pieces
became fake spaces.
```

The repair changes the finite protected runtime path when
`insert_soft_markers=false`:

```text
normal text is kept as raw SP chunks
the wrapper splits only around non-numeric finite protected spans
numeric-like protected spans remain in the SP passthrough chunk
```

This leaves marker-training experiments unchanged.

New valid result:

| Tokenizer | Lines | Exact | Exact rate | Tokens/raw byte |
| --- | ---: | ---: | ---: | ---: |
| SP64 bare | 1994 | 1985 | 0.995486 | 0.158319 |
| finite protected numeric-SP floor | 1994 | 1994 | 1.000000 | 0.162866 |
| boundary-biased lambda 0 | 1994 | 0 | 0.000000 | 0.162451 |
| boundary-biased lambda 4 | 1994 | 0 | 0.000000 | 0.163313 |

New test result:

| Tokenizer | Lines | Exact | Exact rate | Tokens/raw byte |
| --- | ---: | ---: | ---: | ---: |
| SP64 bare | 1998 | 1989 | 0.995495 | 0.158902 |
| finite protected numeric-SP floor | 1998 | 1998 | 1.000000 | 0.163779 |
| boundary-biased lambda 0 | 1998 | 0 | 0.000000 | 0.163120 |
| boundary-biased lambda 4 | 1998 | 0 | 0.000000 | 0.163968 |

Clean-line wrapper tax after repair:

| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta |
| --- | ---: | ---: | ---: | ---: |
| finite protected numeric-SP floor valid | 484 | 164.2955 | 164.3017 | +0.0062 |
| finite protected numeric-SP floor test | 526 | 158.6331 | 158.6331 | 0.0000 |

Interpretation:

```text
the protected floor wrapper tax is fixed on clean no-protected lines
the valid split has only +3 net tokens across 484 clean lines, caused by
UTF-8 fallback for rare unknown characters
the repaired finite protected floor is exact-roundtrip on valid and test
bare SP64 still fails on rare unknown characters because it has no byte fallback
```

## Failure Shape

Most failures are whitespace / punctuation / apostrophe reconstruction errors.

Examples from private samples show behavior like:

```text
TURKIYE'NIN -> TURKIYE ' NIN
Yonetisim - Uluslarotesi -> Yonetisim- Uluslarotesi
```

This means the runtime paths are not preserving raw text. The BPB rows for
lambda 0 / lambda 4 remain diagnostic only.

## Clean-Line Wrapper Tax

Only lines without protected routes were included.

| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta |
| --- | ---: | ---: | ---: | ---: |
| finite protected numeric-SP floor | 484 | 164.2955 | 171.9669 | +7.6715 |
| boundary-biased lambda 0 | 484 | 164.2955 | 163.4380 | -0.8574 |
| boundary-biased lambda 4 | 484 | 164.2955 | 164.4690 | +0.1736 |

This confirms the advisor warning:

```text
the protected wrapper adds avoidable token pressure even on clean lines
```

The likely cause is segment-wise encoding / dummy-prefix handling / blocked
cross-segment merges around whitespace, punctuation, and apostrophes.

## Failed Local Fix Attempt

We tested a local change that kept whitespace inside the SP segment instead of
flushing and dropping it.

Smoke report:

```text
artifacts/v2_0_roundtrip_wrapper_tax_audit_smoke_after_whitespace_segment.md
```

Result:

```text
roundtrip still failed
token pressure became much worse
```

The change was reverted.

Interpretation:

```text
this is not a safe one-line fix
```

## Decision

Do not run longer BPB for the runtime boundary-biased decoder.

Do not promote lambda 4.

The runtime boundary-biased path should stay diagnostic unless we redesign the
lossless wrapper/decoder.

The repaired finite protected numeric-SP floor can return as the active
protected null baseline, subject to the remaining normalization/unknown
character contract:

```text
The finite wrapper now supplies UTF-8 fallback for rare unknown normal-text
characters. Before LLM handoff, still compare against a stock byte-fallback SP
baseline or document why the finite fallback is the chosen contract.
```

Preferred next technical direction:

```text
1. keep runtime boundary-biased decoder demoted
2. use the route-only finite protected floor as the repaired baseline
3. solve the remaining SP unknown-character contract
4. then run Rung-0 morphology-compliant-path diagnostics
```
