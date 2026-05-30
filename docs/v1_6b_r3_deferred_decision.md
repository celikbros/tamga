# v1.6b R3 Azerbaijani Routing Decision

Date: 2026-05-31

Decision: do not implement R3 in v1.6b.

## Context

v1.6b completed four do-no-harm guard batches:

1. Technical comparator/package span guard
2. Arabic/Greek script word fallback
3. English/European apostrophe guard
4. Non-Turkish Latin word guard

Current verified state:

```text
python -m pytest --basetemp C:\tmp\pytest-basetemp
116 passed

tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

en_smoke.tsv
exact_match: 8/10
f1: 0.8889

multilingual_smoke.tsv
exact_match: 17/20
f1: 0.9404

protected span stress
protected_preserved: 25/25
break_rate: 0.0000
```

The remaining `multilingual_smoke.tsv` failures are mostly Azerbaijani routing
and one English hyphenated form:

```text
adim / Bakida / gedir / uzundur
Turkic-speaking
```

## Advisor Consensus

Both advisor responses recommended not shipping an Azerbaijani routing behavior
change in v1.6b.

The key point is methodological:

- The failing Azerbaijani tokens do not carry strong Azerbaijani-only cues.
- A token-level `schwa` guard would not fix the actual failing tokens.
- A sentence/span-level Azerbaijani route would fix them, but that is a v2.0
  router design problem, not a narrow v1.6b guard.

Therefore:

```text
B is a no-op for the visible failures.
C is early v2.0 routing.
R3 should be documented, not implemented, in v1.6b.
```

## Final R3 Decision

R3 is deferred.

v1.6b closes at Batch 4.

The Azerbaijani issue is documented as a known limitation and moved to v2.0
router/MorphBPE planning.

## Safe Cue Policy

If Azerbaijani routing is revisited later:

```text
Strong cue:
  ə / Ə

Weak cue:
  q / x only with other Azerbaijani evidence

Not a cue:
  ı, ş, ç, ğ, ö, ü
```

`q` and `x` must not trigger Azerbaijani routing by themselves. They are common
in Turkish technical/code-mixed text, names, URLs, commands, and model names.

## Future Regression Candidates

These examples should be used when v2.0 routing is designed, not as a v1.6b
implementation target.

Known Azerbaijani limitation examples:

```text
Mənim adım Əli, Bakıda yaşayıram.
Xəbər: qız məktəbə gedir, dağ yolu uzundur.
```

False-positive traps for `q/x`:

```text
Max'in X hesabını engelledim.
qPCR sonucu dün geldi.
Linux'ta xargs komutunu çalıştırdım.
Qwen modelini 2026'da eğittik.
```

Turkish/code-mixed guardrails:

```text
Türkiye'den geldim.
README.md'yi 2026'da güncelledim.
API'den data aldım.
OpenAI API'den sonuç aldık.
```

Embedded Azerbaijani-name trap:

```text
Əli ile İstanbul'da buluştuk.
Mənim dediğin repo'yu API'den çektim.
```

Pure Turkish must not route to Azerbaijani:

```text
Çağrışımlarım kışın yoğunlaşıyor.
```

## Revert Criteria If Revisited

Any future Azerbaijani/Turkic routing experiment must be reverted if:

```text
tr_gold_expanded < 50/50
any tr_challenge category regresses unexpectedly
protected span break_rate > 0
en_smoke < 8/10
Turkish apostrophe/proper-name examples regress
technical/file/number/date guards regress
Turkish sentences with one foreign token become over-protected
```

## Next Step

Move to v1.7:

```text
independent/heldout eval planning
missing baseline protocol
small downstream/tokenizer-usefulness protocol
v2.0 router/MorphBPE RFC skeleton
```

R3 should not block v1.7.
