# Hidden Eval Labeling Guideline

This guideline is for advisors or independent annotators who will prepare the
hidden/heldout evaluation set. The implementer should not inspect the hidden
examples while writing tokenizer rules.

## Core Principle

The hidden set should measure two different questions:

1. **Policy fidelity:** Does the tokenizer follow the project's documented
   surface-stem policy?
2. **Linguistic agreement:** Does that policy agree with an independent Turkish
   morphological reference?

For that reason, the hidden eval uses two gold token columns:

- `gold_independent_tokens_json`
- `gold_policy_tokens_json`

## TSV Format

```text
category<TAB>text<TAB>gold_independent_tokens_json<TAB>gold_policy_tokens_json<TAB>divergence_note
```

Column meanings:

| Column | Meaning |
| --- | --- |
| `category` | One category such as `ambiguity`, `negative_word`, `suffix_chain`. |
| `text` | Natural Turkish sentence. Do not copy existing project eval examples. |
| `gold_independent_tokens_json` | Annotation according to an independent morphology reference or annotator judgment. |
| `gold_policy_tokens_json` | Annotation according to this project's documented surface-stem tokenizer policy. |
| `divergence_note` | Empty if both golds match; otherwise explain the difference briefly. |

Use valid JSON lists for token columns.

## Labeling Policies

### Independent Gold

Use the best available independent morphology judgment:

- trained Turkish linguist or morphologist
- Oflazer-style analyzer output
- METU-Sabanci / BOUN treebank style analysis
- other documented Turkish morphological reference

The independent gold may be lemma-oriented or theoretically cleaner than the
project policy, but it must be consistent.

### Project Policy Gold

Use the current documented tokenizer policy:

- Keep surface stems, not necessarily lemmas.
- Preserve word-start marker `▁`.
- Prefix suffix tokens with `+`.
- Preserve apostrophe as a separate token.
- Do not normalize informal forms into standard Turkish.
- Do not split short ambiguous suffix-like endings unless the project policy has
  a guarded reason to do so.

Examples:

```text
kitaplarımdan -> ▁Kitap +lar +ım +dan
kitabımdan    -> ▁Kitab +ım +dan
Gelicem       -> ▁Gel +icem
```

## Category Distribution for First 40 Examples

The first hidden set should emphasize fragile categories rather than categories
already performing well.

| Category | Count | Reason |
| --- | ---: | --- |
| ambiguity | 7 | Context-free splitting risk is high. |
| negative_word | 7 | False-positive suffix splits are more harmful than missed splits. |
| suffix_chain | 4 | Long productive morphology still matters. |
| proper_name | 3 | Apostrophe/proper noun behavior must stay stable. |
| softening | 4 | Surface-stem variants remain important. |
| verb_past | 3 | Core verbal morphology. |
| verb_future | 3 | Productive chain, likely hybrid-sensitive. |
| question | 2 | Question particle/person suffix cases. |
| informal | 2 | Surface-preserving colloquial forms. |
| code_mixed | 3 | API/file/mixed-case robustness. |
| numbers_dates | 2 | Already improved, still worth sampling. |

Total: 40 examples.

By v1.5 or v2.0, grow this to 80-100 examples.

## Five Public Illustrative Examples

These examples are **not** hidden. They only illustrate the format.

```text
negative_word	Kadın yakın sokakta bekledi.	["▁Kadın","▁yakın","▁sokak","+ta","▁bekle","+di","."]	["▁Kadın","▁yakın","▁sokak","+ta","▁bekle","+di","."]	
softening	Kitabımdan bahsettim.	["▁Kitap","+ım","+dan","▁bahset","+ti","+m","."]	["▁Kitab","+ım","+dan","▁bahset","+ti","+m","."]	independent lemma/root may prefer kitap; project policy keeps surface stem Kitab
ambiguity	Yazın tatile gittik.	["▁Yazın","▁tatil","+e","▁git","+ti","+k","."]	["▁Yazın","▁tatil","+e","▁git","+ti","+k","."]	intended reading is seasonal/adverbial, not Yaz +ın
informal	Gelicem birazdan.	["▁Gel","+eceğ","+im","▁biraz","+dan","."]	["▁Gel","+icem","▁biraz","+dan","."]	independent normalized analysis may map to geleceğim; project preserves surface informal suffix
code_mixed	API'den veri aldım.	["▁API","'","+den","▁veri","▁al","+dı","+m","."]	["▁API","'","+den","▁veri","▁al","+dı","+m","."]	
```

If annotators disagree with an illustrative independent gold, that is useful:
record the disagreement. The hidden set is meant to expose those choices.

## Handling Ambiguity

For ambiguous words, label according to the intended sentence reading.

Examples:

- `Yazın tatile gittik.`: seasonal/adverbial reading.
- `Ben bunu yazarım.`: verb reading.
- `Gül dalında açtı.`: noun reading for `Gül`.
- `Yüz kişi geldi.`: number reading.

If the intended reading is unclear, exclude the sentence or add a divergence
note.

## Handling Negative Examples

Include words that should remain unsplit:

```text
kadın
yakın
altın
alın
kalın
odun
```

These examples are valuable because they test false-positive split risk.

## Privacy and Rotation

- Keep the real hidden TSV out of Git.
- Preferred private path: `data/eval/private/tr_hidden_eval.tsv`.
- Share only aggregate metrics with the implementer when possible.
- If a regression must be discussed, share one anonymized representative
  example rather than the whole set.
- Rotate the hidden set every 6-12 months. Old hidden examples may move into the
  challenge set after rotation.

## Metrics to Report

At minimum:

- overall exact match
- overall precision/recall/F1
- category-level exact match and F1
- policy fidelity using `gold_policy_tokens_json`
- linguistic agreement using `gold_independent_tokens_json`

The gap between policy fidelity and linguistic agreement is important. It tells
us whether the implementation is failing, or whether the policy itself diverges
from independent morphology.
