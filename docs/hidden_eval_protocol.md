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

Treebank or analyzer integration is valuable, but it should be tracked as a
separate research line: **methodological strengthening: independent
morphological reference integration**. The immediate v1.3 task is to start the
hidden evaluation workflow.

## Goal

Create a small hidden/heldout set before any new tokenizer behavior changes.

Recommended size:

```text
40 examples for the first hidden set
80-100 examples by v1.5/v2.0
```

Recommended authorship:

- advisors
- independent reviewers
- examples sampled from natural Turkish text
- examples not inspected by the implementer while writing rules

## Annotator Profile and Effort

Preferred annotator:

- native Turkish speaker
- has not read the project design docs
- preferably has linguistics or Turkish morphology training

One annotator is enough for v1.3. For v1.5, add a second annotator and report
inter-annotator agreement, for example Cohen's kappa.

Estimated effort:

```text
guideline reading:     ~30 minutes
5-item calibration:    ~30 minutes
35 remaining examples: ~105 minutes
total:                 ~2.5 hours
```

This should not be framed as a tiny favor; the annotator needs enough time to do
consistent work.

## File Format

Use a five-column TSV format for hidden eval:

```text
category<TAB>text<TAB>gold_independent_tokens_json<TAB>gold_policy_tokens_json<TAB>divergence_note
```

Column roles:

| Column | Meaning |
| --- | --- |
| `category` | One of the hidden eval categories. |
| `text` | Natural Turkish sentence, not copied from project eval files. |
| `gold_independent_tokens_json` | Independent morphology reference or annotator judgment. |
| `gold_policy_tokens_json` | This project's documented surface-stem policy. |
| `divergence_note` | Required when the two gold columns differ. |

Detailed annotation instructions are in
[`docs/hidden_eval_labeling_guideline.md`](hidden_eval_labeling_guideline.md).
The short handoff document for annotators is
[`docs/hidden_eval_labeler_packet.md`](hidden_eval_labeler_packet.md).

## Calibration Gate

Before labeling the full 40-example set:

1. The annotator labels 5 calibration examples.
2. The examples go to an advisor or second reviewer, not to the implementer.
3. The reviewer checks TSV format, JSON validity, category use, and the
   independent-vs-policy distinction.
4. After approval, the annotator labels the remaining 35 examples.

The 5 public illustrative examples in the guideline must not be included in the
hidden set. They are visible to the implementer and therefore cannot be hidden
test examples.

## Storage and Access Protocol

- The hidden labeled file must not be committed to the public repo.
- Preferred private path: `data/eval/private/tr_hidden_eval.tsv`.
- This path is ignored by Git.
- The canonical copy should stay with the advisor or reviewer.
- The implementer should not keep a writable local copy while writing rules.
- Evaluation can be run by the advisor, or via a temporary read-only mount.
- Public reports should contain aggregate metrics only: overall and
  category-level tables. They should not include hidden example text.
- If the implementer accidentally sees a hidden example, mark that row for
  rotation. This is a "no shame, just rotate" policy.

The private set can be evaluated with:

```powershell
python scripts/evaluate_hidden_eval.py data/eval/private/tr_hidden_eval.tsv --markdown-out artifacts/v1_3_hidden_eval_report.md
```

If separate standard TSV views are needed:

```powershell
python scripts/prepare_hidden_eval_views.py data/eval/private/tr_hidden_eval.tsv --out-dir data/eval/private
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval_policy.tsv
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval_independent.tsv
```

If advisors want to share only aggregate numbers, they can run these commands
and send the summary output without sharing the examples.

## Category Balance

For the first 40 examples:

| Category | Count | Notes |
| --- | ---: | --- |
| ambiguity | 7 | Context-free splitting risk is high. |
| negative_word | 7 | False-positive suffix splits are more harmful than missed splits. |
| suffix_chain | 4 | Long productive morphology still matters. |
| softening | 4 | Surface-stem variants remain important. |
| proper_name | 3 | Names, cities, institutions, apostrophe forms. |
| code_mixed | 3 | API/file/mixed-case forms. |
| verb_future | 2 | Productive future/ability chains. |
| verb_past | 2 | Simple and compound past-tense forms. |
| loanword_rare | 2 | Unseen loanwords and rare surface stems. |
| question | 2 | Question particle and person suffix cases. |
| informal | 2 | Surface-preserving colloquial forms. |
| punctuation | 1 | Unicode punctuation and separators. |
| numbers_dates | 1 | Already improved, still worth sampling. |

Total: 40 examples.

Sampling note: collect roughly 1.5x the target count per category, then reduce
without cherry-picking. For fragile categories, include internal variety:

- `ambiguity`: include common cases such as `yuz`, `at`, `gul` and less common
  cases.
- `negative_word`: include classic cases such as `kadin`, `altin` and less
  obvious suffix-like endings such as `odun`, `pamuk`, `+uk`, `+ik`.

## Authoring Rules

1. Do not copy examples from `tr_gold_expanded.tsv` or `tr_challenge.tsv`.
2. Prefer natural sentences over isolated words.
3. Include examples where not splitting is the desired behavior.
4. Keep surface forms; do not normalize informal text into standard Turkish.
5. Provide both independent morphology gold and project-policy gold.
6. If an example is genuinely ambiguous, label it according to the intended
   reading in that sentence.
7. If the two gold columns differ, `divergence_note` is required.
8. Record general uncertainty in a separate notes file, not inside the TSV.

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
python scripts/evaluate_hidden_eval.py data/eval/private/tr_hidden_eval.tsv --markdown-out artifacts/v1_3_hidden_eval_report.md
python scripts/prepare_hidden_eval_views.py data/eval/private/tr_hidden_eval.tsv --out-dir data/eval/private
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval_policy.tsv
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval_independent.tsv
```

Public hidden-eval reports should include only aggregate metrics:

- overall exact match
- overall precision/recall/F1
- category-level exact match and F1
- policy fidelity using `gold_policy_tokens_json`
- linguistic agreement using `gold_independent_tokens_json`

No hidden text examples should appear in public reports.

## Decision Rule for v1.3

A new deterministic rule should be accepted only if:

- frozen regression remains 50/50
- challenge improves or remains stable in target categories
- hidden eval does not show a clear regression
- policy fidelity and linguistic agreement are reported separately
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

The two-column hidden format also separates two claims:

- **Policy fidelity:** Does the implementation follow our documented policy?
- **Linguistic agreement:** Does that policy agree with independent morphology?

## Recommended Next Step

Before v1.3 rule work:

1. The advisor or reviewer selects an annotator.
2. The annotator reads the labeling guideline and labels 5 calibration examples.
3. A second reviewer checks the calibration output privately.
4. The annotator labels the remaining 35 examples.
5. Advisors or the user run hidden evaluation and share aggregate metrics only.
6. v1.3 proceeds with `safe_rule_candidate` examples only after the hidden eval
   protocol is in place.
