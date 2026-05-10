# Multilingual Reviewer Packet

Status: reviewer handoff  
Date: 2026-05-10  
Scope: multilingual/Turkic architecture review, not tokenizer implementation

## Purpose

`tr-centric-tokenizer` is currently a Turkish-centered morphology-aware tokenizer
prototype. The long-term goal is multilingual-aware and Turkic-aware, but v1.x
does not yet implement a general multilingual tokenizer.

This review asks language/Turkic/NLP reviewers to identify architectural risks
before v2.0 vocabulary allocation, normalization policy, and fallback behavior
are frozen.

## Reviewer Role

The reviewer is not asked to implement code.

The reviewer is asked to comment on:

- whether the v2.0 layering direction is reasonable
- language/script-specific risks
- apostrophe and punctuation conventions
- normalization risks
- characters or scripts that must not fall into poor fallback behavior
- examples that should later become multilingual smoke tests

## Files To Read

Recommended short set:

```text
docs/multilingual_strategy.md
docs/multilingual_observations.md
docs/multilingual_reviewer_response_form.md
```

Optional context:

```text
README.md
docs/advisor_brief.md
```

The reviewer does not need to read tokenizer implementation files.

## Important Framing

This is not a regression evaluation.

Current multilingual failures are planning signals, not bugs to fix immediately.
v1.x remains Turkish-centered. v2.0 may introduce script-aware and
language-aware layers after the architecture is reviewed.

## Main Questions

1. Is the proposed v2.0 layering direction reasonable?
2. Which decisions would become expensive to change later?
3. Which Unicode/script/normalization issues matter for your language or area?
4. Should Turkish-specific apostrophe behavior be kept strictly Turkish-scoped?
5. What examples should we use later for a multilingual smoke set?

## Desired Output

Please fill:

```text
docs/multilingual_reviewer_response_form.md
```

or reply in free text using the same headings.

The response may include examples. These examples are not hidden eval rows; they
may later become public smoke-test candidates if the reviewer agrees.

## What Not To Do

- Do not try to fix the tokenizer in v1.x.
- Do not treat current multilingual failures as regressions.
- Do not send private or licensed corpus text unless redistribution is allowed.
- Do not assume Turkish morphology rules apply to all Turkic languages.

## Current Candidate v2.0 Layering

Subject to revision:

1. Unicode normalization + script-aware pretokenizer
2. Cross-language protection for code, file paths, URLs, numbers, and dates
3. Turkish morphology layer
4. Turkic-aware morphology layer when script/language cues support it
5. MorphBPE fallback, respecting known morphology boundaries when available
6. Byte fallback as last resort

The most important design principle is:

```text
layering first, vocabulary later
```

Vocabulary allocation should not be frozen before script handling, normalization,
cross-language protection, and byte fallback policy are clear.
