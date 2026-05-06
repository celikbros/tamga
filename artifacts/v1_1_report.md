# v1.1 Report

v1.1 is a low-risk pretokenizer release. It improves isolated token-boundary
cases without broadening the general suffix splitter.

## Scope

- proper-name apostrophe suffix gap
- number/date/code-like pretokenizer guards
- punctuation fixtures around quoted and comma/semicolon cases

Out of scope:

- `negative_word`
- `ambiguity`
- broad suffix inventory expansion
- context-sensitive disambiguation

## Verification

```powershell
python -m pytest
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv
python scripts/analyze_mismatches.py data/eval/tr_challenge.tsv artifacts/challenge_mismatch_analysis_v1_1.md
```

## Summary

| Metric | Before v1.1 | After v1.1 |
| --- | ---: | ---: |
| challenge exact match | 21/108 | 40/108 |
| challenge precision | 0.8037 | 0.8600 |
| challenge recall | 0.7155 | 0.7807 |
| challenge F1 | 0.7570 | 0.8184 |
| expanded exact match | 50/50 | 50/50 |

## Target Categories

| Category | Before exact | Before F1 | After exact | After F1 |
| --- | ---: | ---: | ---: | ---: |
| numbers_dates | 0/9 | 0.5693 | 6/9 | 0.9091 |
| proper_name | 2/9 | 0.8409 | 8/9 | 0.9785 |
| punctuation | 2/9 | 0.8392 | 6/9 | 0.9388 |

## Guard Categories

| Category | Before exact | Before F1 | After exact | After F1 |
| --- | ---: | ---: | ---: | ---: |
| negative_word | 0/9 | 0.6387 | 0/9 | 0.6387 |
| ambiguity | 2/9 | 0.7304 | 2/9 | 0.7304 |

These categories were intentionally not optimized in v1.1. They need an
explicit policy before rule changes.

## Remaining Highest-Risk Areas

| Priority | Category | Why risky |
| --- | --- | --- |
| P1 | negative_word | Short suffixes can create false-positive splits such as `kadın -> kad +ın`. |
| P2 | ambiguity | Surface forms like `Yazın`, `Gül`, `Yüz`, `Yazarım` require policy or context. |
| P3 | verb_future | Productive suffix chains are useful but easy to overgeneralize. |
| P4 | softening | Surface stem expansion helps but can leak into normal words if too broad. |

## Next Step

v1.2 should be a policy/documentation step before more tokenizer rules:

- define ambiguity handling policy
- define negative-word guard policy
- decide whether context-free tokenizer should split ambiguous forms
- list examples that must remain unsplit
