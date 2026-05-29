# Current Resume Point

Date: 2026-05-30

## Current State

The project is currently in v1.5 baseline-infrastructure work.

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
Qwen reference tokenizer
LLaMA/Mistral reference tokenizers
SentencePiece BPE
SentencePiece Unigram
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

Use optional dependencies or local model files, then run
`scripts/compare_real_tokenizers.py` with `--hf`, `--sentencepiece`, or
`--toy-bpe`.
