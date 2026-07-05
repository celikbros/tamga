# Current Resume Point

Date: 2026-07-05

## Latest Actual State: Tamga v3.8 Production-Final

Tamga v3.8 is accepted and frozen for the Turkish-primary CELIK-GARDAS Faz 4
pretraining run.

```text
tokenizer: sp64k_final_protected_passthrough_sidecar_controls128
effective vocabulary size: 64,384
full-corpus lines: 6,027,968
full-corpus tokens: 2,499,949,602
tokens/raw byte: 0.184311
SP alignment mismatches: 0
status: ACCEPTED / FROZEN
owner of the next critical path: LLM team
```

Canonical current documents:

```text
docs/v3_8_production_final_closure.md
docs/v3_8_phase2_acceptance_status.md
docs/tamga_brand_contract.md
docs/tamga_v3_8_release_and_maintenance_roadmap.md
```

The tokenizer algorithmic line is closed for this corpus and model run. Reopen
it only for a reproduced regression, security/reconstruction defect, or an
explicit new corpus scope. Multilingual or code-heavy expansion requires a new
version and compatibility decision; it must not mutate v3.8.

Repository release curation is complete. The public source, tests, configs,
aggregate evidence, and the v3.8.0 tag are published at
https://github.com/celikbros/tamga without private corpora, private models, or
full token binaries.

Post-release repository housekeeping (2026-07-05):

```text
README.md rewritten as a bilingual (Turkish/English) front page
previous detailed README archived verbatim: docs/readme_research_history_tr.md
CLAUDE.md added: commit-authorship rule + v3.8 freeze guardrails for AI agents
deploy-key SSH push access configured (github.com-tamga alias)
full test suite verified: 319/319 passed
```

No open tokenizer-side task remains. The critical path is Faz 4 pretraining,
owned by the LLM team.

## Historical State: v2.1 Protected Sidecar Contract

The current v2.1 practical protected-span baseline is:

```text
sp64_protected_passthrough_sidecar
```

Decision:

```text
Use logical byte-span sidecar metadata and avoid global token-boundary
pre-splitting as the baseline.
```

Why:

```text
passthrough sidecar is lossless and exact-roundtrip
test tokens/raw byte: 0.159660
pre-split sidecar test tokens/raw byte: 0.165755
global pre-split tax: +0.006095 tokens/raw byte, about +3.8%
passthrough keeps model-token stream decoupled from detector changes
PII/redaction can use byte offsets plus conservative boundary-token over-mask
```

Advisor split:

```text
B/passthrough: GeminiFlashExt, Qwen37Plus, Fable5
A/pre-split: GeminiPro, Grok43
final project reading: choose B unless exact-copy/constrained decoding over
protected token spans becomes a committed base-model requirement
```

Final handoff package:

```text
docs/v2_1_final_handoff_package.md
status:
  v2.1 can be frozen around sp64_protected_passthrough_sidecar
  global pre-split remains optional only under explicit downstream requirement
  next work is packaging/regression or separate v2.2 morphology research
```

Important artifacts:

```text
docs/v2_1_final_handoff_package.md
docs/v2_1_regression_checklist.md
docs/v2_1_closure_gauntlet_findings.md
docs/v2_1_passthrough_sidecar_handoff_contract.md
docs/advisor_feedback_v2_1_sidecar_contract_triage.md
docs/v2_1_presplit_sidecar_findings.md
docs/llm_team_question_v2_1_sidecar_contract.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_dry_run.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test.md
artifacts/v2_1_sidecar_detector_adversarial_battery.md
artifacts/v2_1_sidecar_route_density_audit_valid_test.md
artifacts/v2_1_sidecar_route_density_audit_train_valid_test.md
artifacts/v2_1_sidecar_operation_simulation_train_valid_test.md
artifacts/v2_1_real_mix_text_sample_materialization_smoke.md
artifacts/v2_1_real_mix_text_sample_materialization_60k.md
artifacts/v2_1_sidecar_operation_simulation_real_mix_smoke.md
artifacts/v2_1_sidecar_operation_simulation_real_mix.md
artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
artifacts/v2_1_sidecar_detector_adversarial_battery_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_valid_regression.md
artifacts/v2_1_passthrough_sidecar_roundtrip_test_regression.md
```

Regression lock:

```text
docs/v2_1_regression_checklist.md
latest result:
  targeted unit tests: 44 passed
  detector battery: 61 cases, 62 expected spans, F1 1.000000
  valid roundtrip: 1994/1994
  test roundtrip: 1998/1998
  dry-run test tokens/raw byte: 0.159660
  real-mix pre-split tax: +0.006088 tokens/raw byte, relative 0.036279
  20M passthrough test BPB: 1.947129
important route invariant:
  percent_encoded and azerbaijani_word must remain in the sidecar passthrough
  route lists
```

Detector battery:

```text
61 cases
62 expected spans
precision/recall/F1: 1.000000
```

Pilot route density on full v1.8 train/valid/test:

```text
protected spans: 95162
protected bytes/raw byte: 0.016414
protected line share: 0.743047
dominant routes:
  numeric_like: 80938 occurrences, 0.009804 bytes/raw byte
  file_like: 8005 occurrences, 0.004528 bytes/raw byte
  apostrophe_surface: 3662 occurrences, 0.001336 bytes/raw byte
reading:
  protected material is frequent by line but small by byte share in this pilot;
  train, valid, and test are in the same protected-density band;
  future alignment work should be selective by route class, not global by
  default.
```

Downstream conservative masking simulation:

```text
artifact: artifacts/v2_1_sidecar_operation_simulation_train_valid_test.md
policy simulated:
  protected byte span -> all overlapping SP tokens -> conservative over-mask
full train/valid/test:
  extra mask bytes/raw byte: 0.004100
  extra/protected byte: 0.249802
  edge-aligned span rate: 0.073916
  crossing span rate: 0.926084
  max extra bytes/span: 9
route extra-mask drivers:
  numeric_like: 106852 extra bytes
  file_like: 7790 extra bytes
  apostrophe_surface: 3201 extra bytes
reading:
  passthrough is not token-boundary aligned and should not be sold as exact
  token-index protection, but conservative masking is cheap on this pilot:
  about 0.41% extra raw bytes masked.
```

Real-mix sampling helper:

```text
script: scripts/materialize_v2_1_real_mix_text_sample.py
purpose:
  materialize JSONL corpus `text` fields into raw .txt sample files before
  route-density or operation-simulation audits
smoke:
  source: data/train/private/celik_ai/trt_news_corpus.jsonl first 100 rows
  output: artifacts/private/v2_1_real_mix/real_mix_smoke.txt
  operation simulation extra mask bytes/raw byte: 0.003509
  reading: end-to-end JSONL sample -> raw text -> operation audit path works
real-mix 60k sample:
  output: artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt
  report: artifacts/v2_1_real_mix_text_sample_materialization_60k.md
  scanned/written lines: 40388 / 40388
  output bytes: 44392189
  source mix:
    trt_news: 388 lines
    academic: 20000 lines
    ttk: 20000 lines
  next:
    run sidecar operation simulation on this sample
real-mix operation simulation:
  report: artifacts/v2_1_sidecar_operation_simulation_real_mix.md
  raw bytes: 44351801
  protected spans: 149999
  protected bytes/raw byte: 0.015398
  extra mask bytes/raw byte: 0.003983
  extra/protected byte: 0.258681
  edge-aligned span rate: 0.077861
  crossing span rate: 0.922139
  max extra bytes/span: 9
  dominant extra-mask routes:
    numeric_like: 160582 extra bytes
    file_like: 9588 extra bytes
    apostrophe_surface: 6477 extra bytes
  reading:
    real-mix confirms pilot; conservative masking cost remains about 0.4%
    extra raw bytes, so global pre-split is still not justified by
    masking/redaction cost alone.
real-mix token-pressure audit:
  report: artifacts/v2_1_sidecar_route_density_real_mix_with_pressure.md
  SP tokens/raw byte: 0.167769
  passthrough tokens/raw byte: 0.167822
  pre-split tokens/raw byte: 0.173911
  pre-split tax: +0.006088 tokens/raw byte
  pre-split relative tax: 0.036279
  reading:
    global pre-split tax is stable on the stronger mixed-domain sample;
    route-selective alignment should be tested before any future global
    pre-split.
20M tiny-LM passthrough row:
  report: artifacts/v2_1_tiny_lm_passthrough_sidecar_20mbytes.md
  steps: 6042
  approx bytes seen: 19998919
  final valid BPB: 1.935810
  test BPB: 1.947129
  valid/test bits per token: 12.1730 / 12.1955
  reading:
    v2.1 selected contract now has a fixed-byte LM-loss reference row.
```

Pre-split remains available as optional variant:

```text
sp64_protected_presplit_sidecar
exact roundtrip valid/test: 1994/1994 and 1998/1998
protected edge alignment: 1.000000
use only if token-boundary protected spans are a real downstream requirement
```

Next sequence:

```text
1. Do not run pre-split 20M now.
2. Passthrough sidecar 20M fixed-byte row is complete.
3. Real-mix protected-route density with token pressure is complete.
4. If exact-copy/constrained decoding becomes committed, test selective
   pre-split by route class before global pre-split.
5. Otherwise, close v2.1 and move new research to v2.2.
```

## Latest Actual State: v2.2 Handoff Hardening

The project target has been reframed:

```text
v2.1 = closed internal protected-sidecar baseline
v2.2 = handoff hardening
v3.0 = reserved first LLM-team experimental handoff candidate, only after v2.x is complete
```

New v2.2 smoke audit:

```text
script: scripts/audit_v2_2_llm_handoff_smoke.py
tests: tests/test_v2_2_llm_handoff_smoke.py
hardening gate: docs/v2_2_llm_handoff_hardening_gate.md
roadmap: docs/v2_2_to_v3_0_roadmap.md
schema candidate: docs/v2_2_sidecar_jsonl_schema.md
LLM README draft: docs/v2_2_llm_team_integration_readme.md
```

What the smoke checks:

