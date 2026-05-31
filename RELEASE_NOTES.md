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
- Added official Meta LLaMA tokenizer reference reports for expanded and
  challenge evals.
- Added the public Meta LLaMA model-card link as documentation context.
- Added `data/eval/en_smoke.tsv` and
  `docs/v1_5_english_smoke_findings.md` to measure English do-no-harm behavior.
- Added `data/eval/multilingual_smoke.tsv` and
  `docs/v1_5_multilingual_smoke_findings.md` to measure cross-language
  do-no-harm behavior.
- Added `docs/v1_6_do_no_harm_routing_plan.md` to plan low-risk routing fixes
  without broadening Turkish morphology.
- Added `docs/advisor_update_v1_6_request.md` to summarize current evidence,
  risks, and questions for external advisor review.
- Added `docs/advisor_feedback_triage_v1_6.md` to incorporate advisor feedback
  and reprioritize v1.6 toward evaluation-strengthening before new guards.
- Added `scripts/report_confidence_intervals.py` plus v1.6 bootstrap CI reports
  for expanded, challenge, English smoke, and multilingual smoke metrics,
  including all-baseline visible evals.
- Added `docs/v1_6_confidence_interval_findings.md` to document what the CI
  reports do and do not prove.
- Added `scripts/report_protected_spans.py` and
  `artifacts/v1_6_protected_span_report_stress.md` for protected-span break
  rates across custom, toy BPE, SentencePiece, and HF tokenizer baselines.
- Added `docs/v1_6_protected_span_findings.md` to make protected-span
  interpretation and v1.6b guardrails explicit.
- Added `scripts/report_fertility.py` and
  `artifacts/v1_6_fertility_report_demo_corpus.md` for natural/demo corpus
  token fertility and protected-candidate telemetry.
- Added `docs/v1_6_fertility_findings.md` to close the minimum v1.6a
  measurement-first loop before routing guard implementation.
- Added the v1.6b Batch 1 technical comparator span guard for package/version
  expressions such as `transformers>=4.40`, plus public stress and protected
  span reports for the updated behavior.
- Added the v1.6b Batch 2 Arabic/Greek script word fallback, reducing
  character-level fragmentation for non-Turkish scripts without adding
  multilingual morphology.
- Added the v1.6b Batch 3 English/European apostrophe guard so non-Turkish
  forms such as `Don't`, `John's`, and `L'amico` stay intact while Turkish
  apostrophe suffix forms still split.
- Added the v1.6b Batch 4 non-Turkish Latin word guard so words such as
  `Straße`, `niño`, `Bogotá`, and `università` stay intact without broad
  language detection.
- Documented the v1.6b R3 Azerbaijani routing decision: no v1.6b behavior
  change, defer span-level Turkic routing to v2.0 planning.
- Added the v1.7 measurement-first plan for heldout evaluation, missing
  baselines, downstream probe protocol, and v2.0 router/MorphBPE RFC.
- Added the v1.7 missing baseline protocol covering Turkish-trained
  SentencePiece BPE/Unigram, Morfessor, BERTurk/XLM-R/mT5, and production LLM
  tokenizer references.
- Added the v1.7 downstream probe protocol for byte-normalized small-LM
  comparison of tokenizer usefulness.
- Added the v2.0 router/MorphBPE RFC skeleton tying together protected spans,
  conservative routing, Turkish deterministic morphology, learned fallback, and
  byte fallback.
- Added `configs/v1_7_baselines.toml` and
  `scripts/report_baseline_matrix.py` so visible baseline comparisons can be run
  from a reproducible config instead of scattered command lines.
- Added v1.7 baseline matrix reports for expanded, challenge, English smoke,
  and multilingual smoke visible eval sets.
- Added `configs/v1_7_sentencepiece_sweep.toml` and
  `scripts/run_sentencepiece_sweep.py` for reproducible Turkish-trained
  SentencePiece sweep scaffolding, with claim-grade larger vocab variants kept
  disabled until a larger leakage-checked corpus exists.
- Added v1.7 demo SentencePiece sweep reports for expanded and challenge evals.
- Added `docs/v1_7_claim_grade_corpus_plan.md` to record advisor consensus on
  FineWeb-2/CulturaX/OSCAR/Wikipedia corpus options, leakage checks, size
  targets, and 48k/64k sweep anchors.
- Added a read-only `C:\CELIK_AI` corpus/tokenizer audit and support for local
  Hugging Face `tokenizers` JSON files as optional baseline references.
- Added visible eval reports for the local CELIK 64k ByteLevel BPE tokenizer
  against expanded and challenge Turkish morphology-policy sets.
- Added local/private corpus copy guardrails plus
  `configs/v1_7_claim_grade_corpus.toml` and
  `scripts/prepare_claim_grade_corpus.py` for claim-grade corpus
  manifest/leakage reporting without committing large text.
- Added first v1.7 claim-grade corpus manifest and leakage smoke reports from
  the local CELIK_AI corpus copies.
- Added a local CELIK_AI SentencePiece pilot sweep config and reports for 4k/8k
  BPE/Unigram trained on an ignored leakage-checked local sample.
- Added `docs/v1_7_sentencepiece_pilot_findings.md` to frame the pilot as
  non-claim-grade evidence and keep private model/vocab files out of git.
- Added `scripts/audit_jsonl_corpus_quality.py` plus an aggregate 100k-line
  quality audit for the copied local `celik_gold_corpus.jsonl` source.
- Added quality filters, exact/normalized de-duplication, and UTF-8 byte-length
  caps to `scripts/prepare_claim_grade_corpus.py`.
- Added a filtered 100k-line local CELIK gold pilot sample config and aggregate
  manifest/leakage reports without committing private corpus text.
- Added a filtered CELIK gold SentencePiece pilot sweep for 4k/8k BPE and
  Unigram baselines, with private model/vocab files kept out of git.
- Added `docs/v1_7_celik_gold_filtered_pilot_findings.md` to interpret the
  filtered pilot as baseline pressure, not hidden-eval or downstream evidence.
- Added `scripts/prepare_downstream_probe.py` plus demo and CELIK gold pilot
  configs for deterministic train/valid/test splits and private tokenizer JSONL
  handoff files.
- Added downstream probe prep aggregate reports and
  `docs/v1_7_downstream_probe_prep_findings.md` to separate tokenizer prep from
  actual small-LM bits-per-byte evidence.
- Added clean local CELIK gold corpus sample/leakage configs and 8k/16k
  SentencePiece sweep reports, using a private copied
  `celik_gold_corpus.clean.jsonl` source.
- Added `docs/v1_7_celik_gold_clean_sweep_findings.md` to mark corpus polishing
  as stopped for v1.7 and move focus back to baseline/downstream evidence.
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
