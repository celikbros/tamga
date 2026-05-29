# v1.4 S1 Buffered Ablative Analysis

Status: analysis only
Date: 2026-05-29
Tokenizer behavior: not changed by this document

## Target

Visible challenge example:

```text
Mehmet'in arabasından ses geldi.
```

Expected:

```json
["▁Mehmet","'","+in","▁araba","+sı","+ndan","▁ses","▁gel","+di","."]
```

Current actual:

```json
["▁Mehmet","'","+in","▁araba","+sın","+dan","▁ses","▁gel","+di","."]
```

## Root Cause

The known surface stem `araba` is found correctly.

The remaining suffix surface is:

```text
sından
```

The current suffix inventory can explain this as:

```text
+sın +dan
```

But the intended policy for this example is:

```text
+sı +ndan
```

The missing inventory item is the buffered ablative suffix:

```text
+ndan / +nden
```

This is not an apostrophe problem. It is a guarded surface-stem suffix-chain
problem.

## Why This Is Medium Risk

Adding `+ndan/+nden` can improve noun suffix chains after 3rd-person possessive:

```text
arabasından -> araba +sı +ndan
dosyasından -> dosya +sı +ndan
evinden     -> ev +in +den
```

But the change must not turn into broad short-suffix splitting. The dangerous
failure mode is accidentally preferring nominal splits inside common words or
question/person forms.

Examples to protect:

```text
Kadın yakın altın kedi.
Yazın tatile gittik.
Yazarım ama göndermem.
Alacak mısınız?
Geliyom musun?
```

## Proposed Implementation Shape

If implemented later, S1 should use the narrowest possible change:

1. Add buffered ablative surfaces to the lexicon-aware suffix inventory:

```text
ndan
nden
```

2. Do not add them as a broad free-standing greedy split if that can affect
unknown lowercase words.

3. Prefer the segmentation:

```text
sı +ndan
```

over:

```text
sın +dan
```

only inside the guarded suffix-chain parser.

4. Keep apostrophe suffix handling unchanged.

## Positive Tests To Add Before Implementation

These should pass after implementation:

```text
Mehmet'in arabasından ses geldi.
expected: ["▁Mehmet","'","+in","▁araba","+sı","+ndan","▁ses","▁gel","+di","."]

Dosyasından bir not çıktı.
expected: ["▁Dosya","+sı","+ndan","▁bir","▁not","▁çık","+tı","."]
```

The second example checks the same pattern outside a proper-name sentence.

## Negative Regression Tests To Add Before Implementation

These should remain stable:

```text
Kadın yakın altın kedi.
Yazın tatile gittik.
Yazarım ama göndermem.
Gül dalında açtı.
Yüz kişi geldi.
Alacak mısınız?
Geliyom musun?
Zeynep'in dosyasını kapattım.
Arabalarımızdakilerdenmişsiniz.
OpenAIlaştırılamayanlardanmış.
```

## Revert Criteria

Revert the S1 implementation if any of these happen:

- `tr_gold_expanded.tsv` drops below 50/50.
- Public stress drops below 28/28 roundtrip.
- Any negative-word or ambiguity regression worsens.
- Question-person forms such as `mısınız` or `musun` break.
- Existing correct possessive+accusative cases such as `dosyasını` break.
- The fix affects apostrophe behavior for English, European, or Uzbek examples.

## Expected Impact

If implemented correctly:

- `Mehmet'in arabasından ses geldi.` becomes exact match.
- challenge exact match may improve from `43/108` to `44/108`.
- proper_name may improve from `8/9` to `9/9`.

This is a useful but small improvement. It should not be bundled with broader
lexicon expansion, passive-stem handling, or `+ma` rules.

## Recommendation

S1 is eligible for a separate v1.4 Batch 2 only if implemented as a guarded
suffix-chain fix with tests first.

Do not combine S1 with S2-S5.