```text
exact encode/decode reconstruction
valid token id ranges
sidecar byte/char offsets slicing back to surfaces
required passthrough route invariants
fallback source token rate
conservative protected-span masking overhead
LM batch-window formation
```

Current v2.2 smoke results:

```text
targeted tests:
  tests/test_v2_2_llm_handoff_smoke.py
  tests/test_v2_1_sidecar_operation_simulation.py
  tests/test_tiny_lm_bpb_probe.py
  result: 28 passed

valid/test 250-line smoke:
  report: artifacts/v2_2_llm_handoff_smoke_valid_test_250.md
  exact: 500/500
  fallback rate: 0.000018
  sidecar failures: 0
  extra mask bytes/raw byte: 0.002666
  LM windows: 221
  overall: PASS

real-mix 5k smoke:
  report: artifacts/v2_2_llm_handoff_smoke_real_mix_5k.md
  exact: 5000/5000
  fallback source tokens: 701
  fallback rate: 0.000731
  protected spans: 16683
  sidecar failures: 0
  extra mask bytes/raw byte: 0.003117
  LM windows: 1883
  overall: PASS

full real-mix smoke:
  report: artifacts/v2_2_llm_handoff_smoke_real_mix_full.md
  exact: 40388/40388
  failures: 0
  fallback source tokens: 3395
  fallback rate: 0.000456
  protected spans: 149999
  sidecar failures: 0
  extra mask bytes/raw byte: 0.003983
  LM windows: 14616
  overall: PASS
  closed regression:
    azerbaijani_word must be included in the sidecar passthrough route lists
```

v2.2 closure:

```text
v2.2 is effectively closed as the handoff smoke gate:
  valid/test smoke PASS
  real-mix 5k smoke PASS
  full real-mix smoke PASS
  targeted unit tests PASS

Next:
  v2.3 schema freeze
  v2.4 LLM consumer simulation
  v2.5 wider robustness only if needed
  do not declare v3.0 yet
```

## Latest Actual State: v2.3 Sidecar Schema Freeze

v2.3 freezes the current sidecar JSONL schema:

```text
schema_version: v2.2-sidecar-jsonl-1
tokenizer: sp64_protected_passthrough_sidecar
schema doc: docs/v2_2_sidecar_jsonl_schema.md
freeze doc: docs/v2_3_sidecar_schema_freeze.md
validator: scripts/audit_v2_3_sidecar_schema_contract.py
tests: tests/test_v2_3_sidecar_schema_contract.py
```

Full real-mix schema audit:

```text
report: artifacts/v2_3_sidecar_schema_contract_audit_real_mix_full.md
records: 40388
spans: 149999
total failures: 0
status: PASS
```

Current next sequence:

```text
1. v2.4 LLM consumer simulation is now closed.
2. Decide whether v2.5 wider robustness is required.
3. Finalize LLM-team README and package after v2.5 decision.
4. Only then consider v3.0.
```

## Latest Actual State: v2.4 LLM Consumer Simulation

v2.4 validates the frozen sidecar for downstream consumer operations:

```text
script: scripts/audit_v2_4_llm_consumer_simulation.py
tests: tests/test_v2_4_llm_consumer_simulation.py
findings: docs/v2_4_llm_consumer_simulation_findings.md
report: artifacts/v2_4_llm_consumer_simulation_real_mix_full.md
```

Full real-mix consumer simulation:

```text
lines: 40388
protected spans: 149999
copy failures: 0
redaction failures: 0
token-mask failures: 0
total failures: 0
extra mask bytes/raw byte: 0.003983
status: PASS
```

Current next sequence:

```text
1. v2.5 wider robustness closeout is complete.
2. v3.0 experimental handoff package is prepared.
3. Next step is human review / LLM-team handoff, not more tokenizer sweeps.
```

## Latest Actual State: v2.5 Closeout and v3.0 Package

v2.5:

```text
closeout doc: docs/v2_5_wider_robustness_closeout.md
decision: no extra robustness run required before experimental handoff
```

v3.0:

```text
package doc: docs/v3_0_experimental_handoff_package.md
status: experimental LLM-team handoff package prepared
not claimed: final production tokenizer
```

Current next sequence:

```text
1. Review docs/v3_0_experimental_handoff_package.md.
2. Hand to LLM team for integration smoke if accepted.
3. Open a new branch only if the LLM team requires token-boundary spans,
   throughput benchmarks, or actual dataloader integration changes.
```

## Latest Actual State: Context-Free Unigram/Pruning Bound

The latest Fable5-guided branch has clarified the context-free Unigram/pruning
path:

```text
score-only Unigram / EM is weak
teacher-distilled score bound is still below the desired frontier
eval-side crossing concentration was an artifact
train-side attribution shows low-support/context-dependent residual damage
simple high-rate pruning is now a closing negative result, not a path forward
```

New findings:

```text
docs/v2_0_distilled_score_bound_findings.md
docs/v2_0_pruned_sp_probe_findings.md
docs/advisor_feedback_v2_0_distilled_score_bound_triage.md
docs/v2_0_context_free_frontier_and_next_steps.md
docs/advisor_update_v2_0_distilled_score_bound.md
```

Teacher-distilled 16k bound:

```text
bare Challenge F1: 0.7509 at 2.3525 tokens/word
finite Challenge F1: 0.7219 at 2.4413 tokens/word
deployed crossing: 139/305, rate 0.455738
high-rate attribution: about 95% from >=0.70-rate pieces
```

Targeted pruning probes:

```text
all >=0.70 high-crossing pieces:
  selected pieces: 4329
  bare F1: 0.7447
  finite F1: 0.6582
  decision: too blunt; do not promote

non_word_start >=0.70 high-crossing pieces:
  selected pieces: 403
  bare F1: 0.7486
  finite F1: 0.6875
  crossed boundaries: 151/305
  decision: best small inventory probe, but still not enough
```

Closing pruning sweep:

```text
rate=1.00/count20:
  bare/finite Challenge F1: 0.7351 / 0.6755
  crossed boundaries: 170/305

rate>=0.90/count20:
  bare/finite Challenge F1: 0.7482 / 0.6871
  crossed boundaries: 155/305

rate>=0.70/count50:
  bare/finite Challenge F1: 0.7497 / 0.6897
  crossed boundaries: 153/305

decision:
  no pruning row materially beats pruned_ge070_nonword
```

Teacher-distilled 16k Gold:

```text
SP64 bare/finite F1: 0.7551 / 0.7314
teacher-distilled 16k bare/finite F1: 0.8042 / 0.8129
interpretation: gold and challenge measure different regimes; use both
```

Wrapper-tax contrast on Challenge:

```text
SP64 tax: -0.0596
pruned_ge070_all tax: -0.0865
pruned_ge070_nonword tax: -0.0611
teacher-distilled 16k tax: -0.0290
interpretation: wrapper tax is model-dependent and route-specific
```

Current recommendation:

```text
Do not continue score-only EM/teacher-distillation.
Do not continue high-rate pruning sweeps.
Do not start MorphBPE yet.
Build the consolidated four-model frontier table.
If budget allows, run one fixed-byte tiny-LM calibration across the ladder.
In parallel, audit/redesign numeric/file/apostrophe finite-wrapper routes.
```

Prepared tiny-LM ladder config:

```text
configs/v2_0_tiny_lm_context_free_ladder.toml
```

Dry-run note:

```text
Dry-run completed via user run:
  artifacts/v2_0_tiny_lm_context_free_ladder_dry_run.md
  artifacts/private/v2_0_tiny_lm_context_free_ladder_dry_run/encoded_stats.jsonl

2M-byte fixed-step counts:
  finite_protected_sp64_numeric_sp_floor: 622
  finite_protected_pruned_ge070_nonword: 630
  finite_protected_teacher_distilled_16000: 675
  finite_protected_teacher_distilled_2000: 730

Run commands are recorded in:
  docs/v2_0_context_free_frontier_and_next_steps.md
```

## Latest Training-Time Objective Triage

The newest advisor round changes the immediate order of work:

```text
do not start a full custom trainer yet
first fix the wrapper / normalization contract and re-emit the protected floor
```

The broad direction remains:

```text
finite protected routing
+ learned tokenizer
+ Turkish morphology teacher as a soft training-time prior
```

But the active protected floor is not clean enough to anchor new objective
claims while roundtrip is failing. Runtime boundary-biased decode stays demoted,
and the toy boundary-weighted BPE smoke remains only a mechanical sanity check.

New triage document:

```text
docs/advisor_feedback_v2_0_training_time_objective_choice_triage.md
```

Current next sequence:

1. Define byte-exact vs normalized-exact contract.
2. Repair/re-audit the protected wrapper. Done for finite protected floor via
   route-only protected splitting.
3. Re-emit baseline tables. Done for repaired strict and numeric-SP floors.
4. Run Rung-0 diagnostic: unconstrained SP64 path vs morphology-compliant path.
   Done on challenge and challenge+valid200.
5. If promising, try stock SentencePiece partial-boundary training before
   writing a heavier custom objective.

Route-only finite protected repair:

