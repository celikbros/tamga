# v1.6 Do-No-Harm Routing Plan

Date: 2026-05-30

Tokenizer behavior: not changed in this document

## Purpose

v1.5 showed that the Turkish-centered morphology layer has strong signal on
Turkish morphology evals, but smoke tests also exposed non-Turkish damage.

v1.6 should not add broad new Turkish morphology rules.

The goal is narrower:

```text
When input is likely non-Turkish or protected technical text, avoid routing it
through Turkish morphology.
```

This is a do-no-harm routing pass.

## Inputs

Primary evidence:

```text
docs/v1_5_english_smoke_findings.md
docs/v1_5_multilingual_smoke_findings.md
artifacts/v1_5_real_tokenizer_report_english_smoke.md
artifacts/v1_5_real_tokenizer_report_multilingual_smoke.md
```

Regression guards:

```text
data/eval/tr_gold_expanded.tsv
data/eval/tr_challenge.tsv
data/eval/en_smoke.tsv
data/eval/multilingual_smoke.tsv
data/eval/tr_stress_public.tsv
```

## Non-Goals

v1.6 should not:

- implement full multilingual tokenization
- implement Turkic morphology
- add broad Turkish suffix rules
- tune against LLaMA/Qwen/Mistral token strings
- claim production multilingual readiness
- normalize non-Turkish text into Turkish-like forms

## Candidate Fixes

### R1: English And European Apostrophe Guard

Status: implemented in v1.6b Batch 3. See
`docs/v1_6b_batch3_apostrophe_guard.md`.

Problem:

```text
Don't -> ▁Don ' +t
John's -> ▁John ' +s
d'Istanbul -> ▁d ' +Istanbul
L'amico -> ▁L ' +amico
```

Suggested fix:

If an apostrophe-containing token is not followed by a known Turkish suffix
tail, keep it as a surface word. Turkish apostrophe suffix splitting should
still work for:

```text
Türkiye'den
Ali'nin
API'den
README.md'yi
2026'da
```

Risk: low to medium.

Revert if:

- `tr_gold_expanded.tsv` falls below 50/50
- Turkish apostrophe examples stop splitting
- protected file/date apostrophe examples regress

### R2: Non-Turkish Latin Word Guard

Status: implemented in v1.6b Batch 4. See
`docs/v1_6b_batch4_non_turkish_latin_guard.md`.

Problem:

```text
Straße -> ▁Stra ß ▁e
niño -> ▁ni ñ ▁o
Bogotá -> ▁Bogot á
università -> ▁universit à
```

Suggested fix:

Treat Latin-script words with non-Turkish Latin letters as surface spans rather
than letting the Turkish word scanner split them into fragments.

Risk: low.

Revert if:

- Turkish diacritics stop behaving correctly
- file/code/URL protection changes unexpectedly

### R3: Azerbaijani Routing Guard

Problem:

```text
adım -> ▁ad +ım
Bakıda -> ▁Bak +ı +da
gedir -> ▁ge +dir
uzundur -> ▁uzun +dur
```

Suggested fix:

If a token or local sentence span contains strong Azerbaijani cues such as
`ə/Ə`, `q`, or `x`, avoid Turkish suffix splitting for nearby Latin words unless
there is an explicit Turkish apostrophe suffix.

Risk: medium.

Revert if:

- Turkish code_mixed examples regress
- `API'den`, `OpenAI...`, or Turkish mixed-case suffix examples regress

### R4: Arabic/Greek Script Word Fallback

Status: implemented in v1.6b Batch 2. See
`docs/v1_6b_batch2_arabic_greek_fallback.md`.

Problem:

```text
مرحبا بالعالم. -> character sequence
Αθήνα είναι όμορφη πόλη. -> character sequence
```

Suggested fix:

Group Arabic and Greek script runs as word-like spans with `▁` word-start
markers. Do not apply Turkish suffix splitting.

Risk: low.

Revert if:

- Cyrillic word grouping regresses
- punctuation spacing/decode roundtrip regresses

### R5: Technical Comparator Span Guard

Status: implemented in v1.6b Batch 1. See
`docs/v1_6b_batch1_technical_comparator_guard.md`.

Problem:

```text
transformers>=4.40 -> ▁transformers > = ▁4.40
tokenizers>=0.19 -> ▁tokenizers > = ▁0.19
```

Suggested fix:

Protect common package/comparator/version spans:

```text
name>=1.2
name<=1.2
name==1.2
name~=1.2
name!=1.2
```

Risk: low.

Revert if:

- numeric/date/file guards regress
- ordinary punctuation around `>`, `<`, `=` becomes sticky in prose

## Proposed Order

Updated after advisor feedback and v1.6a measurement work:

1. R5 technical comparator span guard: completed in v1.6b Batch 1
2. R4 Arabic/Greek script word fallback: completed in v1.6b Batch 2
3. R1 English/European apostrophe guard: completed in v1.6b Batch 3
4. R2 non-Turkish Latin word guard: completed in v1.6b Batch 4
5. R3 Azerbaijani routing guard: design review required before implementation

R5 is first because package/comparator spans are narrow and less linguistically
ambiguous than apostrophe or language-routing decisions. R3 is last because it
may need local context, not only token-level checks, and v1.x should not claim
Azerbaijani morphology.

## Success Criteria

Required:

```text
python -m pytest
python scripts/evaluate_tokenizer.py data/eval/tr_gold_expanded.tsv
python scripts/evaluate_tokenizer.py data/eval/en_smoke.tsv
python scripts/evaluate_tokenizer.py data/eval/multilingual_smoke.tsv
python scripts/report_stress_public.py data/eval/tr_stress_public.tsv --markdown-out artifacts/stress_public_report.md
python scripts/report_protected_spans.py data/eval/tr_stress_public.tsv --toy-bpe toy_bpe_1000=artifacts/bpe_1000.json --sentencepiece sp_bpe=artifacts/sp_bpe_1000.model --sentencepiece sp_unigram=artifacts/sp_unigram_1000.model --hf qwen=Qwen/Qwen2.5-0.5B --hf mistral=mistralai/Mistral-7B-v0.1 --hf llama=meta-llama/Llama-3.2-1B --markdown-out artifacts/v1_6_protected_span_report_stress.md
```

Expected:

- `tr_gold_expanded.tsv` remains 50/50.
- English smoke exact match improves above 5/10.
- Multilingual smoke exact match improves above 8/20.
- English/French/Italian apostrophe mismatches decrease.
- Arabic/Greek no longer fall to character-level sequences.
- Protected span break rate for `custom_tr_morph` remains `0.0000`.
- Natural/demo corpus fertility does not regress unexpectedly.

## Interpretation Guard

Passing v1.6 does not mean the tokenizer is multilingual.

It means:

```text
The Turkish-centered tokenizer is safer around non-Turkish input than before.
```

That is the right v1.x goal.
