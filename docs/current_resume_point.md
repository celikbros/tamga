# Current Resume Point

Date: 2026-05-30

## Current State

The project is currently in v1.6a evaluation-strengthening work.

Completed:

- v1.4 Batch 1: protected exact lexical items `peki` and `yeni`.
- v1.4 Batch 2: guarded possessive-buffered-ablative split:
  - `sından -> +sı +ndan`
  - `sinden -> +si +nden`
  - `sundan -> +su +ndan`
  - `sünden -> +sü +nden`

Current verified metrics:

```text
python -m pytest
82 passed

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
roundtrip_exact: 28/28
protected_spans_preserved: 23/23
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

## Recommended Next Track

Proceed to the next phase of v1.5 real tokenizer baseline comparison:

```text
Qwen reference tokenizer: first expanded/challenge reports complete
Mistral reference tokenizer: first expanded/challenge reports complete
LLaMA reference tokenizer: first expanded/challenge reports complete
SentencePiece BPE: first local demo baseline complete
SentencePiece Unigram: first local demo baseline complete
existing toy BPE sweep
```

The goal is to compare:

```text
token budget
boundary F1
protected span integrity
byte/fallback coverage
```

Primary planning doc:

```text
docs/v1_5_real_tokenizer_baselines.md
```

Current findings summary:

```text
docs/v1_5_baseline_findings.md
```

Use optional dependencies or local model files, then run
`scripts/compare_real_tokenizers.py` with `--hf`, `--sentencepiece`, or
`--toy-bpe`.

Do-no-harm candidates discovered by English smoke:

```text
English apostrophe guard: Don't, John's, We're, LLaMA's
package/comparator protection: transformers>=4.40
code-mixed loanword guard: data, code, OpenAI
non-Turkish Latin guard: Straße, niño, Bogotá, università
Azerbaijani routing guard: adım, Bakıda, gedir, uzundur
Arabic/Greek script-span fallback
```

Current recommended next step:

```text
docs/v1_6_do_no_harm_routing_plan.md
docs/advisor_feedback_triage_v1_6.md
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

Next recommended step:

```text
Start v1.6b with the narrow technical comparator/package span guard.
```