```text
script changed: scripts/run_tiny_lm_bpb_probe.py
test: tests/test_tiny_lm_bpb_probe.py -> 12 passed
new audits:
  artifacts/v2_0_roundtrip_wrapper_tax_audit_valid_after_route_only_byte_fallback.md
  artifacts/v2_0_roundtrip_wrapper_tax_audit_test_after_route_only_byte_fallback.md
finite protected numeric-SP floor valid exact:
  before: 17/1994
  after route-only: 1991/1994
  after route-only + UTF-8 fallback: 1994/1994
finite protected numeric-SP floor test exact:
  after route-only + UTF-8 fallback: 1998/1998
clean no-protected wrapper tax:
  before: +7.6715 tokens/line
  after: +0.0062 tokens/line valid, 0.0000 tokens/line test
valid tokens/raw byte:
  before: 0.171202
  after: 0.162866
test tokens/raw byte:
  after: 0.163779
remaining bare SP64 failures: rare unknown/character coverage cases; repaired
finite floor handles them with UTF-8 byte fallback
intrinsic reports:
  artifacts/v2_0_finite_protected_sp64_intrinsic_eval_strict_repaired.md
  artifacts/v2_0_finite_protected_sp64_intrinsic_eval_numeric_sp_repaired.md
numeric-SP repaired floor:
  Challenge F1: 0.6755
  Protected stress: 25/25
  Challenge avg model tokens/word: 2.2977
interpretation:
  the floor is a valid protection/lossless baseline again, but it is not a
  morphology-improving tokenizer; morphology signal must come from the next
  training-time objective branch
Rung-0 SP64 morph-compliant path audit:
  script: scripts/audit_v2_sp64_morph_compliant_paths.py
  findings: docs/v2_0_sp64_morph_compliant_path_audit_findings.md
  challenge crossing share: 0.747059
  challenge avg token delta constrained-unconstrained: 1.0647
  challenge+valid200 crossing share: 0.928189
  challenge+valid200 avg token delta: 1.5614
  decision: hard no-cross morphology is too costly; try stock SP partial
    boundary pretokenization before custom trainer work
partial-boundary infrastructure:
  script: scripts/materialize_v2_partial_boundary_sp_view.py
  candidate runner: scripts/run_v2_candidate_sentencepiece_probe.py
  tests: 21 passed for partial-boundary/candidate/evaluator/tiny-lm helpers
  rho=0.10 train view:
    artifacts/private/v2_0_partial_boundary_sp/partial_boundary_rho010.train.txt
  rho=0.10 config:
    configs/v2_0_partial_boundary_rho010_sentencepiece.toml
  rho=0.10 view report:
    artifacts/v2_0_partial_boundary_rho010_view.md
  rho=0.10 SP probe:
    artifacts/v2_0_partial_boundary_rho010_sentencepiece_probe.md
  rho=0.10 intrinsic eval:
    artifacts/v2_0_partial_boundary_rho010_intrinsic_eval.md
  rho=0.10 valid/test tokens/raw byte: 0.158404 / 0.159029
  rho=0.10 bare Challenge F1: 0.7361
  rho=0.10 finite-protected Challenge F1: 0.6750
  rho=0.10 decision:
    compression stayed near SP64, but morphology signal did not materially
    transfer
  rho=0.25 config:
    configs/v2_0_partial_boundary_rho025_sentencepiece.toml
  rho=0.25 view/raw bytes: 1.029451
  rho=0.50 config:
    configs/v2_0_partial_boundary_rho050_sentencepiece.toml
  rho=0.50 view/raw bytes: 1.058956
  rho=0.25 valid/test tokens/raw byte: 0.158458 / 0.159060
  rho=0.25 bare Challenge F1: 0.7380
  rho=0.25 finite-protected Challenge F1: 0.6782
  rho=0.50 valid/test tokens/raw byte: 0.158676 / 0.159231
  rho=0.50 bare Challenge F1: 0.7361
  rho=0.50 finite-protected Challenge F1: 0.6777
  decision:
    close stock SentencePiece partial-boundary branch; compression is safe,
    but morphology transfer is not material
  findings:
    docs/v2_0_partial_boundary_sp_findings.md
post-hoc score-shift probe:
  script: scripts/materialize_v2_score_shifted_sp_model.py
  tests: tests/test_v2_score_shifted_sp_model.py -> 3 passed
  lambda=0.5 materialization:
    artifacts/v2_0_score_shift_lambda05_materialization.md
  lambda=0.5 intrinsic eval:
    artifacts/v2_0_score_shift_lambda05_intrinsic_eval.md
  adjusted pieces: 4878
  alignment failures: 0
  lambda=0.5 bare Challenge F1: 0.7364
  lambda=0.5 finite-protected Challenge F1: 0.6768
  decision:
    do not run tiny-LM; this shallow score-shift is too weak at lambda=0.5
  advisor update:
    docs/advisor_update_v2_0_after_sp_compatible_hacks.md
Fable5 triage after SP-compatible hacks:
  docs/advisor_feedback_v2_0_sp_compatible_hacks_triage.md
SP64 vocab oracle ceiling:
  script: scripts/audit_v2_sp_vocab_oracle_ceiling.py
  report: artifacts/v2_0_sp_vocab_oracle_ceiling_challenge.md
  lambda0 Challenge F1: 0.7422
  no-cross Challenge F1: 0.8407
  oracle-best-F1 Challenge F1: 0.8417
  oracle-best-F1 avg tokens/word: 2.5457
  decision:
    SP64 vocabulary can express better morphology-compatible paths; run one
    cached score-shift sweep before moving to a full custom trainer
score-shift script update:
  supports --stats-out / --stats-in
  supports --penalty-mode rate|mass|hybrid
  supports --min-crossing-count
cached score-shift sweep:
  findings: docs/v2_0_score_shift_sweep_findings.md
  stats cache:
    artifacts/private/v2_0_score_shifted_sp/sp64_crossing_stats.train.json
  lambda sweep: 1, 2, 4, 8
  lambda 1 bare/finite Challenge F1: 0.7351 / 0.6755
  lambda 2 bare/finite Challenge F1: 0.7351 / 0.6755
  lambda 4 bare/finite Challenge F1: 0.7351 / 0.6755
  lambda 8 bare/finite Challenge F1: 0.7364 / 0.6768
  decision:
    close post-hoc score-shift; shallow score patching does not move the
    deployed SP path toward the oracle ceiling
  next:
    boundary-weighted Unigram/EM objective, after bootstrap CI/noise-floor and
    wrapper-tax decomposition
methodology chores completed:
  findings: docs/v2_0_methodology_chore_findings.md
  CI script: scripts/report_v2_sp_model_ci.py
  CI report: artifacts/v2_0_sp_model_ci_challenge_current_frontier.md
  wrapper-tax script: scripts/audit_v2_finite_wrapper_eval_tax.py
  wrapper-tax report: artifacts/v2_0_finite_wrapper_eval_tax_challenge.md
  CI decision:
    SP64 / partial-boundary / score-shift intervals overlap heavily; tiny
    visible F1 deltas are noise
  wrapper-tax decision:
    finite-wrapper F1 loss is concentrated in numeric_like, file_like, and
    apostrophe/hard_suffix routes
  metric decision:
    use bare F1 for normal-text objective development and track finite-wrapper
    tax separately
boundary-weighted Unigram/EM spec:
  docs/v2_0_boundary_weighted_unigram_em_spec.md
  first implementation target:
    SP64 candidate vocab + per-word lattice + forward-backward with
    exp(-lambda * crossings), starting on 2k/5k train-line smoke
boundary-weighted Unigram/EM prototype:
  script: scripts/materialize_v2_boundary_weighted_unigram_em.py
  sweep runner: scripts/run_v2_boundary_weighted_unigram_em_sweep.py
  runbook: docs/v2_0_boundary_weighted_unigram_em_runbook.md
  findings: docs/v2_0_boundary_weighted_unigram_em_findings.md
  advisor follow-up:
    docs/advisor_followup_v2_0_boundary_weighted_unigram_em.md
  tests:
    tests/test_v2_boundary_weighted_unigram_em.py
    tests/test_v2_boundary_weighted_unigram_em_sweep.py
    latest targeted result: 9 passed
  smoke report:
    artifacts/v2_0_boundary_weighted_unigram_em_lambda1_iter1_100lines.md
    artifacts/v2_0_boundary_weighted_unigram_em_lambda0_iter1_100lines.md
  smoke model:
    artifacts/private/v2_0_boundary_weighted_unigram_em/lambda1_iter1_100lines_unigram_64000.model
  smoke result:
    100 train lines, 25486 normal segments, 0 skipped segments,
    15479 expected piece types, 15479 changed scores for both lambda0/lambda1
  smoke CI/eval:
    artifacts/v2_0_boundary_weighted_unigram_em_100lines_ci.md
    artifacts/v2_0_boundary_weighted_unigram_em_lambda1_iter1_100lines_ci.md
    lambda0 bare Challenge F1: 0.7392 [0.7067, 0.7664]
    bare Challenge F1: 0.7404 [0.7081, 0.7664]
    finite Challenge F1: 0.6809 [0.6429, 0.7176]
  interpretation:
    mechanical path is working; this is not yet a quality result. Next run
    should be a controlled lambda0/lambda>0 comparison on 2k or 5k lines.
  2k sweep:
    artifacts/v2_0_boundary_weighted_unigram_em_2000lines_ci.md
    lambda0/lambda1/lambda2/lambda4 bare F1 stayed flat:
      0.7383 / 0.7396 / 0.7396 / 0.7391
    skipped segments: 0
  crossing diagnostic:
    lambda0 avg expected crossings/segment: 0.282770
    lambda4 avg expected crossings/segment: 0.256630
    lambda16 avg expected crossings/segment: 0.018998
  decision:
    boundary penalty is mechanically active, but the current EM score branch
    shows weak transfer. Do not run tiny-LM; ask advisors whether to add
    aligned-piece reward/pruning or pivot to constrained MorphBPE.
Fable5 decisive probes after EM:
  deployed crossing script:
    scripts/audit_v2_deployed_sp_crossings.py
  teacher-distilled script:
    scripts/materialize_v2_teacher_distilled_sp_model.py
  findings:
    docs/v2_0_distilled_score_bound_findings.md
  advisor update:
    docs/advisor_update_v2_0_distilled_score_bound.md
  targeted tests:
    tests/test_v2_deployed_sp_crossings.py
    tests/test_v2_teacher_distilled_sp_model.py
    latest targeted result: 4 passed
  EM 2k deployed crossing:
    SP64 crossed boundaries: 170/305
    EM lambda0/lambda1/lambda2/lambda4 crossed boundaries: 157/305
    decision: lambda does not survive as a useful deployed crossing curve
  teacher-distilled 2k challenge:
    SP64 bare F1/tokens-word: 0.7351 / 2.2010
    distilled bare F1/tokens-word: 0.7447 / 2.5065
    SP64 finite F1/tokens-word: 0.6755 / 2.2977
    distilled finite F1/tokens-word: 0.7179 / 2.5927
  teacher-distilled 2k deployed crossing:
    challenge SP64: 170/305, rate 0.557377
    challenge distilled: 119/305, rate 0.390164
    high-rate attribution: about 95% of challenge crossings from >=0.70-rate pieces
  decision:
    score-only Unigram looks weak, but high-rate crossing attribution means
    targeted inventory/pruning is not killed. Next choice is full 16k
    distilled bound versus one high-rate pruning/inventory probe.
```

