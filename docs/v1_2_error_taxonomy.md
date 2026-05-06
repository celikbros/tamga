# v1.2 Error Taxonomy

v1.2 does not change tokenizer behavior. It labels challenge-set mismatches so
future rule work can be prioritized without chasing every error at once.

## Labels

| Label | Meaning | v1.3 action |
| --- | --- | --- |
| `exact_match` | Expected and actual tokens already match. | Keep as evidence. |
| `safe_rule_candidate` | Isolated punctuation, apostrophe, number/date, or token-boundary issue. | Add a narrow fixture first. |
| `needs_lexicon` | A known surface stem or guarded suffix pattern would likely explain the mismatch. | Batch small lexicon additions with negative regressions. |
| `needs_context` | The surface form is ambiguous without sentence context. | Do not add a deterministic rule yet. |
| `hybrid_candidate` | Productive/complex chain is better suited to MorphBPE or hybrid fallback. | Feed into MorphBPE design. |
| `do_not_fix_yet` | Fixing now risks false positives in common words. | Keep protected until policy is stronger. |

## Command

```powershell
python scripts/label_challenge_mismatches.py data/eval/tr_challenge.tsv data/eval/tr_challenge_labeled.tsv --markdown-out artifacts/v1_2_error_taxonomy_report.md
```

## Policy

- `tr_gold_expanded.tsv` remains the frozen regression set.
- `tr_challenge.tsv` remains a dev/error-analysis set.
- `tr_challenge_labeled.tsv` is generated taxonomy data, not a new gold set.
- `negative_word` and `ambiguity` should not be optimized by broad suffix rules.
- `safe_rule_candidate` is the only label that should usually receive a direct
  deterministic rule in the next implementation step.

## Expected Use

v1.3 should start from the generated label summary:

- pick a small number of `safe_rule_candidate` examples
- add tests first
- verify expanded regression remains 50/50
- re-run challenge evaluation
- re-run taxonomy labeling

The aim is to keep the deterministic core conservative while preparing a path
for MorphBPE/hybrid handling of productive and ambiguous forms.
