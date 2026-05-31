# Current Resume Point

Date: 2026-05-31

## Current State

The project has completed v1.6b Batch 4 do-no-harm routing work and deferred R3
Azerbaijani routing after advisor review.

Current next step:

```text
v1.7 baseline matrix config and visible reports are now available.
The Turkish-trained SentencePiece sweep scaffold is now available in demo-only
mode. Advisor feedback on claim-grade corpus choice has been converted into a
corpus plan. A read-only audit of the user's `C:\CELIK_AI` corpus/tokenizer
artifacts found useful raw text candidates and a local 64k ByteLevel BPE
tokenizer reference. Local CELIK_AI text sources have been copied into the
repo's ignored private corpus area, and the corpus-preparation/leakage-check
skeleton now produces aggregate reports. A 75,388-line local CELIK_AI pilot
sample and 4k/8k SentencePiece BPE/Unigram pilot sweep are available, with
private model/vocab files kept out of git. The user's primary
`celik_gold_corpus.jsonl` source has also been copied into the ignored private
area and audited on the first 100k lines. Next: either add explicit filtering
for long/control/replacement-character lines and rebuild the pilot sample from
the gold JSONL source, or begin the downstream-probe runner skeleton.
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

After `celik_gold_corpus.jsonl` 100k quality audit:

```text
copied source:
data/train/private/celik_ai/celik_gold_corpus.jsonl

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
Add filtering/source-proportion controls for the local gold JSONL corpus and
rebuild the SentencePiece pilot sample, or start the downstream-probe runner
skeleton. Do not add new tokenizer morphology rules.
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
