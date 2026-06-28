# Multilingual Strategy

Status: principles, subject to revision  
Date: 2026-05-10  
Tokenizer behavior: not changed

## Scope

`Tamga` is Turkish-centered and multilingual-aware. The current
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
- global lowercase, global casefold, or global NFKC normalization

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
- Unknown or ambiguous Latin/Turkic input should not default to Turkish
  morphology in a future multilingual system.

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
- raw input and offset-map policy
- Unicode normalization beyond safe local needs
- NFC/NFD strategy
- whether NFC is applied only after protected spans are identified
- casing and dotted/dotless `i` behavior across languages
- Turkish-specific apostrophe behavior as an all-Turkic rule
- apostrophe policy for `'`, `’`, `‘`, `ʼ`, `ʻ`, and `` ` ``
- script handling for Latin, Cyrillic, and mixed-script inputs
- language/script routing confidence thresholds
- byte fallback policy
- per-language byte fallback rate targets

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
| Destructive normalization before protection | URL, code, file, and language-specific spans may be changed before they can be protected. |
| Defaulting ambiguous Latin/Turkic spans to Turkish morphology | The system may produce plausible but wrong segmentation instead of falling back safely. |
| Generic apostrophe normalization | Uzbek, Tatar, English, code, and quoted text may be damaged by a Turkish-specific assumption. |

None of these should be locked in v1.x.

## Refined Candidate Layering for v2.0

Subject to revision after prototyping:

1. Raw input preservation and offset map
2. Minimal reversible cleanup only
3. Cross-language protection for code, file paths, URLs, numbers, dates, and
   similar spans
4. Script/language router with confidence scores
5. Turkish morphology layer only for high-confidence Turkish spans
6. Turkic-specific morphology only when supported script/language cues are
   explicit enough
7. MorphBPE fallback, respecting known morphology boundaries when available
8. Byte fallback as lossless last resort

The cross-language protection layer must come before language-specific
morphology. A token like `README.md` should be protected before it reaches
Turkish or Turkic morphology.

The first normalization stage must be non-destructive. No v2.0 design should
assume global NFKC, global lowercase, or global casefold. If NFC is used, the
safer default is to apply it only to non-protected spans and to preserve raw
offsets.

Turkish morphology should not be a default route for unknown input. If the
router is unsure, fallback is safer than a plausible but wrong Turkish split.

Byte fallback is not a quality strategy. It is a lossless safety net, and its
rate should be reported per language/script.

## Near-Term Backlog

For v1.x:

- keep multilingual smoke observations factual
- do not make multilingual smoke a regression target
- consider a narrow future guard against accidental non-Turkish apostrophe
  over-application
- consider a future guard so unsupported scripts pass through more gracefully
  instead of character-level splitting
- keep the AI expert review triage as advisory input, not as hidden eval
  evidence

For v2.0:

- define script-aware pretokenization
- define byte fallback
- define cross-language protection
- define a language/script router and confidence thresholds
- define a language-specific apostrophe policy matrix
- define protected-span normalization rules
- test Turkic Latin and Turkic Cyrillic inputs explicitly
- decide vocabulary allocation only after the above are clear
