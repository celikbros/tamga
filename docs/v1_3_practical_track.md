# v1.3 Practical Technical Track

Status: approved direction  
Date: 2026-05-19  
Tokenizer behavior: low-risk protection and roundtrip hardening

## Decision

External human validation is valuable, but it is no longer the critical path for
v1.3.

The project can continue without waiting for a professor, student, or external
annotator. Human hidden eval remains a later validation path, not a blocker for
technical hardening.

## Why This Is Acceptable

The current project goal is still a research prototype, not a published
benchmark claim. We can improve the engineering and measurement base without
claiming independent human validation.

This means:

- We can keep developing the tokenizer research infrastructure.
- We can add public stress tests and smoke tests.
- We can strengthen Unicode, apostrophe, protection, and baseline comparison.
- We must not claim that the tokenizer has passed independent human evaluation.

## Updated v1.3 Priority

Instead of waiting on external reviewers, v1.3 should focus on public,
reproducible checks:

1. Public stress test set
2. Unicode and apostrophe smoke tests
3. Protected span integrity tests
4. Coverage telemetry by layer
5. Stronger baseline preparation

This keeps the project moving while preserving methodological honesty.

## What Remains Optional

The following remain useful but optional:

- human hidden eval
- professor/student review
- second annotator and inter-annotator agreement
- treebank or independent morphological reference integration

These should be tracked as external validation or methodological strengthening,
not as required work before the next technical step.

## Guardrails

Even without human hidden eval, the project should keep these guardrails:

- `tr_gold_expanded.tsv` must remain the frozen regression set.
- Challenge examples should not be chased one-by-one with broad rules.
- New tokenizer behavior should require positive and negative regression tests.
- No broad greedy short-suffix splitter.
- No global lowercase, casefold, or NFKC.
- No generic apostrophe rule for all languages.
- No Turkish morphology for all Latin/Turkic input.

## Next Technical Work

Recommended next sequence:

1. Add `data/eval/tr_stress_public.tsv`.
2. Include Unicode, apostrophe, protection, code/file, number/date, informal, and
   multilingual do-no-harm examples.
3. Add a script or report mode that measures protected span break rate.
4. Add coverage telemetry:
   - protected tokens
   - morphology-split tokens
   - fallback/unknown tokens
   - punctuation/number/file-like tokens
5. Prepare stronger baseline comparison notes:
   - SentencePiece BPE
   - SentencePiece Unigram
   - byte-level BPE
   - existing LLM tokenizer fertility checks

Current command:

```powershell
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_public_stress_report.md
python scripts/report_coverage.py data/eval/tr_gold_expanded.tsv --markdown-out artifacts/v1_3_coverage_expanded.md
python scripts/report_coverage.py data/eval/tr_stress_public.tsv --markdown-out artifacts/v1_3_coverage_stress.md
```

Current public-stress baseline:

```text
examples: 28
roundtrip_exact: 23/28
protected_spans_preserved: 23/23
```

URL protection is now covered by the public stress set. The remaining first
weak spots are Azerbaijani-specific letters and Turkic Cyrillic pass-through.
These are observations, not v1.x regression failures.

Current coverage telemetry:

```text
expanded regression:
  examples: 50
  tokens: 332
  suffix tokens: 163
  protected tokens: 2
  other tokens: 0

public stress:
  examples: 28
  tokens: 304
  suffix tokens: 43
  protected tokens: 17
  other tokens: 94
```

The high `other` count in the stress set is concentrated in Azerbaijani and
Kazakh/Kyrgyz/Tatar Cyrillic inputs. That is useful v2.0 routing/fallback
evidence, not a v1.x production failure.

## Documentation Rule

Until external human validation exists, project claims should use this wording:

```text
The tokenizer passes the project-owned frozen regression set and has public
challenge/stress analysis infrastructure. Independent human hidden evaluation is
planned but not yet completed.
```