## Latest Advisor Correction

Advisor review of the boundary-biased decode result found the key unresolved
control:

```text
boundary_biased lambda 0 is not equivalent to official SentencePiece /
the finite protected floor.
```

Therefore lambda 4 is not promoted as a v2.0 candidate. It is a promising
diagnostic point whose attribution is blocked until the lambda 0 tiny-LM BPB
row and decoder-alignment / roundtrip audits are complete.

Lambda 0 control has now been run:

```text
report: artifacts/v2_0_tiny_lm_marker_calibration_boundary_lambda0_300steps.md
decomposition: artifacts/v2_0_boundary_biased_lambda_decomposition.md
```

Decomposition table:

```text
finite protected numeric-SP floor -> lambda 0:
  test BPB -0.142010, Challenge F1 +0.0509
lambda 0 -> lambda 4:
  test BPB -0.047547, Challenge F1 +0.0279
lambda 4 -> lambda 8:
  test BPB +0.129466, Challenge F1 +0.0524
```

Interpretation: most BPB gain comes from the decoder/pipeline path, but lambda
4 still adds a smaller morphology-boundary gain over lambda 0 in the 300-step
screen.

Roundtrip smoke:

```text
SP64 bare: 20/20 exact
boundary-biased lambda 0: 0/20 exact
boundary-biased lambda 4: 0/20 exact
reports:
  artifacts/v2_0_boundary_encoder_roundtrip_audit_sp64_smoke.md
  artifacts/v2_0_boundary_encoder_roundtrip_audit_smoke.md
```

This is now the blocker. Do not run longer BPB until boundary-biased encode
becomes exact-roundtrip or is demoted to diagnostic-only evidence for a future
training-time objective.

Follow-up advisor review is now stricter:

```text
the runtime boundary-biased decoder branch is demoted from candidate status
to diagnostic status until exact roundtrip is fixed
longer/larger BPB is blocked
the next useful engineering work is roundtrip/root-cause audit plus wrapper-tax
audit on clean no-protected lines
```

New triage:

```text
docs/advisor_feedback_v2_0_lambda0_roundtrip_triage.md
```

New audit:

```text
script: scripts/audit_v2_roundtrip_wrapper_tax.py
report: artifacts/v2_0_roundtrip_wrapper_tax_audit_valid.md
findings: docs/v2_0_roundtrip_wrapper_tax_findings.md
```

New training-time objective smoke:

```text
implementation: src/tr_tokenizer/boundary_weighted_bpe.py
runner: scripts/run_v2_boundary_weighted_bpe_probe.py
findings: docs/v2_0_boundary_weighted_bpe_probe_findings.md
smoke report: artifacts/v2_0_boundary_weighted_bpe_probe_smoke_small.md
```

New advisor request:

```text
docs/advisor_request_v2_0_training_time_objective_choice.md
```

Important additional finding from advisor review:

```text
even no-protected valid lines show a protected-wrapper tax:
  finite/protected floor: about 171.97 tokens
  official SP: about 164.30 tokens
This likely reflects segment-wise encoding / dummy-prefix / boundary handling,
and should be fixed or explained before more morphology-objective work.
```

The audit confirmed this. On the valid split:

```text
SP64 exact roundtrip: 1985/1994
finite protected numeric-SP floor exact roundtrip: 17/1994
boundary-biased lambda0 exact roundtrip: 0/1994
boundary-biased lambda4 exact roundtrip: 0/1994
clean no-protected wrapper tax:
  official SP avg tokens: 164.2955
  finite protected floor avg tokens: 171.9669
```

A quick whitespace-in-segment local fix was tested and reverted. It worsened
token pressure and did not restore roundtrip. Treat this as structural enough
to demote the runtime decoder path unless a cleaner wrapper redesign is chosen.

## Current State

The project has completed enough v1.8 tiny-LM screening and token accounting
audit work to choose the v2.0 direction.

Current next step:

```text
Do not run more BPB and do not promote lambda 4.

Immediate next step:
  1. classify boundary-biased roundtrip failures
  2. audit/reduce protected-wrapper tax on clean no-protected lines
  3. compute normal-text-only morphology F1
  4. decide whether runtime decode gets a short fix attempt or is archived as
     evidence for a boundary-weighted Unigram/constrained training objective
Current recommendation: archive/demote runtime boundary-biased decode as a
candidate path and move the morphology prior into a training-time objective.

Boundary-weighted toy BPE smoke confirms the training-time objective mechanism
is wired correctly: higher lambda reduces morph-boundary-crossing merges. The
quality signal is still weak and the toy trainer is slow, so this is not a
candidate tokenizer. It is an objective sanity check.

Next decision: choose the first real training-time objective. Current leaning is
boundary-weighted Unigram because it is closer to the SP64 baseline and to the
lambda decoder evidence.
```

Most recent decision artifacts:

- [v1.8 tiny-LM smoke findings](v1_8_tiny_lm_bpb_smoke_findings.md)
- [v2.0 hybrid vocabulary plan](v2_0_hybrid_vocab_plan.md)
- [v2.0 roadmap review](v2_0_roadmap_review.md)
- [advisor request for v2.0 hybrid/vocab direction](advisor_update_v2_0_hybrid_vocab_request.md)
- [advisor feedback triage](advisor_feedback_v2_0_triage.md)
- [advisor feedback: protected-aware architecture](advisor_feedback_v2_0_protected_aware_triage.md)
- [v2.0 protected-aware tokenizer spec](v2_0_protected_aware_tokenizer_spec.md)
- [v2.0 tiny-LM finite protected soft-marker findings](v2_0_tiny_lm_finite_protected_soft_marker_findings.md)
- [v2.0 marker-stripped soft-marker findings](v2_0_marker_stripped_soft_marker_findings.md)
- [v2.0 train-only marker findings](v2_0_train_only_marker_findings.md)
- [v2.0 selective soft-marker plan](v2_0_selective_soft_marker_plan.md)
- [advisor request: v2.0 selective soft-marker direction](advisor_request_v2_0_selective_soft_marker.md)
- [advisor request: v2.0 train-only marker frontier](advisor_request_v2_0_train_only_marker_frontier.md)
- [v2.0 tiny-LM marker calibration results](../artifacts/v2_0_tiny_lm_marker_calibration_results.md)
- [v2.0 morph seed vocabulary plan](v2_0_morph_seed_vocab_plan.md)
- [v2.0 finite protected wrapper cost findings](v2_0_finite_protected_wrapper_cost_findings.md)
- [v2.0 non-Turkish Latin route quality findings](v2_0_non_turkish_latin_route_quality_findings.md)
- [v2.0 Turkish loan-diacritic pass-through findings](v2_0_turkish_loan_diacritic_pass_findings.md)
- [v2.0 protected route cost reduction findings](v2_0_protected_route_cost_reduction_findings.md)
- [v2.0 numeric protected encoder what-if findings](v2_0_numeric_protected_encoder_whatif_findings.md)
- [v2.0 morph vocabulary coverage findings](v2_0_morph_vocab_coverage_findings.md)
- [v2.0 boundary-biased Unigram findings](v2_0_boundary_biased_unigram_findings.md)
- [advisor feedback: lambda0 roundtrip triage](advisor_feedback_v2_0_lambda0_roundtrip_triage.md)
- [v2.0 roundtrip and wrapper tax findings](v2_0_roundtrip_wrapper_tax_findings.md)
- [v2.0 boundary-weighted BPE probe findings](v2_0_boundary_weighted_bpe_probe_findings.md)
- [advisor request: v2.0 training-time objective choice](advisor_request_v2_0_training_time_objective_choice.md)

Current v2.0 diagnostic result:

```text
active protected floor: finite_protected_sp64_numeric_sp_floor
floor valid/test tokens/raw byte without EOS: 0.171202 / 0.172015
floor Challenge F1: 0.6913
boundary-biased lambda 4 valid/test tokens/raw byte without EOS: 0.163313 / 0.163968
boundary-biased lambda 4 Challenge F1: 0.7701
boundary-biased lambda 8 valid/test tokens/raw byte without EOS: 0.178023 / 0.178580
boundary-biased lambda 8 Challenge F1: 0.8225
boundary-biased lambda 0 tiny-LM valid/test BPB: 4.726285 / 4.769027
boundary-biased lambda 4 tiny-LM valid/test BPB: 4.686700 / 4.721480
boundary-biased lambda 8 tiny-LM valid/test BPB: 4.816592 / 4.850946
SP64 tiny-LM valid/test BPB: 4.827723 / 4.860352
finite protected numeric-SP floor tiny-LM valid/test BPB: 4.875198 / 4.911037
protected stress: 25/25 for all tested boundary-biased rows
decision: do not return to marker-dose, seed appendix, or broad UDS
decision: lambda 4 is a diagnostic row only, not a tokenizer candidate, because
the boundary-biased runtime path currently fails exact roundtrip
decision: lambda 8 is high-F1 and still BPB-positive vs SP64, but lambda 4 is
the lower-pressure diagnostic point
next: no longer BPB; classify roundtrip failures and wrapper tax first. If the
fix is non-trivial, demote runtime decode and move the morphology signal into a
training-time objective.
```

v1.8 key result:

```text
fixed-token / fixed-step view: SP wins
approx iso-byte view: custom wins, but not iso-compute
decision: do not hand pure custom to LLM team as default
decision: do not discard morphology-aware tokenization
next: v2.0 hybrid/vocabulary prototype
```

Token-accounting audit result:

