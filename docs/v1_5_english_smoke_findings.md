# v1.5 English Smoke Findings

Date: 2026-05-30

Tokenizer behavior: not changed

## Purpose

This smoke test checks whether the Turkish-centered tokenizer harms English and
technical English-like text.

This is not an English morphology benchmark. It is a do-no-harm check for:

- plain English pass-through
- English apostrophes
- technical/package-like spans
- code-like snippets
- Turkish-English code-mixed examples

## Dataset

```text
data/eval/en_smoke.tsv
```

The expected tokens are a simple word/punctuation policy, not a deep English
morphology gold standard.

## Summary

```text
custom_tr_morph exact_match: 5/10
custom_tr_morph boundary_f1: 0.7949
custom_tr_morph avg_tokens/word: 1.2692
```

All-baseline report:

```text
artifacts/v1_5_real_tokenizer_report_english_smoke.md
```

## Baseline Table

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 1.2692 | 0.7949 | 5/10 |
| qwen | 1.5641 | 0.5251 | 0/10 |
| llama | 1.4872 | 0.5434 | 0/10 |
| mistral | 1.9487 | 0.5742 | 0/10 |
| toy_bpe_1000 | 3.5256 | 0.3735 | 0/10 |
| sp_bpe | 3.4872 | 0.3647 | 0/10 |
| sp_unigram | 3.7692 | 0.3533 | 0/10 |
| unicode_char | 5.0769 | 0.2781 | 0/10 |

## Category Findings

| Category | custom_tr_morph F1 | Main observation |
| --- | ---: | --- |
| code_like | 1.0000 | Basic code snippets are preserved well. |
| english_passthrough | 0.9697 | Plain English mostly passes through. |
| english_apostrophe | 0.6667 | English contractions/possessives are incorrectly routed through Turkish apostrophe splitting. |
| technical | 0.5000 | Package/version comparison spans like `transformers>=4.40` are split too much. |
| mixed_turkish_english | 0.7442 | Turkish morphology still fires on English/code-mixed tokens such as `data` and `code`. |

## Important Mismatches

### English Apostrophe

```text
Don't split John's book.
expected: ▁Don't ▁split ▁John's ▁book .
actual:   ▁Don ' +t ▁split ▁John ' +s ▁book .
```

This is a clear do-no-harm issue. The Turkish apostrophe suffix flow should not
fire on English contractions or possessives.

### Technical Comparator Spans

```text
Install transformers>=4.40 and tokenizers>=0.19.
expected: ▁transformers>=4.40 ... ▁tokenizers>=0.19
actual:   ▁transformers > = ▁4.40 ... ▁tokenizers > = ▁0.19
```

This suggests that package/version comparator spans should be protected before
morphology.

### Code-Mixed Loanwords

```text
OpenAI API'den data aldım in a code-mixed sentence.
expected: ▁OpenAI ▁API ' +den ▁data ▁aldım ... ▁code-mixed ...
actual:   ▁OpenA +I ▁API ' +den ▁da +ta ▁al +dı +m ... ▁co +de - ▁mixed ...
```

This confirms earlier advisor warnings: English/code-mixed tokens are not a
separate multilingual problem only; they also expose Turkish false-positive
splitting risk.

## Interpretation

The tokenizer is not an English tokenizer, and it should not try to become one
in v1.x. But it should avoid damaging common English spans in Turkish-centered
multilingual text.

The right policy is:

```text
English/general text: pass through or defer to BPE fallback.
Turkish morphology: only fire when Turkish-specific cues are strong.
Code/file/version spans: protect before morphology.
```

## Recommended Follow-Up

Do not add broad English morphology rules.

Recommended v1.x do-no-harm fixes:

1. Add an English apostrophe guard so `Don't`, `John's`, `We're`, `LLaMA's` do
   not route through Turkish suffix splitting.
2. Add package/comparator span protection for examples like
   `transformers>=4.40`.
3. Add a small protected English/code-mixed negative list or routing guard for
   high-risk words such as `data`, `code`, and mixed-case identifiers such as
   `OpenAI`.
4. Keep Turkish regression `tr_gold_expanded.tsv` at 50/50 before and after any
   do-no-harm fix.

These fixes should be treated as low-risk pretokenizer/routing fixes, not as
new broad morphology rules.
