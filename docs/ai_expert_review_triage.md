# AI Expert Review Triage

Status: advisory synthesis  
Date: 2026-05-19  
Tokenizer behavior: not changed

## Purpose

This document summarizes the AI expert-style reviews collected for the
Turkish-centered tokenizer project. These reviews are useful advisory signals,
but they are not a substitute for human linguistic review, hidden evaluation, or
real baseline experiments.

The goal is to separate:

- what should become an immediate v1.x guardrail
- what should be deferred to v1.5/v2.0
- what should remain an open research question
- what should be validated by human reviewers

## Review Sources

The user collected Turkish-focused and multilingual/Turkic-focused AI review
comments from several reviewer personas:

- Turkish-focused: Grok42TR, Opus47TR, Grok43TR, Gemini31TR, CGPT
- Multilingual/Turkic-focused: Grok42ML, Opus47ML, Grok43ML, Gemini31ML,
  CGPTML

These names identify advisory sources in this project discussion. They should
not be treated as independent human expert evidence.

## High-Confidence Consensus

Across the reviews, the strongest shared signals are:

1. Hidden eval should happen before adding new tokenizer rules.
2. Short suffixes must not be added to a broad greedy splitter.
3. False-positive splits are more dangerous than missed splits.
4. Code, file, URL, number, date, and protected spans must be protected before
   morphology.
5. Turkish apostrophe splitting is useful, but must not become a generic
   apostrophe rule.
6. v1.x should not claim general multilingual or all-Turkic support.
7. Non-Turkish input should follow a do-no-harm policy in v1.x.
8. No global lowercase, casefold, or NFKC normalization should be used.
9. Dotted/dotless `i` behavior must be explicit and tested.
10. Byte fallback is a lossless safety net, not a quality strategy.
11. Stronger baselines will be needed beyond the current toy BPE.

## Accepted Now

These points should affect project policy immediately, without changing
tokenizer behavior:

- Keep `tr_gold_expanded.tsv` as the frozen regression set.
- Treat `tr_challenge.tsv` as a dev/error-analysis set, not a target to force
  to 100%.
- Continue the hidden eval track before new rules.
- Keep human hidden eval and aggregate-only reporting as the critical path.
- Document that v1.x is Turkish-centered, not multilingual production.
- Treat multilingual smoke results as observations, not regression failures.
- Update architecture docs so cross-language protection and language/script
  routing are first-class v2.0 decisions.

## Accepted v1.x Guardrails

These are constraints for future v1.x work:

- Do not add broad suffix rules to improve challenge score.
- Do not add language detection or Turkic morphology in v1.x.
- Do not normalize informal Turkish to standard Turkish in the tokenizer.
- Do not replace the surface-stem policy before hidden eval.
- Do not apply Turkish morphology to all Latin-script input.
- Do not use global `lower()`, `casefold()`, or NFKC.
- Do not let code/file/URL spans enter morphology.
- Do not treat every apostrophe-like character as Turkish suffix separation.

## Deferred To v1.5/v2.0

The following are important but should not block the immediate hidden eval
process:

- SentencePiece BPE/Unigram and stronger production-like baselines.
- Downstream experiments such as language-model validation loss, POS, or NER.
- Coverage telemetry by layer: protection, morphology, fallback, byte fallback.
- Protected span integrity metrics.
- Formal suffix grammar or FST-backed morphology.
- Syncope/allomorph policy for forms like `akıl -> akl`, `burun -> burn`,
  `ağız -> ağz`, `şehir -> şehr`.
- Lemma alias or metadata channel for surface stems.
- Optional informal normalization or analysis channel.
- Language/script router with confidence thresholds.
- Per-language apostrophe policy matrix.
- Per-language byte fallback rate targets.
- Vocabulary allocation across Turkish, Turkic languages, code, English, and
  fallback space.

## Not Accepted For v1.x

These recommendations are not accepted as immediate v1.x changes:

- Replacing surface-stem tokenization with lemma-plus-alternation tokens.
- Normalizing `Gelicem` to `geleceğim` as the default tokenizer behavior.
- Treating 500 or 5000 hidden examples as a blocker before the first pilot.
- Expanding to full Turkic morphology before Turkish hidden eval.
- Making multilingual smoke tests pass as regression requirements.
- Using challenge-set exact match as the main optimization target.

These ideas may still be valuable research directions later.

## Key Disagreements To Preserve

### Surface Stem vs Lemma

Some reviewers prefer lemma-level representation to avoid `kitap` and `kitab`
as separate surface stems. Others argue that tokenizers must preserve surface
form for offset and detokenization safety.

Current v1.x policy:

```text
Tokenizer output is surface-preserving segmentation, not lemma analysis.
```

Future v2.0 option:

```text
tokens:   ▁kitab +ım +dan
metadata: lemma=kitap, stem_surface=kitab
```

### Informal Normalization

Some reviewers want informal forms normalized to standard Turkish to reduce
vocabulary fragmentation. Others warn that this loses style, offsets, and
surface evidence.

Current v1.x policy:

```text
Gelicem -> ▁Gel +icem
```

Future v2.0 option:

```text
raw:        gelicem
tokens:     ▁gel +icem
analysis:   gel + ecek + im
normalized: geleceğim
```

### Hidden Eval Size

Some reviewers ask for hundreds or thousands of hidden examples immediately.
That is methodologically desirable, but not realistic as a first step.

Current plan:

- Start with a 40-example hidden pilot.
- Keep it private and aggregate-only.
- Grow toward 80-100 examples next.
- Later add larger independent and possibly treebank-derived references.

## Multilingual Strategy Adjustments

The multilingual/Turkic reviews converge on one architectural correction:

```text
Do not run Turkish morphology first and ask later whether the input was Turkish.
```

The safer v2.0 direction is:

1. Preserve raw input and offsets.
2. Apply only minimal reversible cleanup.
3. Protect code, file, URL, number, date, and similar spans before morphology.
4. Route remaining spans by script/language confidence.
5. Run Turkish morphology only on high-confidence Turkish spans.
6. Run Turkic-specific morphology only when a supported language/script cue is
   explicit enough.
7. Use MorphBPE or ordinary subword fallback for uncertain spans.
8. Use byte fallback only as lossless last resort.

Unknown or ambiguous Latin/Turkic input should not default to Turkish
morphology.

## Human Validation Needed

These points should be asked of human reviewers or labelers:

- Is the surface-stem policy acceptable for tokenizer output if lemma metadata is
  separated?
- Which ambiguity classes should be `MUST_NOT_SPLIT`, `MUST_SPLIT`, or
  `AMBIGUOUS`?
- Which apostrophe forms should be treated as Turkish suffix separators?
- Should hidden eval include a small amount of code-mixed and loanword Turkish?
- Should informal forms be surface-preserving only, or should optional
  normalization metadata be added later?
- Which Turkic languages should be first-class in v2.0, and which should remain
  pass-through/fallback?

## Operational Decision

The reviews do not require an immediate tokenizer rewrite.

They strengthen the current plan:

```text
freeze behavior
finish hidden eval setup
collect human feedback
then decide the next low-risk rule batch
```

The next critical-path action remains:

```text
find human labeler/reviewer -> run calibration -> collect 40 hidden examples
```

