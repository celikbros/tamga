# v1.3 Closing Report

Status: closed technical hardening phase
Date: 2026-05-29
Repository: `https://github.com/alicelik77/tr-centric-tokenizer`

## Summary

v1.3 moved the project from "selected Turkish morphology examples work" toward
a more robust research prototype with public stress checks, coverage telemetry,
and multilingual do-no-harm guards.

This phase does not claim production readiness or independent human validation.
It does show that the current deterministic core remains stable while the
surface-preservation layer is much stronger.

## What Changed

The main v1.3 hardening work focused on low-risk protection and roundtrip
behavior:

- URL spans are preserved before morphology.
- Smart double quotes round-trip without ASCII conversion.
- Code-call spacing is preserved for code-like tokens such as
  `kullanici_adi(ad)` and `ad.strip()`.
- Uzbek apostrophe-like lexical spans such as `Oʻzbekiston`, `gʻisht`, and
  `sanʼat` are not routed through Turkish apostrophe suffix splitting.
- Azerbaijani `ə/Ə`-bearing Latin words are preserved as surface spans.
- Turkic Cyrillic words are preserved as word-level spans instead of
  character-level pieces.
- Dash width is preserved in public stress examples.
- Public stress reporting and coverage telemetry were added.

## Current Metrics

### Frozen Regression

Command:

```powershell
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
```

Result:

```text
examples:    50
exact_match: 50/50
precision:   1.0000
recall:      1.0000
f1:          1.0000
```

Interpretation: the project-owned frozen regression set remains intact.

### Challenge Set

Command:

```powershell
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
```

Result:

```text
examples:    108
exact_match: 40/108
precision:   0.8600
recall:      0.7807
f1:          0.8184
```

Interpretation: challenge remains a dev/error-analysis set. We did not chase
challenge examples with broad morphology rules during v1.3.

### Public Stress

Command:

```powershell
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_public_stress_report.md
```

Result:

```text
examples: 28
roundtrip_exact: 28/28
protected_spans_preserved: 23/23
```

Interpretation: the public smoke/stress examples now preserve surface text and
protected spans. This is a do-no-harm signal, not a multilingual morphology
claim.

### Coverage Telemetry

Command:

```powershell
python scripts/report_coverage.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_coverage_stress.md
```

Result:

```text
examples: 28
tokens: 223
suffix tokens: 43
protected tokens: 17
other tokens: 0
```

Interpretation: public stress inputs no longer fall into unclassified `other`
tokens. This reflects pass-through/protection hardening.

## What This Does Not Mean

v1.3 does not mean:

- the tokenizer is production-ready
- multilingual tokenization is solved
- Turkic morphology is implemented
- challenge set quality is satisfactory
- independent human hidden eval has been completed
- toy BPE comparison is enough for academic claims

The correct claim is:

```text
The tokenizer passes the project-owned frozen regression set and the public
stress smoke set. Independent human hidden evaluation and stronger baseline
comparison remain future validation work.
```

## Remaining Known Risks

- Challenge exact match is still low: `40/108`.
- Ambiguity and negative-word policies remain conservative and intentionally
  unresolved.
- Surface-stem segmentation is useful for roundtrip tokenization, but it is not
  lemma-level morphological analysis.
- Informal Turkish coverage is still hand-curated.
- Azerbaijani, Uzbek, Kazakh, Kyrgyz, and Tatar support is currently
  pass-through/protection only, not language-specific morphology.
- Strong baselines such as SentencePiece BPE/Unigram and existing LLM
  tokenizers are not yet integrated.

## v1.4 Entry Criteria

v1.4 should begin only under these constraints:

- `tr_gold_expanded.tsv` must stay `50/50`.
- Public stress should stay `28/28` roundtrip unless a documented policy change
  intentionally changes expected output.
- No broad greedy short-suffix expansion.
- No generic apostrophe rule for all languages.
- No global lowercase, casefold, or destructive Unicode normalization.
- New behavior must include positive and negative regression tests.

## Recommended v1.4 Direction

The next step should not be broad morphology expansion. The recommended path is:

1. Use `docs/v1_4_decision_framework.md` as the decision gate.
2. Re-run challenge mismatch analysis.
3. Select only low-risk safe-rule candidates with explicit revert criteria.
4. Keep hidden eval and independent morphological reference integration as
   external validation tracks.

## Final v1.3 Position

v1.3 is closed as a practical hardening phase.

The tokenizer is now better described as:

```text
A Turkish-centered deterministic morphology tokenizer prototype with stable
project-owned regression, public stress/coverage telemetry, and multilingual
surface-preservation guards.
```

The main research question remains open:

```text
Can a deterministic Turkish morphology layer plus MorphBPE fallback preserve
Turkish morphological boundaries better than standard subword tokenizers at a
similar token budget?
```

v1.3 gives a cleaner engineering base for answering that question, but not the
final answer.
