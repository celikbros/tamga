# v1.4 S1 Buffered Ablative Analysis

Status: Batch 2 implemented
Date: 2026-05-29
Tokenizer behavior: changed by the Batch 2 implementation

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

## Implementation Shape

S1 used the narrowest possible change:

1. Do not add `+ndan/+nden` to the broad suffix inventory.

2. Add a dedicated guarded helper for exactly these suffix surfaces after a
   known surface stem:

```text
sından -> +sı +ndan
sinden -> +si +nden
sundan -> +su +ndan
sünden -> +sü +nden
```

3. Do not add them as a broad free-standing greedy split if that can affect
unknown lowercase words.

4. Prefer the segmentation:

```text
sı +ndan
```

over:

```text
sın +dan
```

only inside the guarded suffix-chain parser.

5. Keep apostrophe suffix handling unchanged.

## Positive Tests Added

These now pass:

```text
Mehmet'in arabasından ses geldi.
expected: ["▁Mehmet","'","+in","▁araba","+sı","+ndan","▁ses","▁gel","+di","."]

Dosyasından bir not geldi.
expected: ["▁Dosya","+sı","+ndan","▁bir","▁not","▁gel","+di","."]
```

The second example checks the same pattern outside a proper-name sentence.

## Negative Regression Tests Added

These remain stable:

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

Implemented result:

- `Mehmet'in arabasından ses geldi.` becomes exact match.
- challenge exact match improved from `43/108` to `44/108`.
- challenge F1 improved from `0.8233` to `0.8255`.
- proper_name improved from `8/9` to `9/9`.

This is a useful but small improvement. It should not be bundled with broader
lexicon expansion, passive-stem handling, or `+ma` rules.

## Recommendation

S1 is complete as v1.4 Batch 2.

Do not combine S1 with S2-S5.
