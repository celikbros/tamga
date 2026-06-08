# Current Resume Point

Date: 2026-06-08

## Current State

The project has completed enough v1.8 tiny-LM screening and token accounting
audit work to choose the v2.0 direction.

Current next step:

```text
Stop v2.0 marker-dose tuning. The finite protected-aware path is frozen as the
protected-span mechanism, but train-only morphology marker shaping did not pay
back its token-pressure cost in the 300-step tiny-LM BPB calibration.

The next candidate should change the mechanism: selected morph seed vocabulary,
curated high-value morph pieces, or a constrained Unigram/MorphBPE-style
objective. Use finite_protected_sp64_floor as the true protected null baseline.
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
next user-run command:
  python scripts\analyze_v2_morph_seed_candidates.py --progress 1000
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