```text
standard custom is close to SP64 in token pressure
lossless custom is much more expensive
lossless+64k byte fallback is about 2.66x-2.67x SP64 tokens/byte on valid/test
report: artifacts/v1_8_token_accounting_audit.md
```

Current script:

```text
scripts/materialize_v2_soft_morph_artifacts.py
scripts/analyze_v2_seed_vocab.py
scripts/select_v2_seed_policy.py
scripts/materialize_v2_candidate_serialization.py
scripts/materialize_v2_candidate_split_views.py
scripts/run_v2_candidate_sentencepiece_probe.py
scripts/materialize_v2_raw_hard_candidate_views.py
scripts/evaluate_v2_raw_hard_candidate_intrinsic.py
scripts/materialize_v2_raw_soft_marker_candidate_views.py
scripts/evaluate_v2_soft_marker_candidate_intrinsic.py
scripts/materialize_v2_protected_routes.py
scripts/analyze_v2_protected_route_inventory.py
scripts/select_v2_protected_piece_vocab.py
scripts/evaluate_v2_protected_encoder.py
scripts/evaluate_v2_finite_protected_sp64_intrinsic.py
scripts/evaluate_v2_finite_protected_soft_marker_intrinsic.py
scripts/measure_v2_finite_protected_soft_marker_pressure.py
scripts/materialize_v2_train_only_marker_views.py
scripts/analyze_v2_morph_seed_candidates.py
scripts/select_v2_morph_seed_policy.py
scripts/materialize_v2_morph_seed_augmented_view.py
```

Current finding:

```text
64k seed cap covers 95.34% of non-whitespace custom seed occurrences
suffix inventory is small: 244 unique suffix tokens, 925856 occurrences
remaining pressure is mostly word_start long-tail + whitespace serialization
docs/v2_0_soft_morph_seed_findings.md
```

Current seed policy:

```text
protected_hard_soft_morph_seeded_sp64
budget: 64000
selected coverage: 95.11%
suffix selected: 244 unique / 925856 occurrences
protected selected: 944 unique / 51231 occurrences, count >= 10
word_start selected: 62560 unique / 2284533 occurrences
report: artifacts/v2_0_seed_policy_selection.md
```

Current roadmap phase:

