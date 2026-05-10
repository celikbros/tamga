# v1.4 Decision Framework + Safe Rule Candidate Analysis

Status: draft for advisor review  
Date: 2026-05-10  
Tokenizer behavior: not changed

## Purpose

This is not an implementation plan. It is a decision framework for v1.4.

The goal is to decide, after hidden eval aggregate results arrive, whether any
low-risk deterministic rule should be added. The decision should not be based on
challenge-set score chasing.

## Inputs

v1.4 decisions must use these inputs:

| Input | Role |
| --- | --- |
| `data/eval/tr_gold_expanded.tsv` | Frozen regression. Must remain 50/50. |
| `data/eval/tr_challenge.tsv` | Visible dev/error-analysis set. |
| `data/eval/tr_challenge_labeled.tsv` | Visible taxonomy data. |
| hidden eval aggregate report | Independent signal. No hidden examples should be inspected. |

## Non-Goals

- Do not optimize directly for `tr_challenge.tsv`.
- Do not add broad greedy suffix rules.
- Do not target `negative_word` or `ambiguity` with deterministic broad rules.
- Do not add hidden examples to the public repo.
- Do not implement MorphBPE in v1.4.

## Pre-Registered Expectations

These expectations are written before hidden eval results are available.

| Expectation | Rationale |
| --- | --- |
| Hidden policy F1 will likely be lower than expanded F1. | Expanded is frozen and visible; hidden is independent. |
| Expected policy F1 range: 0.75-0.85. | Challenge F1 is 0.8184, but hidden should contain more natural variation. |
| Independent F1 may be lower than policy F1. | Independent morphology may prefer lemma-oriented analyses over surface-stem policy. |
| Weakest hidden categories will likely be `ambiguity`, `negative_word`, `informal`, and `verb_future`. | These are either context-sensitive, high false-positive risk, or productive chains. |
| Stronger hidden categories should be `proper_name`, `numbers_dates`, and `punctuation`. | v1.1 isolated many low-risk pretokenizer cases. |

If observed results differ strongly from these expectations, v1.4 should start
with analysis, not implementation.

## Calibration Gate

Hidden eval should start only after a separate 5-example calibration batch.

| Calibration result | Action |
| --- | --- |
| 5/5 accepted | Proceed to the 40 hidden examples. |
| 3-4/5 accepted | Discuss failed rows privately, correct the issue, then proceed if the reviewer is satisfied. |
| 0-2/5 accepted | Revise the guideline or examples, then request a fresh 5-example calibration batch. |

Calibration rows are not part of the 40 hidden examples.

## Current Safe Rule Candidates

These seven visible examples come from challenge taxonomy. They can be analyzed
now because they are not hidden. They map to eight candidate decisions because
S4 contains two separable issues: `tarihinde` and `yazıldı`.

| ID | Category | Visible example | Mismatch pattern | Candidate hypothesis | Regression risk |
| --- | --- | --- | --- | --- | --- |
| S1 | proper_name | `Mehmet'in arabasından ses geldi.` | `arabasından` becomes `araba +sın +dan` instead of `araba +sı +ndan`. | If a known noun stem is followed by possessive `+sı/+si/+su/+sü` plus buffered ablative `+ndan/+nden`, split the buffered ablative as one suffix. | Medium |
| S2 | numbers_dates | `12:30'da toplantı başladı.` | Number/apostrophe flow is correct; `başladı` remains unsplit. | Treat this as a possible lexicon-safe verb-past fixture only if hidden eval shows the same common-verb under-splitting. | Low-medium |
| S3 | numbers_dates | `5'inci satırı sildim.` | Number/apostrophe flow is correct; `satırı` remains unsplit. | Add `satır` as a guarded surface stem candidate only with negative regressions for short `+ı` splitting. | Medium |
| S4a | numbers_dates | `2024/05/01 tarihinde yazıldı.` | Date token is correct; `tarihinde` remains under-split. | Add `tarih` as a guarded surface stem only if hidden eval shows the same date-context pattern. | Medium |
| S4b | numbers_dates | `2024/05/01 tarihinde yazıldı.` | Date token is correct; `yazıldı` is split as `yaz +ıl +dı` rather than `yazıl +dı`. | Treat `yazıl` as a separate explicit passive surface stem only if supported by hidden aggregate patterns. | Medium |
| S5 | punctuation | `Hayır! Bunu yapma.` | Punctuation is correct; `yapma` remains unsplit. | Consider `yap +ma` only as an explicit known-verb negative/imperative pattern. | High |
| S6 | punctuation | `Peki... sonra ne oldu?` | `Peki` over-splits as `Pe +ki`. | Add exact protected lexical item `peki` so `+ki` does not fire inside it. | Low |
| S7 | punctuation | `(Ankara'dan) yeni döndüm.` | Parentheses/apostrophe flow is correct; `yeni` over-splits as `ye +ni`. | Add exact protected lexical item `yeni`. | Low |

## Hypotheses To Test

Each candidate should be phrased as a testable hypothesis before implementation.
Each candidate also needs a pre-registered revert condition.

