# Multilingual Strategy

Status: principles, subject to revision  
Date: 2026-05-10  
Tokenizer behavior: not changed

## Scope

`tr-centric-tokenizer` is Turkish-centered and multilingual-aware. The current
v1.x prototype is not a general multilingual tokenizer.

The long-term direction is:

```text
Turkish deterministic morphology
+ Turkic-aware extensions
+ cross-language protection
+ MorphBPE fallback
+ byte fallback
```

This document keeps architectural options open. It is not a final spec.

## v1.x Non-Goals

v1.x will not implement:

- language detection
- full script-aware fallback
- multilingual evaluation as a regression target
- Turkic Cyrillic morphology
- production vocabulary allocation
- final normalization policy for all supported languages

Non-Turkish failures observed in smoke tests are planning inputs for v2.0, not
v1.x regressions.

## Current Policy for Non-Turkish Input

The v1.x policy is conservative pass-through where possible.

This means:

- Do not intentionally optimize for non-Turkish languages in v1.x.
- Avoid accidental Turkish rule over-application to non-Turkish input.
- Document failures rather than chasing them with broad rules.
- Keep language-specific behavior layered so it can be replaced before v2.0
  vocabulary training.

French apostrophe over-application and Cyrillic character-level splitting are
known limitations, not immediate v1.4 targets.

## Code-Mixed and Loanwords

Code-mixed/loanword behavior is a Turkish false-positive split risk, not a
multilingual smoke category.

Example:

```text
API'den data aldım.
```

`API'den` is Turkish apostrophe behavior around a code token. `data -> da +ta`
is loanword over-splitting by Turkish rules. Track this under Turkish
`code_mixed`, `loanword_rare`, and false-positive split protection.

## Preserved Options for v2.0

Do not lock these decisions in v1.x:

- vocabulary allocation
- Unicode normalization beyond safe local needs
- NFC/NFD strategy
- casing and dotted/dotless `i` behavior across languages
- Turkish-specific apostrophe behavior as an all-Turkic rule
- script handling for Latin, Cyrillic, and mixed-script inputs
- byte fallback policy

The practical rule is:

```text
layering first, vocabulary later
```

If vocabulary is trained before script handling and fallback policy are decided,
early tokenizer decisions become expensive to change.

## Irreversibility Flags

These are the main future points where bad decisions can become costly:

| Decision | Risk |
| --- | --- |
| Vocabulary allocation before script policy | Turkic Cyrillic, Azerbaijani `ə`, and other characters may fall into poor fallback behavior. |
| Turkish apostrophe rule generalized to all Turkic languages | Other Turkic languages may use apostrophe differently. |
| Turkish-only normalization commitment | Choices around casing, dotted/dotless `i`, NFC/NFD, or diacritics may harm related languages. |
| Morphology layer tied directly to vocabulary | Changing deterministic rules later may require retraining the vocabulary. |

None of these should be locked in v1.x.

## Candidate Layering for v2.0

Subject to revision after prototyping:

1. Unicode normalization + script-aware pretokenizer
2. Cross-language protection for code, file paths, URLs, numbers, and dates
3. Turkish morphology layer
4. Turkic-aware morphology layer when script/language cues support it
5. MorphBPE fallback, respecting known morphology boundaries when available
6. Byte fallback as last resort

The cross-language protection layer must come before language-specific
morphology. A token like `README.md` should be protected before it reaches
Turkish or Turkic morphology.

## Near-Term Backlog

For v1.x:

- keep multilingual smoke observations factual
- do not make multilingual smoke a regression target
- consider a narrow future guard against accidental non-Turkish apostrophe
  over-application
- consider a future guard so unsupported scripts pass through more gracefully
  instead of character-level splitting

For v2.0:

- define script-aware pretokenization
- define byte fallback
- define cross-language protection
- test Turkic Latin and Turkic Cyrillic inputs explicitly
- decide vocabulary allocation only after the above are clear
