# Multilingual Observations

Status: factual note  
Date: 2026-05-10  
Tokenizer behavior: not changed

## Purpose

This note records lightweight smoke-test observations while they are fresh. It
is not an evaluation benchmark and not a regression target.

The tokenizer is currently Turkish-centered. Multilingual and Turkic-aware
behavior belongs to later v2.0 planning.

AI expert-style review comments are summarized separately in
[ai_expert_review_triage.md](ai_expert_review_triage.md). Those comments are
advisory signals, not hidden eval evidence.

## Non-Goals

- These observations do not define desired behavior.
- Failures here are not v1.x regressions.
- v1.x will not add language-detection-based fixes for these examples.
- Code-mixed loanword false positives are tracked as Turkish false-positive
  risks, not as multilingual smoke results.

## Smoke Observations

Commands were run with `python -m tr_tokenizer`.

### English Pass-Through

```text
Input:
I came from Istanbul.

Observed:
["▁I", "▁came", "▁from", "▁Istanbul", "."]
```

Basic English pass-through is acceptable for a Turkish-centered prototype.

### German Pass-Through

```text
Input:
Ich komme aus Berlin.

Observed:
["▁Ich", "▁komme", "▁aus", "▁Berlin", "."]
```

Basic German pass-through is acceptable in this narrow example. German compounds
are not tested yet.

### European Apostrophe

```text
Input:
Je viens d'Istanbul.

Observed:
["▁Je", "▁viens", "▁d", "'", "+Istanbul", "."]
```

The apostrophe flow over-applies Turkish suffix logic to a French apostrophe
case. This is a multilingual pass-through gap, not a target for v1.4.

### Turkic Latin

```text
Input:
Azərbaycandan gəldim.

Observed:
["▁Az", "ə", "▁rbaycan", "+dan", "▁g", "ə", "▁ld", "+im", "."]
```

Azerbaijani-specific letters such as `ə` are not handled correctly. The system
partly applies Turkish suffix logic and partly splits around unsupported
characters.

Update: v1.3 later added a narrow pass-through guard for `ə/Ə`-bearing
Azerbaijani Latin words. This note remains as historical context for why that
guard was added; broader Azerbaijani morphology is still out of v1.x scope.

### Turkic Cyrillic

```text
Input:
Қазақстаннан келдім.

Observed:
["Қ", "а", "з", "а", "қ", "с", "т", "а", "н", "н", "а", "н", "к", "е", "л", "д", "і", "м", "."]
```

Cyrillic Turkic input falls to character-level segmentation. This should be
treated as a v2.0 planning signal, not a v1.x regression.

## Code-Mixed Note

```text
Input:
API'den data aldım.

Observed:
["▁API", "'", "+den", "▁da", "+ta", "▁al", "+dı", "+m", "."]
```

`API'den` is handled well, but English `data` is over-split as if it were
Turkish. This is not a multilingual smoke issue. It is a Turkish false-positive
split risk for loanwords/code-mixed text.

Track this under:

- `code_mixed`
- `loanword_rare`
- false-positive split protection

## v2.0 Implications

These observations suggest that v2.0 should preserve room for:

- raw input preservation and offset mapping
- minimal, non-destructive cleanup before protection
- Unicode/script-aware pretokenization
- cross-language protection for code, files, URLs, numbers, and dates
- Turkish morphology as a gated layer, not a default for all Latin input
- Turkic-aware handling only when script and language cues support it
- MorphBPE fallback
- byte fallback as last resort

No vocabulary allocation or normalization commitment should be frozen before
script handling and fallback policy are decided.