| Candidate | Expected improvement | Must not regress | Revert if |
| --- | --- | --- | --- |
| S1 buffered possessive+ablative | Improves proper-name/noun suffix-chain F1. | `mısın`, `yakın`, `kadın`, question-person suffix cases. | Expanded falls below 50/50, any protected negative-word case regresses, or question-person suffix cases break. |
| S2 explicit `başla` past split | Improves common verb-past under-splitting. | Unknown verbs should not receive broad `+dı` splitting. | Any unknown verb starts receiving broad past-tense splitting, or expanded falls below 50/50. |
| S3 explicit `satır` stem | Improves object-case examples around `satır`. | `sarı`, `satı`, unrelated short-final words. | Any short-final negative regression appears, or `+ı` becomes broadly aggressive. |
| S4a explicit `tarih` stem | Improves date-context examples such as `tarih +in +de`. | Broad `+in/+de` splitting in unknown words. | Any negative-word or ambiguity case regresses through short suffix splitting. |
| S4b explicit `yazıl` passive stem | Improves passive verb-past examples when the surface stem is `yazıl`. | Existing `yaz +ıl +dı` behavior where expected. | Expanded falls below 50/50 or visible/hidden passive examples show inconsistent policy. |
| S5 explicit `yap +ma` | Improves punctuation/imperative examples. | Negative-word and ambiguity categories; words ending in `ma`. | Any word-final `ma` false positive appears, or hidden `negative_word`/`ambiguity` aggregate worsens. |
| S6 protect `peki` | Reduces punctuation over-splitting. | `+ki` behavior in already correct words. | `Peki...` still fails, expanded falls below 50/50, or existing correct `+ki` cases break. |
| S7 protect `yeni` | Reduces over-splitting in punctuation/question/code-mixed examples. | `yeniden` policy must be decided separately. | `yeni` still over-splits, `yeniden` gets worse, or expanded falls below 50/50. |

Positive regression tests are required too. Each implemented rule must add at
least one positive test asserting the new behavior, in addition to negative
regressions protecting existing behavior.

## Statistical Power Note

Hidden categories with three or fewer examples should be treated as low-power
signals. In the first 40-example hidden set this includes `informal`,
`numbers_dates`, `punctuation`, `question`, `verb_future`, `verb_past`, and
`loanword_rare`.

Their F1 should not trigger decision-tree branches in isolation. They can
support a decision only when the same direction appears across multiple
categories or when visible challenge evidence and hidden aggregate evidence
point to the same pattern.

## Decision Tree After Hidden Eval

Use aggregate hidden metrics only.

1. If expanded regression is not 50/50, stop and fix regression before v1.4.
2. If hidden policy F1 is below 0.65, do not add rules. Review annotation
   protocol and category aggregates first.
3. If hidden `negative_word` or `ambiguity` F1 is below 0.60, do not add broad
   suffix rules. Add only protective regressions or documentation.
4. If hidden policy F1 is 0.65-0.75, v1.4 may add tests and protected lexical
   exceptions only. Avoid suffix-chain behavior changes.
5. If hidden policy F1 is 0.75-0.85 and target categories align with visible
   `safe_rule_candidate` issues, implement at most 1-2 low-risk candidates.
6. If hidden policy F1 is above 0.85 and no fragile category regresses, implement
   at most 2-3 low-risk candidates, still with tests first.

Candidate priority after hidden eval:

| Priority | Candidate | Why |
| --- | --- | --- |
| 1 | S6 protect `peki` | Low risk exact lexical protection. |
| 2 | S7 protect `yeni` | Low risk exact lexical protection, but check `yeniden`. |
| 3 | S1 buffered possessive+ablative | Useful morphology, but needs careful person-suffix regressions. |
| 4 | S2 explicit common verb split | Contained if implemented as one known stem; note that this is a secondary verb-past issue inside a numbers/date example. |
| 5 | S3 explicit `satır` stem | May help object-case handling, but expands lexicon policy and short `+ı` risk. |
| 6 | S4a explicit `tarih` stem | Useful in date contexts, but expands short `+in/+de` handling risk. |
| 7 | S4b explicit `yazıl` passive stem | Separate passive-stem policy question; should not be bundled with S4a. |
| 8 | S5 `yap +ma` | Highest risk because `+ma` is productive and ambiguous. |

S2 should remain visible in this framework because it came from a
`numbers_dates` challenge row, but the candidate itself is not a number/date
fix. If taxonomy is regenerated later, this row may be better described as a
secondary verb-past mismatch within a number/date fixture.

## Required Regression Tests Before Any Rule

Any v1.4 implementation must keep these checks:

- `python -m pytest`
- `python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv`
- `python scripts/evaluate_tokenizer.py data/eval/tr_challenge.tsv`

Protected examples:

```text
Kadın yakın altın kedi.
Yazın tatile gittik.
Yazarım ama göndermem.
Gül dalında açtı.
Yüz kişi geldi.
Arabalarımızdakilerdenmişsiniz.
OpenAIlaştırılamayanlardanmış.
Geldim.
Alacak mısınız?
```

Candidate-specific negative regressions should be added before implementation,
not after.

## Possible v1.4 Outcomes

| Hidden eval result | v1.4 outcome |
| --- | --- |
| Weak or surprising hidden metrics | No tokenizer change; improve protocol/reporting. |
| Fragile categories regress | Add protective tests only. |
| Stable metrics with low-risk visible issue | Implement 1-2 exact/protected rules. |
| Strong metrics across target categories | Implement a small guarded batch, still no broad greedy suffix expansion. |

## Backlog, Not v1.4

- Methodological strengthening: independent morphological reference integration
  for METU-Sabanci / BOUN / Oflazer-style resources.
- Literature note for Turkish tokenization and morphology-aware tokenization.
- MorphBPE/hybrid trainer prototype.
