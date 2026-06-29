# v2.0 SP64 Morph-Compliant Path Audit Findings

Date: 2026-06-10

## Purpose

This is the Fable5-style Rung-0 diagnostic.

Question:

```text
Does the existing SP64 vocabulary already contain paths that avoid
high-confidence custom morphology boundaries?
```

If yes and those paths are cheap, a light decode/objective nudge may be enough.
If yes but expensive, morphology-aware training must be soft and selective.
If no, the vocabulary itself must be reshaped.

Script:

```text
scripts/audit_v2_sp64_morph_compliant_paths.py
```

Reports:

```text
artifacts/v2_0_sp64_morph_compliant_path_audit_challenge.md
artifacts/v2_0_sp64_morph_compliant_path_audit_challenge_valid200.md
```

## Challenge Result

Input:

```text
data/eval/tr_challenge.tsv
```

| Metric | Value |
| --- | ---: |
| soft-boundary segments | 170 |
| unconstrained crosses >=1 boundary | 127 |
| crossing share | 0.747059 |
| avg token delta constrained-unconstrained | 1.0647 |
| median token delta | 1.0000 |
| avg score delta unconstrained-constrained | 7.0634 |
| median score delta | 5.3881 |
| avg score delta on crossed segments | 9.4549 |

## Challenge + Natural Valid Sample

Input:

```text
data/eval/tr_challenge.tsv
valid split first 200 lines
```

| Metric | Value |
| --- | ---: |
| soft-boundary segments | 8787 |
| unconstrained crosses >=1 boundary | 8156 |
| crossing share | 0.928189 |
| avg token delta constrained-unconstrained | 1.5614 |
| median token delta | 1.0000 |
| avg score delta unconstrained-constrained | 11.9824 |
| median score delta | 10.6109 |
| avg score delta on crossed segments | 12.9094 |

## Interpretation

The existing SP64 vocabulary usually has a morphology-compliant path, because
character/short-piece fallback paths exist. But those paths are often
substantially worse than the unconstrained SP path:

```text
many common inflected words are single or short SP pieces
hard no-cross morphology would add about 1-2 tokens per affected segment
large score deltas appear for common words and uppercase/domain terms
```

This means:

```text
hard morphology constraints are too expensive
runtime hard-constrained decode is not the right production shape
boundary signals should be soft, partial, and training-time
```

## Decision

Do not build a hard constrained decoder.

Do not return to marker-dose tuning or broad UDS.

The next best experiment is a stock SentencePiece partial-boundary prior:

```text
insert morphology pretokenization delimiters in only a fraction of training
examples
rho sweep: 0.0, 0.05, 0.10, 0.25, 0.50
inference text remains delimiter-free
compare against repaired finite protected numeric-SP floor
```

Rationale:

```text
The Rung-0 audit says the vocabulary can often represent compliant paths, but
full compliance is too costly. A partial training prior is a better first
mechanism than a custom hard objective.
```
