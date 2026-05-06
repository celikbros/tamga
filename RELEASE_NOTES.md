# Release Notes

## v1.1.0

v1.1.0, v1.0-rc2 sonrasinda dusuk riskli pretokenizer iyilestirmelerine
odaklanir. Genel greedy suffix splitter agresiflestirilmedi; `negative_word` ve
`ambiguity` kategorileri bilincli olarak hedef disi birakildi.

### Highlights

- Numeric-like tokenlar kelime baslangici marker'i alir:
  `2025`, `3.14`, `34-ABC-1907`, `12:30`, `2024/05/01`, `2GB`.
- File-like apostrof formlari korunur ve suffix olarak ayrilir:
  `README.md'yi -> ▁README.md ' +yi`.
- Apostrof sonrasi suffix akisi dar kapsamli guclendirildi.
- Punctuation fixture'lari eklendi:
  `"Merhaba,"`, `Evet;`, `Ali, Ayşe'ye`, `README.md'yi`.
- v1.1 hedef mismatch dokumu eklendi:
  `docs/v1_1_target_mismatches.md`.
- v1.1 challenge analiz raporu eklendi:
  `artifacts/challenge_mismatch_analysis_v1_1.md`.

### Metrics

| Metric | Before v1.1 | After v1.1 |
| --- | ---: | ---: |
| challenge exact match | 21/108 | 40/108 |
| challenge F1 | 0.7570 | 0.8184 |
| numbers_dates F1 | 0.5693 | 0.9091 |
| proper_name F1 | 0.8409 | 0.9785 |
| punctuation F1 | 0.8392 | 0.9388 |
| expanded exact match | 50/50 | 50/50 |

### Non-goals

- No broad morphology rule expansion.
- No changes intended for `negative_word` or `ambiguity` policy.
- No production-tokenizer claim.

## v1.0.0-rc2

v1.0.0-rc2 freezes the deterministic core and adds challenge mismatch analysis.

- `tr_gold_expanded.tsv` is the frozen regression set.
- `tr_challenge.tsv` is the dev/error-analysis set.
- `scripts/analyze_mismatches.py` writes categorized mismatch reports.
- Git tag: `v1.0.0-rc2`.
