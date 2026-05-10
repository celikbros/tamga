# Multilingual Reviewer Response Form

Reviewer name:

Affiliation or background:

Language/script expertise:

Date:

## 1. Scope Check

Which language, language family, or script are you reviewing?

```text

```

Should this language/script be:

```text
[ ] pass-through only for v1.x
[ ] smoke-test only for v1.x
[ ] considered for v2.0 Turkic-aware handling
[ ] out of scope for now
```

## 2. Layering Review

Current proposed v2.0 layering:

```text
1. Unicode normalization + script-aware pretokenizer
2. Cross-language protection for code, file paths, URLs, numbers, and dates
3. Turkish morphology layer
4. Turkic-aware morphology layer when script/language cues support it
5. MorphBPE fallback
6. Byte fallback
```

Is this order reasonable for your language/script area?

```text

```

What would you change?

```text

```

## 3. Irreversibility Risks

Which decisions would be expensive to change later?

```text

```

Please comment on any relevant risks:

```text
[ ] vocabulary allocation before script policy
[ ] Unicode normalization
[ ] casing / dotted-dotless i
[ ] apostrophe conventions
[ ] diacritics or special characters
[ ] Cyrillic/Latin script mixing
[ ] byte fallback
[ ] other:
```

Notes:

```text

```

## 4. Apostrophe and Punctuation

Does your language/script use apostrophe in a way that could conflict with
Turkish apostrophe+suffix behavior?

```text

```

Examples:

```text

```

## 5. Characters and Normalization

Which characters, diacritics, or normalization choices must be handled carefully?

```text

```

For Turkic languages, please include examples such as `ə`, `ı`, `ğ`, `ñ`,
Cyrillic-specific letters, or any locally important characters.

## 6. Suggested Smoke Examples

Please provide 5-10 short examples that can become public smoke-test candidates.
Do not include private or licensed corpus text.

```text
1.
2.
3.
4.
5.
```

For each example, what should the tokenizer avoid doing?

```text

```

## 7. Current Observation Review

If you reviewed `docs/multilingual_observations.md`, which observations are
expected, surprising, or misleading?

```text

```

## 8. Priority Recommendation

What should be handled before v2.0 vocabulary training?

```text

```

What can safely wait?

```text

```

## 9. Final Recommendation

One-sentence summary:

```text

```

Overall status:

```text
[ ] Strategy looks safe as a v2.0 direction.
[ ] Strategy is mostly safe but needs revisions listed above.
[ ] Strategy has a serious risk and should be revised before further work.
```