```text
Phase 3: raw-hard candidate passed compression but failed visible intrinsic gate
report: artifacts/v2_0_candidate_serialization.md
valid/test report: artifacts/v2_0_candidate_split_views.md
failed SP probe: artifacts/v2_0_candidate_sentencepiece_probe.md
raw-hard view report: artifacts/v2_0_raw_hard_candidate_views.md
raw-hard SP probe: artifacts/v2_0_raw_hard_candidate_sentencepiece_probe.md
raw-hard intrinsic eval: artifacts/v2_0_raw_hard_candidate_intrinsic_eval.md
hard segments/raw byte: 0.130918
train-view/raw bytes: 1.511092
valid hard segments/raw byte: 0.130737
test hard segments/raw byte: 0.130560
failed candidate valid/test SP tokens/raw byte: 0.398475 / 0.397593
raw-hard candidate valid/test SP tokens/raw byte: 0.162884 / 0.163117
raw-hard challenge boundary F1: 0.5951
SP64 challenge boundary F1: 0.7351
raw-hard protected span preservation: 1/25
SP64 baseline valid/test tokens/raw byte: about 0.1566 / 0.1570
pure custom lossless+64k valid/test tokens/raw byte: about 0.4162 / 0.4194
decision: do not run tiny-LM on protected_hard_soft_morph_seeded_sp64
decision: do not run tiny-LM on protected_hard_raw_sp64
next gate: design a candidate that preserves protected spans and improves
visible boundary F1 without returning to pure custom token pressure
next candidate: protected_hard_soft_marker_raw_sp64
soft-marker SP probe: artifacts/v2_0_raw_soft_marker_candidate_sentencepiece_probe.md
soft-marker intrinsic eval: artifacts/v2_0_raw_soft_marker_candidate_intrinsic_eval.md
soft-marker valid/test SP tokens/raw byte: 0.236749 / 0.236700
soft-marker challenge boundary F1: 0.6724
soft-marker protected span preservation: 1/25
protected-aware upper-bound challenge boundary F1: 0.8259
protected-aware upper-bound protected span preservation: 25/25
decision: do not run tiny-LM on protected_hard_soft_marker_raw_sp64
decision: protected-aware routing is necessary, but open-vocab protected tokens
are not final LLM-safe
advisor decision: use the Option 1 + Option 3 hybrid
LLM-safe invariant: decode(ids) must be stateless
rejected: placeholder + payload side-channel decoding
next gate: write finite protected-aware encoding/fallback spec before tiny-LM
spec: docs/v2_0_protected_aware_tokenizer_spec.md
protected route report: artifacts/v2_0_protected_route_inventory_analysis.md
decision: UDS cannot be the main protected solution; use finite protected
subword pieces plus byte fallback
protected piece report: artifacts/v2_0_protected_piece_vocab_selection.md
selected finite protected pieces: 374 + 256 byte fallback pieces
protected encoder report: artifacts/v2_0_protected_encoder_diagnostic.md
protected encoder byte fallback byte rate: 0.002679 overall
decision: finite protected-piece path is viable for a full tokenizer prototype
finite protected + SP64 report: artifacts/v2_0_finite_protected_sp64_intrinsic_eval.md
finite protected + SP64 protected stress: 25/25
finite protected + SP64 challenge F1: 0.6913, below SP64 0.7351
decision: plain SP64 normal text is not enough; next use soft-morph prior
finite protected + soft-marker report: artifacts/v2_0_finite_protected_soft_marker_intrinsic_eval.md
finite protected + soft-marker protected stress: 25/25
finite protected + soft-marker challenge F1: 0.8259
decision: intrinsic morphology/protection gate passes
token pressure report: artifacts/v2_0_finite_protected_soft_marker_token_pressure.md
finite protected + soft-marker valid/test model tokens/raw byte: 0.249142 / 0.249758
SP64 baseline valid/test tokens/raw byte: about 0.1566 / 0.1570
raw-soft-marker candidate valid/test tokens/raw byte: about 0.2367 / 0.2367
pure custom lossless+64k valid/test tokens/raw byte: about 0.4162 / 0.4194
decision: token pressure is much closer to raw-soft-marker than pure custom,
but still materially above SP64
tiny-LM dry-run config: configs/v2_0_tiny_lm_finite_protected_soft_marker_probe.toml
tiny-LM dry-run report: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_dry_run.md
tiny-LM dry-run candidate valid/test tokens/raw byte: 0.251658 / 0.252212
tiny-LM dry-run SP64 valid/test tokens/raw byte: 0.159020 / 0.159620
tiny-LM 200-step report: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_200steps.md
tiny-LM finite 321-step iso-byte report: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_finite_321_iso_byte.md
tiny-LM SP64 321-step control: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_sp64_321steps.md
tiny-LM findings: docs/v2_0_tiny_lm_finite_protected_soft_marker_findings.md
fixed-token 200-step test BPB: finite=7.067777, SP64=5.966637
approx iso-byte test BPB: finite_321=5.263920 vs SP64_200=5.966637
same-step 321-step test BPB: finite=5.263920, SP64=4.629442
decision: fixed-token/same-step views favor SP64; approximate iso-byte view
shows useful morphology/protection signal, but current candidate is too
token-expensive for handoff or larger LM probes
next gate: redesign toward lower token pressure while keeping protected-span
and boundary gains
selective marker plan: docs/v2_0_selective_soft_marker_plan.md
advisor request: docs/advisor_request_v2_0_selective_soft_marker.md
marker-stripped diagnostic report: artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md
marker-stripped findings: docs/v2_0_marker_stripped_soft_marker_findings.md
marker-stripped valid/test tokens/raw byte: 0.195611 / 0.196236
marker-stripped challenge F1: 0.7703
marker-stripped protected stress: 25/25
decision: in-stream marker cost is a major bottleneck; prioritize train-only
vocab shaping / constrained-Unigram style experiments before any more tiny-LM
train-only marker materializer: scripts/materialize_v2_train_only_marker_views.py
suffix-chain2 valid-only smoke: artifacts/v2_0_train_only_marker_views_suffix_chain2_smoke.md
suffix-chain2 valid view/raw bytes: 1.086996
suffix-chain2 valid marker keep rate: 0.559449
full suffix-chain2 view report: artifacts/v2_0_train_only_marker_views_suffix_chain2.md
suffix-chain2 SP probe: artifacts/v2_0_train_only_suffix_chain2_sentencepiece_probe.md
suffix-chain2 marker-stripped diagnostic: artifacts/v2_0_train_only_suffix_chain2_marker_stripped_diagnostic.md
suffix-chain2 valid/test tokens/raw byte: 0.183799 / 0.184619
suffix-chain2 challenge F1: 0.7632
high-value suffix view report: artifacts/v2_0_train_only_marker_views_high_value_suffix.md
high-value suffix SP probe: artifacts/v2_0_train_only_high_value_suffix_sentencepiece_probe.md
high-value suffix diagnostic: artifacts/v2_0_train_only_high_value_suffix_marker_stripped_diagnostic.md
high-value valid/test tokens/raw byte: 0.190346 / 0.191068
high-value challenge F1: 0.7665
frontier report: artifacts/v2_0_train_only_marker_frontier.md
findings: docs/v2_0_train_only_marker_findings.md
marker vocab audit: artifacts/v2_0_sentencepiece_marker_vocab_audit.md
marker audit decision: no marker+surface vocab artifact found; each train-only
marker model learned only the standalone U+E000 marker
frontier CI report: artifacts/v2_0_train_only_marker_frontier_ci.md
frontier CI decision: train-only marker F1 intervals overlap heavily; do not
rank all-soft/suffix-chain2/high-value by tiny point differences
decision: stop marker-dose tuning; next choose between calibrated BPB on
bracketing candidates or a genuinely different seed-vocab/morph-piece mechanism
tiny-LM marker calibration config: configs/v2_0_tiny_lm_marker_calibration.toml
tiny-LM marker calibration plan: docs/v2_0_tiny_lm_marker_calibration_plan.md
new tiny-LM kind: finite_protected_marker_stripped
suffix-chain2 tiny-LM dry-run smoke: artifacts/v2_0_tiny_lm_marker_calibration_suffix_chain2_dry_run.md
full tiny-LM marker dry-run: artifacts/v2_0_tiny_lm_marker_calibration_dry_run.md
full dry-run valid/test tokens/raw byte:
  sp64: 0.159020 / 0.159620
  finite_protected_sp64_floor: 0.182112 / 0.183362
  suffix_chain2: 0.184500 / 0.185337
  all_soft: 0.196313 / 0.196954
decision: dry-run passed; next run short per-tokenizer BPB probes in the fixed
calibration order, not all at once
tiny-LM marker calibration results: artifacts/v2_0_tiny_lm_marker_calibration_results.md
300-step test BPB:
  sp64: 4.860352
  finite_protected_sp64_floor: 4.976850
  suffix_chain2_marker_stripped: 5.094965
  all_soft_marker_stripped: 5.157444
decision: marker shaping improved visible F1 but worsened BPB versus the true
protected floor; stop marker-dose tuning
next: selected morph seed vocabulary / curated morph pieces / constrained
Unigram or MorphBPE-style mechanism
morph seed plan: docs/v2_0_morph_seed_vocab_plan.md
morph seed candidate analyzer: scripts/analyze_v2_morph_seed_candidates.py
morph seed policy selector: scripts/select_v2_morph_seed_policy.py
candidate analysis user-run command:
  python scripts\analyze_v2_morph_seed_candidates.py --progress 1000
next user-run command:
  python scripts\select_v2_morph_seed_policy.py
morph seed policy result: artifacts/v2_0_morph_seed_policy_selection.md
morph seed policy findings: docs/v2_0_morph_seed_policy_findings.md
selected unique: 107
selected occurrence share: 0.962466
decision: first prototype should use seed_bias as a learned-vocab prior, not
broad user-defined symbols
morph seed augmented-view script: scripts/materialize_v2_morph_seed_augmented_view.py
morph seed SP config: configs/v2_0_morph_seed_bias_sentencepiece.toml
morph seed bias findings: docs/v2_0_morph_seed_bias_findings.md
augmentation report: artifacts/v2_0_morph_seed_augmented_view.md
SP probe report: artifacts/v2_0_morph_seed_bias_sentencepiece_probe.md
augmentation bytes/base byte: 0.000022
morph_seed_bias valid/test tokens/raw byte: 0.158312 / 0.158901
decision: token-pressure gate passed; run finite-protected intrinsic eval next
morph seed bias intrinsic report: artifacts/v2_0_morph_seed_bias_finite_protected_intrinsic_eval.md
morph seed bias intrinsic findings: docs/v2_0_morph_seed_bias_intrinsic_findings.md
challenge F1, finite protected + morph_seed_bias: 0.6913
protected stress: 25/25
decision: no tiny-LM; weak appendix did not move morphology F1
strong seed-bias reports:
  artifacts/v2_0_morph_seed_bias_strong_augmented_view.md
  artifacts/v2_0_morph_seed_bias_strong_sentencepiece_probe.md
  artifacts/v2_0_morph_seed_bias_strong_finite_protected_intrinsic_eval.md
strong valid/test tokens/raw byte: 0.158315 / 0.158913
strong challenge F1, finite protected: 0.6918
decision: stop simple morph-seed appendix branch; keep finite protected routing
and move to a more structural mechanism
safe UDS plan: docs/v2_0_safe_uds_plan.md
safe UDS materializer: scripts/materialize_v2_safe_uds_symbols.py
safe UDS symbols report: artifacts/v2_0_safe_uds_symbols.md
safe UDS SP config: configs/v2_0_safe_uds_sentencepiece.toml
safe UDS selected symbols: 7
safe UDS SP report: artifacts/v2_0_safe_uds_sentencepiece_probe.md
safe UDS intrinsic report: artifacts/v2_0_safe_uds_finite_protected_intrinsic_eval.md
safe UDS findings: docs/v2_0_safe_uds_findings.md
safe UDS valid/test tokens/raw byte: 0.159109 / 0.159684
safe UDS challenge F1, bare: 0.7556
safe UDS challenge F1, finite protected: 0.7081
safe UDS protected stress, finite protected: 25/25
decision: safe UDS is the current best cheap structural morphology prior, but
not enough for tiny-LM or LLM handoff
expanded UDS22 plan: docs/v2_0_expanded_uds22_plan.md
expanded UDS22 materializer: scripts/materialize_v2_expanded_uds_symbols.py
expanded UDS22 symbols report: artifacts/v2_0_expanded_uds22_symbols.md
expanded UDS22 SP config: configs/v2_0_expanded_uds22_sentencepiece.toml
expanded UDS22 selected symbols: 22
expanded UDS22 SP report: artifacts/v2_0_expanded_uds22_sentencepiece_probe.md
expanded UDS22 findings: docs/v2_0_expanded_uds22_findings.md
expanded UDS22 valid/test tokens/raw byte: 0.183675 / 0.184059
decision: expanded UDS22 failed token-pressure gate; no intrinsic eval
decision: stop UDS expansion; keep safe UDS7 as best cheap structural prior
Fable5 advisor triage: docs/advisor_response_fable5_triage.md
finite protected wrapper cost audit:
  report: artifacts/v2_0_finite_protected_wrapper_cost_audit.md
  findings: docs/v2_0_finite_protected_wrapper_cost_findings.md
  test SP64 tokens/raw byte: 0.159620
  test finite protected tokens/raw byte: 0.183362
  test relative delta: 14.87%
  test protected bytes share: 2.67%
  highest route deltas:
    numeric_like: +137807 protected-vs-SP tokens on same surfaces
    file_like: +120580
    non_turkish_latin_word: +94661
    apostrophe_surface: +51203
  private top-delta examples show Turkish rows with legacy encoding artifacts
    such as ý/þ/ð/Ý, causing non_turkish_latin_word over-routing
non-Turkish Latin route quality audit:
  report: artifacts/v2_0_non_turkish_latin_route_quality_audit.md
  findings: docs/v2_0_non_turkish_latin_route_quality_findings.md
  route occurrences: 18984
  turkish_loan_diacritic: 17333 occurrences / 91.30%
  other_non_turkish_latin: 960 / 5.06%
  legacy_turkish_encoding_artifact: 691 / 3.64%
Turkish loan-diacritic pass-through:
  findings: docs/v2_0_turkish_loan_diacritic_pass_findings.md
  after route occurrences: 1644
  test finite protected tokens/raw byte: 0.183362 -> 0.180564
  relative delta over SP64: 14.87% -> 13.12%
  protected stress after change: 25/25
  challenge F1 after change: 0.6913
protected route cost reduction:
  findings: docs/v2_0_protected_route_cost_reduction_findings.md
  latest report: artifacts/v2_0_finite_protected_wrapper_cost_audit_after_file_glue_pass.md
  test finite protected tokens/raw byte: 0.180564 -> 0.177726
  relative delta over SP64: 13.12% -> 11.34%
  apostrophe_surface delta after route fixes: +20662
  file_like delta after route fixes: +72043
  numeric_like remains the largest route cost: +137885
  protected stress after route fixes: 25/25
  challenge F1 after route fixes: 0.6913
numeric protected encoder what-if:
  findings: docs/v2_0_numeric_protected_encoder_whatif_findings.md
  report: artifacts/v2_0_numeric_protected_encoder_whatif.md
  dry-run: artifacts/v2_0_tiny_lm_marker_calibration_numeric_sp_dry_run.md
  300-step report: artifacts/v2_0_tiny_lm_marker_calibration_numeric_sp_300steps.md
  finite protected after route fixes test tokens/raw byte: 0.177726
  numeric-SP protected floor test tokens/raw byte: 0.172734
  digit2 finite numeric codec what-if test tokens/raw byte: 0.175069
  numeric-SP protected floor test BPB: 4.911037
  current finite_protected_sp64_floor test BPB: 4.939361
  old finite_protected_sp64_floor test BPB: 4.976850
  decision: promote numeric-SP as the active protected floor for experiments,
    while keeping final numeric codec design open
morph vocabulary coverage:
  findings: docs/v2_0_morph_vocab_coverage_findings.md
  report: artifacts/v2_0_morph_vocab_coverage.md
  SP64 exact-piece occurrence share: 0.963019
  safe UDS7 exact-piece occurrence share: 0.962751
  decision: morph surface vocabulary coverage is not the main bottleneck;
    next test decode-time boundary preference
updated decision:
  do not build constrained/MorphBPE yet
  finite protected wrapper cost has been reduced and numeric-SP promoted as
    active protected floor
  morph surface vocab coverage is high, so broad UDS/seed expansion is not the
    next lever
  next test decode-time boundary-biased Unigram/Viterbi lambda sweep
next implementation:
  boundary-biased Viterbi sweep only after coverage tells us it is meaningful
```

Completed:

- v1.6b Batch 1: technical comparator/package span guard:
  - `transformers>=4.40 -> ▁transformers>=4.40`
  - `tokenizers>=0.19 -> ▁tokenizers>=0.19`
- v1.6b Batch 2: Arabic/Greek script word fallback:
  - `مرحبا بالعالم. -> ▁مرحبا ▁بالعالم .`
  - `Αθήνα είναι όμορφη πόλη. -> ▁Αθήνα ▁είναι ▁όμορφη ▁πόλη .`
- v1.6b Batch 3: English/European apostrophe guard:
  - `Don't -> ▁Don't`
  - `John's -> ▁John's`
  - `L'amico -> ▁L'amico`
- v1.6b Batch 4: non-Turkish Latin word guard:
  - `Straße -> ▁Straße`
  - `niño -> ▁niño`
  - `all'università -> ▁all'università`
- v1.6b R3 Azerbaijani routing decision:
  - no v1.6b behavior change
  - documented as a known limitation
  - deferred to v2.0 router/MorphBPE planning
