# Hidden Eval Labeler Packet

This packet is the short handoff document for the person who will prepare the
first hidden/heldout evaluation set.

## Purpose

The goal is to create a private 40-example hidden eval set for
`tr-centric-tokenizer`. The set should test whether the tokenizer generalizes
beyond examples already visible in the repository.

The implementer should not inspect the hidden examples while writing tokenizer
rules.

## What to Read First

1. `docs/hidden_eval_labeling_guideline.md`
2. This packet
3. The empty TSV template in `data/eval/templates/tr_hidden_eval_template.tsv`

The requester can use `docs/hidden_eval_request_message.md` as the initial
message to the advisor or annotator.

Do not read the tokenizer implementation or design docs before labeling. The
hidden set should reflect independent judgment, not the implementation's current
rules.

## Required Output

Private file:

```text
data/eval/private/tr_hidden_eval.tsv
```

Columns:

```text
category<TAB>text<TAB>gold_independent_tokens_json<TAB>gold_policy_tokens_json<TAB>divergence_note
```

The public repository should contain only the template, not the labeled hidden
examples.

## Workflow

1. Collect roughly 1.5x the target count per category.
2. Choose natural Turkish sentences; do not copy examples from existing project
   eval files.
3. Label 5 separate calibration examples first.
4. Send the 5 calibration examples to an advisor or second reviewer, not to the
   implementer.
5. After calibration approval, label the full 40 hidden examples.
6. Keep the canonical copy with the advisor or reviewer.
7. Run evaluation privately and share aggregate metrics only.

Calibration examples must not be included in the 40 hidden examples. Discussed
calibration rows are no longer strictly hidden.

## Category Targets

| Category | Count |
| --- | ---: |
| ambiguity | 7 |
| negative_word | 7 |
| suffix_chain | 4 |
| softening | 4 |
| proper_name | 3 |
| code_mixed | 3 |
| verb_future | 2 |
| verb_past | 2 |
| loanword_rare | 2 |
| question | 2 |
| informal | 2 |
| punctuation | 1 |
| numbers_dates | 1 |

Total: 40 examples.

## Two Gold Columns

Each row needs two token annotations:

- `gold_independent_tokens_json`: independent morphology reference or annotator
  judgment.
- `gold_policy_tokens_json`: the project's surface-preserving policy.

If the two columns differ, `divergence_note` is mandatory.

Example divergence note:

```text
Independent analysis maps Gelicem toward gel+ecek+im; project policy preserves the surface informal suffix +icem.
```

## Privacy Rules

- Do not commit `data/eval/private/tr_hidden_eval.tsv`.
- Share only aggregate metrics with the implementer when possible.
- Public reports must not include hidden example text.
- If the implementer accidentally sees a hidden row, mark it for rotation.
- Rotate the set every 6-12 months.

## Private Evaluation Commands

```powershell
python scripts/evaluate_hidden_eval.py data/eval/private/tr_hidden_eval.tsv --markdown-out artifacts/v1_3_hidden_eval_report.md
```

This command prints and writes aggregate metrics only. It should not print
hidden sentences or token lists.

If standard policy/independent TSV views are needed:

```powershell
python scripts/prepare_hidden_eval_views.py data/eval/private/tr_hidden_eval.tsv --out-dir data/eval/private
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval_policy.tsv
python scripts/evaluate_tokenizer.py data/eval/private/tr_hidden_eval_independent.tsv
```

Suggested public report shape:

```text
overall_policy_exact: ...
overall_policy_f1: ...
overall_independent_exact: ...
overall_independent_f1: ...
category_policy_f1: ...
category_independent_f1: ...
```

Do not include hidden sentences or token lists in the public report.
