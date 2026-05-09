# Hidden Eval Labeling Guideline

This guideline is for advisors or independent annotators who will prepare the
hidden/heldout evaluation set. The implementer should not inspect the hidden
examples while writing tokenizer rules.

## Core Principle

The hidden set measures two different questions:

1. **Policy fidelity:** Does the tokenizer follow the project's documented
   surface-stem policy?
2. **Linguistic agreement:** Does that policy agree with an independent Turkish
   morphological reference?

For that reason, every row has two gold token columns:

- `gold_independent_tokens_json`
- `gold_policy_tokens_json`

The difference between these columns is not a problem. It is useful evidence.
When they differ, the `divergence_note` explains why.

## Annotator Profile and Effort

Preferred annotator:

- native Turkish speaker
- has not read the project design docs
- preferably has linguistics or Turkish morphology training

Estimated effort for the first 40 examples:

```text
guideline reading:     ~30 minutes
5-item calibration:    ~30 minutes
40 hidden examples:    ~120 minutes
total:                 ~3 hours
```

One annotator is enough for v1.3. A second annotator and inter-annotator
agreement, for example Cohen's kappa, should be added in v1.5.

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
| `divergence_note` | Empty only if both golds match; otherwise one sentence explaining the difference. |

Use valid JSON lists for token columns.

## Calibration Step

Before labeling all 40 examples:

1. Label 5 separate calibration examples.
2. Send them to an advisor or second reviewer, not to the implementer.
3. The reviewer checks format, JSON validity, category choices, and the
   independent-vs-policy distinction.
4. Continue with the full 40 hidden examples only after approval.

Calibration examples are not part of the 40 hidden examples. Once they are
reviewed or discussed, they lose strict hidden status. The five public examples
below are only demonstrations and must not be included in the hidden set.

## Labeling Policies

### Independent Gold

Use the best available independent morphology judgment:

- trained Turkish linguist or morphologist
- Oflazer-style analyzer output
- METU-Sabanci / BOUN treebank style analysis
- another documented Turkish morphological reference

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
| softening | 4 | Surface-stem variants remain important. |
| proper_name | 3 | Apostrophe/proper noun behavior must stay stable. |
| code_mixed | 3 | API/file/mixed-case robustness. |
| verb_future | 2 | Productive chain, likely hybrid-sensitive. |
| verb_past | 2 | Core verbal morphology. |
| loanword_rare | 2 | Unseen loanwords and rare surface stems. |
| question | 2 | Question particle/person suffix cases. |
| informal | 2 | Surface-preserving colloquial forms. |
| punctuation | 1 | Unicode punctuation and separators. |
| numbers_dates | 1 | Already improved, still worth sampling. |

Total: 40 examples.

By v1.5 or v2.0, grow this to 80-100 examples.

## Sampling Workflow

Collect about 1.5x the target count per category, then reduce to the target
count without cherry-picking. This keeps the hidden set more natural and avoids
forcing artificial examples just to fill quotas.

Category-internal variety matters:

- `ambiguity`: include frequent examples such as `yüz`, `at`, `gül`, plus less
  frequent ambiguous forms.
- `negative_word`: include classic examples such as `kadın`, `altın`, plus less
  obvious cases such as `odun`, `pamuk`, and words that resemble `+uk` or `+ik`
  suffix endings.
- `informal`: include at least two surface-preserving forms because this is a
  distinctive design policy of the project.

## Divergence Notes

If `gold_independent_tokens_json` differs from `gold_policy_tokens_json`, write
one short sentence in `divergence_note`.

Example note:

```text
Independent analysis maps Gelicem toward gel+ecek+im; project policy preserves the surface informal suffix +icem.
```

These notes are important research data. They explain whether a mismatch is an
implementation failure or an intentional policy difference.

## Five Public Illustrative Examples

These examples are **not** hidden. They only illustrate the format and must not
be included in the 40 hidden examples.

```text
negative_word	Kadın yakın sokakta bekledi.	["▁Kadın","▁yakın","▁sokak","+ta","▁bekle","+di","."]	["▁Kadın","▁yakın","▁sokak","+ta","▁bekle","+di","."]	
softening	Kitabımdan bahsettim.	["▁Kitap","+ım","+dan","▁bahset","+ti","+m","."]	["▁Kitab","+ım","+dan","▁bahset","+ti","+m","."]	Independent lemma/root may prefer kitap; project policy keeps surface stem Kitab.
ambiguity	Yazın tatile gittik.	["▁Yazın","▁tatil","+e","▁git","+ti","+k","."]	["▁Yazın","▁tatil","+e","▁git","+ti","+k","."]	Intended reading is seasonal/adverbial, not Yaz +ın.
informal	Gelicem birazdan.	["▁Gel","+ecek","+im","▁biraz","+dan","."]	["▁Gel","+icem","▁biraz","+dan","."]	Independent normalized analysis may map to geleceğim; project preserves surface informal suffix.
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
note explaining the uncertainty.

## Handling Negative Examples

Include words that should remain unsplit:

```text
kadın
yakın
altın
alın
kalın
odun
pamuk
```

These examples are valuable because they test false-positive split risk.

## Privacy, Storage, and Rotation

- Keep the real hidden TSV out of Git.
- Preferred private path: `data/eval/private/tr_hidden_eval.tsv`.
- The canonical copy should stay with the advisor or reviewer.
- The implementer should not keep a writable local copy while writing rules.
- Advisors can run evaluation themselves, or provide temporary read-only access.
- Share only aggregate metrics with the implementer when possible.
- Public reports must not include hidden example text.
- If a regression must be discussed, share one anonymized representative example
  rather than the whole set.
- If the implementer accidentally sees a hidden example, mark that row for
  rotation. This is a "no shame, just rotate" policy.
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
