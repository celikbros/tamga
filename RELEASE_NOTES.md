# Release Notes

## Unreleased

- Added `docs/v1_4_decision_framework.md` as a hidden-eval-dependent decision
  framework, not an implementation plan.
- Added revert criteria, low-power category notes, and positive-regression
  requirements to the v1.4 decision framework.
- Added `docs/labeler_recruitment_plan.md` for hidden eval annotator selection
  and first contact.
- Added multilingual strategy and observation notes to keep v2.0 options open
  without changing v1.x tokenizer behavior.
- Added multilingual reviewer packet, request messages, and response form for
  language/Turkic architecture review.
- Added fictional multilingual reviewer response examples to show what useful
  professor/student feedback may look like.
- Added calibration review thresholds for the hidden eval workflow.
- Added `docs/ai_expert_review_triage.md` to summarize Turkish and
  multilingual/Turkic AI review comments without changing tokenizer behavior.
- Refined `docs/multilingual_strategy.md` so v2.0 protection, routing,
  normalization, and byte-fallback decisions remain explicit and reversible.
- Added `docs/v1_3_practical_track.md` and clarified that professor/student
  hidden eval is optional external validation, not the immediate critical path.
- Added `data/eval/tr_stress_public.tsv` and
  `scripts/report_stress_public.py` for public stress reporting and protected
  span visibility.
- Added URL protection in the pretokenizer so `https://...` spans are preserved
  before morphology and sentence-final punctuation remains separate.
- Added `scripts/report_coverage.py` for token-kind telemetry across regression
  and stress TSV files.
- Preserved smart double quotes in normalization and decode spacing so
  `“Merhaba,” dedi.` round-trips without ASCII quote conversion.
- Preserved code-call spacing for protected code-like tokens, e.g.
  `kullanici_adi(ad)` and `ad.strip()`, while keeping plain prose parentheses
  spaced normally.
- Preserved Uzbek apostrophe-like lexical spans such as `Oʻzbekiston`,
  `gʻisht`, and `sanʼat` without routing them through Turkish apostrophe suffix
  splitting.
- Preserved Azerbaijani-specific `ə/Ə` Latin words as surface spans instead of
  splitting around unsupported letters or forcing Turkish morphology.
- Preserved Turkic Cyrillic word spans and dash width in public stress examples,
  bringing the public stress roundtrip report to 28/28 with no `other` tokens.
- Added `docs/v1_3_closing_report.md` to summarize the v1.3 hardening outcome,
  remaining limits, and v1.4 entry criteria.
- Added `docs/v1_4_candidate_shortlist.md` and refreshed the v1.4 challenge
  mismatch analysis without changing tokenizer behavior.
- Protected exact lexical items `peki` and `yeni` to avoid low-risk
  over-splitting (`Pe +ki`, `ye +ni`) without broadening suffix rules.
- Added `docs/v1_4_s1_buffered_ablative_analysis.md` to scope the next
  medium-risk candidate before implementation.
- Added a guarded possessive-buffered-ablative split for known surface stems,
  fixing `arabasından -> araba +sı +ndan` without broad `+ndan/+nden` splitting.

- Added `docs/v1_5_real_tokenizer_baselines.md` to plan Qwen/LLaMA/Mistral and
  SentencePiece BPE/Unigram comparisons beyond the toy BPE baseline.
- Added `docs/current_resume_point.md` so the project can resume without losing
  the v1.4/v1.5 boundary.
- Added optional real-tokenizer baseline infrastructure:
  `src/tr_tokenizer/external_baselines.py` and
  `scripts/compare_real_tokenizers.py`.
- Added `scripts/train_sentencepiece_baselines.py` for local demo
  SentencePiece BPE/Unigram baselines.
- Added local SentencePiece BPE/Unigram v1.5 reports alongside the custom and
  diagnostic character baselines.
- Added first Qwen tokenizer reference reports for expanded and challenge evals.
- Added first Mistral tokenizer reference reports for expanded and challenge
  evals.
- Recorded the official Meta LLaMA tokenizer access attempt as authenticated but
  not authorized for the gated model.
- Added the public Meta LLaMA model-card link as a documentation-only reference
  while tokenizer access remains pending.
- Added `docs/v1_5_baseline_findings.md` to summarize what the real-tokenizer
  comparisons do and do not prove.
- Added the optional `baselines` dependency group for SentencePiece,
  Transformers, and Tokenizers without making them required runtime
  dependencies.

## v1.3.0

v1.3.0 adds the hidden/heldout evaluation protocol and aggregate-only hidden
eval reporting. It does not change tokenizer behavior.

### Highlights

- Added hidden eval protocol and annotator guideline.
- Added a labeler handoff packet and public empty TSV template.
- Added `scripts/evaluate_hidden_eval.py` for policy-vs-independent aggregate
  reporting without printing hidden examples.
- Enforced `divergence_note` when independent and policy gold columns differ.
- Documented separate calibration examples, private storage, rotation, and
  aggregate-only sharing.

### Non-goals

- No tokenizer behavior change.
- No public hidden examples.
- No treebank integration yet; that remains a later methodological
  strengthening track.

## v1.2.0

v1.2.0 adds a challenge mismatch taxonomy layer without changing tokenizer
behavior.

### Highlights

- Added `scripts/label_challenge_mismatches.py`.
- Added generated taxonomy data:
  `data/eval/tr_challenge_labeled.tsv`.
- Added Markdown taxonomy report:
  `artifacts/v1_2_error_taxonomy_report.md`.
- Added taxonomy documentation:
  `docs/v1_2_error_taxonomy.md`.

### Labels

- `exact_match`
- `safe_rule_candidate`
- `needs_lexicon`
- `needs_context`
- `hybrid_candidate`
- `do_not_fix_yet`

### Non-goals

- No tokenizer behavior change.
- No broad suffix splitter change.
- No attempt to force challenge set to 100%.

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
