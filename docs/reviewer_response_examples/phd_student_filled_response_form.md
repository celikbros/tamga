# Example Scenario: PhD Student Filled Response Form

This is a fictional filled response form. It illustrates the type of answer we
want from a multilingual/Turkic reviewer.

Reviewer name: [Student Name]

Affiliation or background: PhD student, computational linguistics

Language/script expertise: Azerbaijani Latin, Turkish, basic Turkic NLP

Date: 2026-05-11

## 1. Scope Check

Which language, language family, or script are you reviewing?

```text
Azerbaijani in Latin script, with some notes about Cyrillic legacy data.
```

Should this language/script be:

```text
[ ] pass-through only for v1.x
[x] smoke-test only for v1.x
[x] considered for v2.0 Turkic-aware handling
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
Yes. Cross-language protection before morphology is important. Azerbaijani text
can include URLs, file names, Latin abbreviations, and numbers just like Turkish
or English text.
```

What would you change?

```text
For v2.0, I would make script detection explicit before deciding whether the
Turkish morphology layer or a Turkic-aware layer should run. Azerbaijani Latin
should not be sent blindly through Turkish morphology.
```

## 3. Irreversibility Risks

Which decisions would be expensive to change later?

```text
Vocabulary allocation before including Azerbaijani characters would be costly.
If ə, x, q, ğ, ı, ö, ü, ş, ç are poorly represented, Azerbaijani words may fall
into byte fallback too often.
```

Please comment on any relevant risks:

```text
[x] vocabulary allocation before script policy
[x] Unicode normalization
[x] casing / dotted-dotless i
[x] apostrophe conventions
[x] diacritics or special characters
[ ] Cyrillic/Latin script mixing
[x] byte fallback
[ ] other:
```

Notes:

```text
Do not assume Turkish dotted/dotless i rules solve Azerbaijani casing. They are
related, but the system should test Azerbaijani words directly. Also, ə must be
treated as a normal letter, not a separator.
```

## 4. Apostrophe and Punctuation

Does your language/script use apostrophe in a way that could conflict with
Turkish apostrophe+suffix behavior?

```text
Azerbaijani can use apostrophes in borrowed or transliterated forms, but the
Turkish proper-name suffix convention should not be generalized automatically.
For v1.x, pass-through or limited Turkish-only apostrophe handling is safer.
```

Examples:

```text
O'Connor Bakıya gəldi.
D'Artanyan haqqında yazı oxudum.
```

The tokenizer should not treat `O'Connor` or `D'Artanyan` as Turkish suffix
splits.

## 5. Characters and Normalization

Which characters, diacritics, or normalization choices must be handled carefully?

```text
ə, ı, i, ğ, ö, ü, ş, ç, x, q
```

For Turkic languages, please include examples such as `ə`, `ı`, `ğ`, `ñ`,
Cyrillic-specific letters, or any locally important characters.

```text
Azərbaycan
gəldim
uşaqlar
qızlar
xəbərlər
```

## 6. Suggested Smoke Examples

Please provide 5-10 short examples that can become public smoke-test candidates.
Do not include private or licensed corpus text.

```text
1. Azərbaycandan gəldim.
2. Qızlar məktəbə getdilər.
3. Uşaqlar kitabları oxudu.
4. Bakıdan gələn xəbərləri gördüm.
5. README.md faylını açdım.
6. O'Connor Bakıya gəldi.
```

For each example, what should the tokenizer avoid doing?

```text
It should not split ə as a separate token. It should not send Azerbaijani words
through Turkish suffix logic unless a Turkic-aware layer is explicitly enabled.
It should protect README.md before morphology. It should not treat European
names with apostrophe as Turkish suffix constructions.
```

## 7. Current Observation Review

If you reviewed `docs/multilingual_observations.md`, which observations are
expected, surprising, or misleading?

```text
The Azerbaijani result is expected given the current Turkish-only letter set,
but it is a strong signal that script/letter coverage must be decided before
vocabulary training. The `data -> da +ta` example should remain code-mixed /
loanword false-positive, not multilingual.
```

## 8. Priority Recommendation

What should be handled before v2.0 vocabulary training?

```text
1. Treat Azerbaijani letters as letters in pretokenization.
2. Decide whether Azerbaijani goes through a Turkic-aware layer or MorphBPE
   directly.
3. Protect cross-language file/code/URL/number tokens before morphology.
4. Decide byte fallback.
```

What can safely wait?

```text
Full Azerbaijani morphology can wait. A complete Azerbaijani analyzer is not
necessary before the first v2.0 prototype, but pretokenization and vocabulary
coverage cannot wait.
```

## 9. Final Recommendation

One-sentence summary:

```text
The strategy is safe if Azerbaijani letters and apostrophe behavior are handled
before vocabulary allocation, and if Turkish morphology is not applied blindly
to Azerbaijani text.
```

Overall status:

```text
[x] Strategy looks safe as a v2.0 direction.
[ ] Strategy is mostly safe but needs revisions listed above.
[ ] Strategy has a serious risk and should be revised before further work.
```