- v1.4 Batch 1: protected exact lexical items `peki` and `yeni`.
- v1.4 Batch 2: guarded possessive-buffered-ablative split:
  - `sından -> +sı +ndan`
  - `sinden -> +si +nden`
  - `sundan -> +su +ndan`
  - `sünden -> +sü +nden`

Current verified metrics:

```text
python -m pytest
122 passed

tr_gold_expanded.tsv
exact_match: 50/50
f1: 1.0000

tr_challenge.tsv
exact_match: 44/108
f1: 0.8255

proper_name
exact_match: 9/9
f1: 1.0000

tr_stress_public.tsv
roundtrip_exact: 34/34
protected_spans_preserved: 25/25

en_smoke.tsv
exact_match: 8/10
f1: 0.8889

multilingual_smoke.tsv
exact_match: 17/20
f1: 0.9404
```

After v1.5 baseline infrastructure:

```text
python -m pytest
91 passed

expanded real-baseline report
custom_tr_morph boundary_f1: 1.0000, exact_match: 50/50
unicode_char boundary_f1: 0.4947, exact_match: 0/50

challenge real-baseline report
custom_tr_morph boundary_f1: 0.9220, exact_match: 44/108
unicode_char boundary_f1: 0.4949, exact_match: 0/108

public stress report
roundtrip_exact: 28/28
protected_spans_preserved: 23/23
```

After local SentencePiece demo baselines:

```text
expanded real-baseline report
custom_tr_morph: avg_tokens/word=2.7438, boundary_f1=1.0000
sp_bpe:          avg_tokens/word=2.7273, boundary_f1=0.6263
sp_unigram:      avg_tokens/word=3.0744, boundary_f1=0.6325

challenge real-baseline report
custom_tr_morph: avg_tokens/word=2.1749, boundary_f1=0.9220
sp_bpe:          avg_tokens/word=2.7807, boundary_f1=0.6497
sp_unigram:      avg_tokens/word=2.9321, boundary_f1=0.6225
```

After local CELIK_AI SentencePiece pilot baselines:

```text
pilot corpus
lines written: 75,388
size: ~132 MB
visible leakage hits: 0 exact, 0 normalized, 0 8-gram

expanded visible eval
custom_tr_morph:              avg_tokens/word=2.7438, boundary_f1=1.0000
sp_bpe_4000_celik_pilot:      avg_tokens/word=3.3058, boundary_f1=0.6614
sp_unigram_4000_celik_pilot:  avg_tokens/word=3.2810, boundary_f1=0.7091
sp_bpe_8000_celik_pilot:      avg_tokens/word=2.9008, boundary_f1=0.6792
sp_unigram_8000_celik_pilot:  avg_tokens/word=2.9917, boundary_f1=0.7441

challenge visible eval
custom_tr_morph:              avg_tokens/word=2.1749, boundary_f1=0.9220
sp_bpe_4000_celik_pilot:      avg_tokens/word=3.0183, boundary_f1=0.6480
sp_unigram_4000_celik_pilot:  avg_tokens/word=3.0131, boundary_f1=0.6961
sp_bpe_8000_celik_pilot:      avg_tokens/word=2.5692, boundary_f1=0.6714
sp_unigram_8000_celik_pilot:  avg_tokens/word=2.5666, boundary_f1=0.7405
```

After deprecated raw `celik_gold_corpus.jsonl` 100k quality audit:

```text
copied source:
data/train/private/celik_ai/archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl

audit report:
artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md

scanned lines: 100,000
valid JSON: 100,000
missing/empty text: 0
exact duplicates in scan: 0
normalized duplicates in scan: 0
tr_like heuristic: 84.38%
mixed_tr_en heuristic: 15.47%
latin script heuristic: 99.998%
chars > 4,192: 1.58%
chars > 20,000: 0.46%
mojibake suspects: 0.03%
replacement-char texts: 0.003%
control-char texts: 0.71%
```

After deprecated raw `celik_gold_corpus.jsonl` pilot sample:

```text
config:
configs/v1_7_celik_gold_filtered_sample.toml

output:
data/train/claim_grade/celik_gold_filtered_pilot.txt

scanned rows: 120001
usable text rows: 120000
filtered rows: 7779
duplicate rows: 11
written rows: 100000
visible leakage hits: 0 exact, 0 normalized, 0 8-gram

filter details:
short: 4329
long chars: 2466
long UTF-8 bytes: 217
control chars: 744
replacement chars: 2
mojibake suspects: 21
normalized duplicates: 11
```

After filtered CELIK gold SentencePiece pilot baselines:

```text
config:
configs/v1_7_celik_gold_sentencepiece_pilot_sweep.toml

SentencePiece loaded all 100000 filtered sentences.

expanded visible eval
custom_tr_morph:                   avg_tokens/word=2.7438, boundary_f1=1.0000
sp_bpe_4000_celik_gold_pilot:      avg_tokens/word=3.3058, boundary_f1=0.6424
sp_unigram_4000_celik_gold_pilot:  avg_tokens/word=3.3719, boundary_f1=0.7125
sp_bpe_8000_celik_gold_pilot:      avg_tokens/word=2.9669, boundary_f1=0.6633
sp_unigram_8000_celik_gold_pilot:  avg_tokens/word=2.9669, boundary_f1=0.7445

challenge visible eval
custom_tr_morph:                   avg_tokens/word=2.1749, boundary_f1=0.9220
sp_bpe_4000_celik_gold_pilot:      avg_tokens/word=2.9347, boundary_f1=0.6506
sp_unigram_4000_celik_gold_pilot:  avg_tokens/word=3.0052, boundary_f1=0.7101
sp_bpe_8000_celik_gold_pilot:      avg_tokens/word=2.5770, boundary_f1=0.6690
sp_unigram_8000_celik_gold_pilot:  avg_tokens/word=2.5979, boundary_f1=0.7388
```

After clean CELIK gold corpus copy and SentencePiece sweep:

```text
private copied source:
data/train/private/celik_ai/celik_gold_corpus.clean.jsonl

config:
configs/v1_7_celik_gold_clean_sample.toml
configs/v1_7_celik_gold_clean_sentencepiece_sweep.toml

sample:
scanned rows: 120001
usable text rows: 120000
filtered rows: 7737
duplicates: 11
written rows: 100000
visible leakage hits: 0 exact, 0 normalized, 0 8-gram
direct eval leakage on SP training pilot:
  raw exact: 0 gold, 0 challenge
  strict normalized full (>=3 words): 0 gold, 0 challenge
  partial 8-gram: 0 gold, 0 challenge
  short_full: 9 gold one-word examples, 0 challenge
  report: artifacts/v1_7_celik_gold_clean_pilot_eval_leakage_report.md
  scope: actual 100k SP training pilot, not the full 13 GB source JSONL

SentencePiece loaded all 100000 filtered sentences.

expanded visible eval
custom_tr_morph:                    avg_tokens/word=2.7438, boundary_f1=1.0000
sp_bpe_8000_celik_gold_clean:       avg_tokens/word=2.9669, boundary_f1=0.6633
sp_unigram_8000_celik_gold_clean:   avg_tokens/word=2.9669, boundary_f1=0.7377
sp_bpe_16000_celik_gold_clean:      avg_tokens/word=2.6694, boundary_f1=0.6919
sp_unigram_16000_celik_gold_clean:  avg_tokens/word=2.7355, boundary_f1=0.7425

challenge visible eval
custom_tr_morph:                    avg_tokens/word=2.1749, boundary_f1=0.9220
sp_bpe_8000_celik_gold_clean:       avg_tokens/word=2.5770, boundary_f1=0.6690
sp_unigram_8000_celik_gold_clean:   avg_tokens/word=2.5953, boundary_f1=0.7369
sp_bpe_16000_celik_gold_clean:      avg_tokens/word=2.3446, boundary_f1=0.6837
sp_unigram_16000_celik_gold_clean:  avg_tokens/word=2.3995, boundary_f1=0.7340
```

After downstream probe prep skeleton:

```text
script:
scripts/prepare_downstream_probe.py

demo config/report:
configs/v1_7_downstream_probe_demo.toml
artifacts/v1_7_downstream_probe_prep_demo.md

CELIK gold pilot config/report:
configs/v1_7_downstream_probe_celik_gold_pilot.toml
artifacts/v1_7_downstream_probe_prep_celik_gold_pilot.md

private token JSONL output:
artifacts/private/v1_7_downstream_probe/

CELIK gold pilot split:
train: 16000 lines, 21.68 MiB, 2592338 words
valid: 2000 lines, 2.73 MiB, 325698 words
test:  2000 lines, 2.71 MiB, 324637 words

valid avg tokens/word:
custom_tr_morph:                  1.4922
sp_bpe_8000_celik_gold_pilot:     1.9342
sp_unigram_8000_celik_gold_pilot: 1.8876
unicode_char:                     7.0537

test avg tokens/word:
custom_tr_morph:                  1.4935
sp_bpe_8000_celik_gold_pilot:     1.9292
sp_unigram_8000_celik_gold_pilot: 1.8824
unicode_char:                     7.0491
```

After Qwen tokenizer reference:

```text
expanded all-baseline report
custom_tr_morph: avg_tokens/word=2.7438, boundary_f1=1.0000
toy_bpe_1000:    avg_tokens/word=2.7438, boundary_f1=0.6277
sp_bpe:          avg_tokens/word=2.7273, boundary_f1=0.6263
sp_unigram:      avg_tokens/word=3.0744, boundary_f1=0.6325
qwen:            avg_tokens/word=3.0661, boundary_f1=0.3317

challenge all-baseline report
custom_tr_morph: avg_tokens/word=2.1749, boundary_f1=0.9220
toy_bpe_1000:    avg_tokens/word=2.7572, boundary_f1=0.6610
sp_bpe:          avg_tokens/word=2.7807, boundary_f1=0.6497
sp_unigram:      avg_tokens/word=2.9321, boundary_f1=0.6225
qwen:            avg_tokens/word=2.8590, boundary_f1=0.3511
```

