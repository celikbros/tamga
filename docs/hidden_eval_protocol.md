# Hidden / Heldout Eval Protocol

This protocol responds to the main methodological concern raised after v1.2:
before adding more rules or lexicon entries, the project needs a small
independent evaluation set that was not used while designing the tokenizer.

## Why This Comes Before v1.3 Rule Work

The current metrics are useful, but they are based on examples visible during
development:

- `tr_gold_expanded.tsv` is a frozen regression set.
- `tr_challenge.tsv` is a dev/error-analysis set.
- `tr_challenge_labeled.tsv` is taxonomy data derived from challenge examples.

These are not hidden signals. If v1.3 and v1.4 add rules based only on these
files, the project risks overfitting to its own examples.

## Goal

Create a small hidden/heldout set before any new tokenizer behavior changes.

Recommended size:

```text
30-50 examples
```

Recommended authorship:

- advisors
- independent reviewers
- examples sampled from natural Turkish text
- examples not inspected by the implementer while writing rules

## File Format

Use the existing three-column TSV format:

```text
category<TAB>text<TAB>expected_tokens_json
```

Example shape:

```text
verb_past<TAB>Geldim.<TAB>["▁Gel","+di","+m","."]
```

The actual hidden set should not be committed if it is meant to stay hidden.

## Recommended Local Path

Use a private ignored directory:

```text
data/eval/private/tr_hidden_eval.tsv
```

This path is ignored by Git. It can be evaluated locally with:

```powershell
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval.tsv
```

If advisors want to share only aggregate numbers, they can run the command and
send the summary output without sharing the examples.

## Suggested Category Balance

For 40 examples:

| Category | Count | Notes |
| --- | ---: | --- |
| suffix_chain | 4 | Long but natural suffix chains. |
| proper_name | 4 | Names, cities, institutions, apostrophe forms. |
| softening | 4 | Surface stem alternations such as `kitab`, `ağac`, `reng`. |
| negative_word | 5 | Words that must not be falsely split. |
| ambiguity | 5 | Forms such as `Yazın`, `Gül`, `Yüz`, `At`, `Ocak`. |
| verb_past | 3 | Simple and compound past-tense forms. |
| verb_future | 3 | Productive future/ability chains. |
| question | 3 | Question particle and person suffix cases. |
| informal | 3 | Surface-preserving colloquial forms. |
| code_mixed | 3 | API/file/mixed-case forms. |
| numbers_dates | 3 | Dates, decimals, license plates, percentages. |

The exact distribution can change, but the set should include both positive
split cases and negative "must not split" cases.

## Authoring Rules

1. Do not copy examples from `tr_gold_expanded.tsv` or `tr_challenge.tsv`.
2. Prefer natural sentences over isolated words.
3. Include examples where not splitting is the desired behavior.
4. Keep surface forms; do not normalize informal text into standard Turkish.
5. Mark expected tokens according to the project's current surface-stem policy.
6. If an example is genuinely ambiguous, label it according to the intended
   reading in that sentence.
7. Record uncertainty in a separate notes file, not inside the TSV.

## Evaluation Policy

Use three evaluation tiers:

| Tier | File | Role |
| --- | --- | --- |
| Frozen regression | `data/eval/tr_gold_expanded.tsv` | Must stay 50/50. |
| Dev/challenge | `data/eval/tr_challenge.tsv` | Visible error-analysis set. |
| Hidden/heldout | `data/eval/private/tr_hidden_eval.tsv` | Independent signal. |

v1.3 should report all three:

```powershell
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval.tsv
```

## Decision Rule for v1.3

A new deterministic rule should be accepted only if:

- frozen regression remains 50/50
- challenge improves or remains stable in target categories
- hidden eval does not show a clear regression
- negative-word and ambiguity examples do not degrade

If hidden eval drops while challenge improves, treat that as an overfitting
warning.

## Relation to BPE Claims

The current BPE comparison uses gold boundaries created under this project's
morphological assumptions. That is acceptable for internal iteration, but a
stronger research claim needs independent annotation or alignment with external
morphological references.

Hidden eval helps by adding an independent human-authored signal before more
rules are added.

## Recommended Next Step

Before v1.3 rule work:

1. Advisors prepare `30-50` hidden examples.
2. The implementer does not inspect the examples while writing rules.
3. Advisors or the user run the hidden evaluation and share only aggregate
   metrics when possible.
4. v1.3 proceeds with `safe_rule_candidate` examples only after the hidden eval
   protocol is in place.