After Mistral tokenizer reference:

```text
expanded all-baseline report
custom_tr_morph: avg_tokens/word=2.7438, boundary_f1=1.0000
mistral:         avg_tokens/word=4.3306, boundary_f1=0.5423

challenge all-baseline report
custom_tr_morph: avg_tokens/word=2.1749, boundary_f1=0.9220
mistral:         avg_tokens/word=3.9426, boundary_f1=0.5463
```

LLaMA reference result:

```text
model_id: meta-llama/Llama-3.2-1B
status: ok
expanded:  avg_tokens/word=2.9008, boundary_f1=0.3259
challenge: avg_tokens/word=2.5744, boundary_f1=0.3501
reports:
  artifacts/v1_5_llama_report_expanded.md
  artifacts/v1_5_llama_report_challenge.md
```

English smoke result:

```text
dataset: data/eval/en_smoke.tsv
custom_tr_morph exact_match: 5/10
custom_tr_morph boundary_f1: 0.7949
custom_tr_morph avg_tokens/word: 1.2692
report: artifacts/v1_5_real_tokenizer_report_english_smoke.md
findings: docs/v1_5_english_smoke_findings.md
```

Multilingual smoke result:

```text
dataset: data/eval/multilingual_smoke.tsv
custom_tr_morph exact_match: 8/20
custom_tr_morph boundary_f1: 0.6775
custom_tr_morph avg_tokens/word: 2.8493
report: artifacts/v1_5_real_tokenizer_report_multilingual_smoke.md
findings: docs/v1_5_multilingual_smoke_findings.md
```

After v1.6a bootstrap confidence intervals:

```text
python -m pytest
95 passed

tr_gold_expanded.tsv
custom_tr_morph exact_match_rate: 1.0000 [1.0000, 1.0000]
custom_tr_morph boundary_f1:      1.0000 [1.0000, 1.0000]
custom_tr_morph avg_tokens/word:  2.7438 [2.4542, 3.1402]

tr_challenge.tsv
custom_tr_morph exact_match_rate: 0.4074 [0.3056, 0.5093]
custom_tr_morph boundary_f1:      0.9220 [0.9043, 0.9382]
custom_tr_morph avg_tokens/word:  2.1749 [2.0544, 2.3080]

reports:
  artifacts/v1_6_ci_expanded.md
  artifacts/v1_6_ci_challenge.md
  artifacts/v1_6_ci_all_expanded.md
  artifacts/v1_6_ci_all_challenge.md
  artifacts/v1_6_ci_all_en_smoke.md
  artifacts/v1_6_ci_all_multilingual_smoke.md
  docs/v1_6_confidence_interval_findings.md
```

After v1.6a protected-span baseline metrics:

```text
data/eval/tr_stress_public.tsv
custom_tr_morph protected_preserved: 23/23
custom_tr_morph protected_broken:    0
custom_tr_morph break_rate:          0.0000

all-baseline report:
  artifacts/v1_6_protected_span_report_stress.md
  docs/v1_6_protected_span_findings.md
```

After v1.6a natural/demo corpus fertility report:

```text
data/train/tr_bpe_train.txt
lines: 310
words: 1326

custom_tr_morph avg_tokens/word: 1.9419
toy_bpe_1000 avg_tokens/word:    2.1953
sp_bpe avg_tokens/word:          2.2097
sp_unigram avg_tokens/word:      2.4555
llama avg_tokens/word:           2.5505
qwen avg_tokens/word:            2.8190
mistral avg_tokens/word:         3.9306

custom_tr_morph protected candidates: 16/16
report:
  artifacts/v1_6_fertility_report_demo_corpus.md
  docs/v1_6_fertility_findings.md
```

## Do Not Forget

The next step is not to blindly continue adding challenge-set rules.

S2-S5 remain on hold:

- S2 `başladı` common verb split
- S3 `satırı` object-case stem
- S4a `tarihinde`
- S4b `yazıldı`
- S5 `yapma`

These require separate decisions and tests.

## Completed Measurement Track

v1.5 and v1.6a baseline/measurement work is complete enough to start a narrow
v1.6b guard batch.

Completed evidence:

```text
token budget
boundary F1
confidence intervals
protected span integrity
natural/demo corpus fertility
English/multilingual smoke observations
```

Primary findings:

```text
docs/v1_5_baseline_findings.md
docs/v1_6_confidence_interval_findings.md
docs/v1_6_protected_span_findings.md
docs/v1_6_fertility_findings.md
```

Do-no-harm candidates discovered by English smoke:

```text
English apostrophe guard: Don't, John's, We're, LLaMA's
package/comparator protection: transformers>=4.40
code-mixed loanword guard: data, code, OpenAI
non-Turkish Latin guard: Straße, niño, Bogotá, università
Azerbaijani routing guard: adım, Bakıda, gedir, uzundur
Arabic/Greek script-span fallback
```

Advisor-reviewed R3 decision:

```text
Do not implement Azerbaijani routing in v1.6b.
Token-level schwa guard does not fix the visible failures.
Span-level routing belongs to v2.0.
Close v1.6b at Batch 4 and move to v1.7.
```

Current recommended next step:

```text
Create configs/v1_7_baselines.toml and baseline matrix implementation tasks.
```

Updated after advisor feedback:

```text
Do not start with more tokenizer rules.
Start v1.6a with evaluation-strengthening:
- bootstrap confidence intervals
- protected-span break metrics
- natural/demo corpus fertility reports
Then move to v1.6b low-risk routing guards.
```

Bootstrap confidence intervals, protected-span break metrics, and natural/demo
corpus fertility reporting are now complete.

v1.6b Batch 1 through Batch 4 are complete and v1.6b is now closed:

```text
docs/v1_6b_batch1_technical_comparator_guard.md
artifacts/v1_6b_public_stress_report.md
artifacts/v1_6b_protected_span_report_stress.md
artifacts/v1_6b_real_tokenizer_report_english_smoke.md
artifacts/v1_6b_ci_all_en_smoke.md
docs/v1_6b_batch2_arabic_greek_fallback.md
artifacts/v1_6b_batch2_public_stress_report.md
artifacts/v1_6b_batch2_protected_span_report_stress.md
artifacts/v1_6b_batch2_real_tokenizer_report_multilingual_smoke.md
artifacts/v1_6b_batch2_ci_all_multilingual_smoke.md
docs/v1_6b_batch3_apostrophe_guard.md
artifacts/v1_6b_batch3_public_stress_report.md
artifacts/v1_6b_batch3_protected_span_report_stress.md
artifacts/v1_6b_batch3_real_tokenizer_report_english_smoke.md
artifacts/v1_6b_batch3_real_tokenizer_report_multilingual_smoke.md
artifacts/v1_6b_batch3_ci_all_en_smoke.md
artifacts/v1_6b_batch3_ci_all_multilingual_smoke.md
docs/v1_6b_batch4_non_turkish_latin_guard.md
artifacts/v1_6b_batch4_public_stress_report.md
artifacts/v1_6b_batch4_protected_span_report_stress.md
artifacts/v1_6b_batch4_real_tokenizer_report_multilingual_smoke.md
artifacts/v1_6b_batch4_ci_all_multilingual_smoke.md
docs/advisor_request_v1_6b_r3_azerbaijani.md
docs/v1_6b_r3_deferred_decision.md
docs/v1_7_plan.md
docs/v1_7_heldout_eval_plan.md
docs/v1_7_missing_baseline_protocol.md
docs/v1_7_downstream_probe_protocol.md
docs/v2_0_router_morphbpe_rfc.md
configs/v1_7_baselines.toml
scripts/report_baseline_matrix.py
configs/v1_7_sentencepiece_sweep.toml
docs/v1_7_claim_grade_corpus_plan.md
docs/v1_7_celik_ai_corpus_tokenizer_audit.md
scripts/run_sentencepiece_sweep.py
configs/v1_7_claim_grade_corpus.toml
scripts/prepare_claim_grade_corpus.py
tests/test_prepare_claim_grade_corpus.py
artifacts/v1_7_baseline_matrix_expanded.md
artifacts/v1_7_baseline_matrix_challenge.md
artifacts/v1_7_baseline_matrix_english_smoke.md
artifacts/v1_7_baseline_matrix_multilingual_smoke.md
artifacts/v1_7_public_stress_report.md
artifacts/v1_7_sentencepiece_sweep/sp_bpe_1000_demo.model
artifacts/v1_7_sentencepiece_sweep/sp_bpe_1000_demo.vocab
artifacts/v1_7_sentencepiece_sweep/sp_unigram_1000_demo.model
artifacts/v1_7_sentencepiece_sweep/sp_unigram_1000_demo.vocab
artifacts/v1_7_sentencepiece_sweep_expanded.md
artifacts/v1_7_sentencepiece_sweep_challenge.md
artifacts/v1_7_celik_64k_tokenizer_report_expanded.md
artifacts/v1_7_celik_64k_tokenizer_report_challenge.md
artifacts/v1_7_claim_grade_corpus_manifest.md
artifacts/v1_7_claim_grade_leakage_report.md
configs/v1_7_sentencepiece_pilot_sweep.toml
docs/v1_7_sentencepiece_pilot_findings.md
artifacts/v1_7_sentencepiece_pilot_sweep_expanded.md
artifacts/v1_7_sentencepiece_pilot_sweep_challenge.md
scripts/audit_jsonl_corpus_quality.py
tests/test_audit_jsonl_corpus_quality.py
artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md
```

Next recommended step:

```text
Hand the prepared private token JSONL splits to the LLM training side for a
small byte-normalized LM loss probe, or run a larger 32k/48k/64k clean SP sweep
only if a baseline-scaling decision is needed. Do not add new tokenizer
morphology rules.
```

Guardrails after v1.6b:

```text
python -m pytest
tr_gold_expanded.tsv must remain 50/50
tr_stress_public.tsv must remain 34/34 roundtrip
custom protected span break rate must remain 0.0000
Do not add broad Turkish morphology rules
Do not start with Azerbaijani morphology or span-level routing
```
