# v1.7 Claim-Grade Corpus Plan

Date: 2026-05-31

## Purpose

This note converts the advisor feedback about claim-grade Turkish
SentencePiece baselines into a concrete project decision.

The goal is not to make the custom tokenizer look good against weak baselines.
The goal is to train strong Turkish BPE/Unigram baselines and then compare
fairly.

## Advisor Consensus

Three independent review threads converged on the same core points:

- the current 310-line demo corpus is useful only for wiring checks
- 1k demo BPE/Unigram is not a claim-grade baseline
- a real Turkish-trained SentencePiece baseline needs a larger, documented,
  leakage-checked corpus
- BPE and Unigram should both be swept across multiple vocab sizes
- leakage checks should go beyond exact sentence match
- larger vocab anchors such as 48k or 64k should be present to test whether the
  morphology-aware advantage persists at high vocabulary budgets

## Corpus Decision

Primary recommendation:

```text
FineWeb-2 TR or CulturaX TR as the main cleaned web source
plus Turkish Wikipedia as a formal/encyclopedic quality anchor
```

Conservative fallback:

```text
OSCAR 23.01 Turkish deduplicated split
plus Turkish Wikipedia
```

Rationale:

- FineWeb-2 and CulturaX are modern, documented, filtered Common Crawl-derived
  corpora.
- OSCAR is widely used and reproducible, but the text is still Common
  Crawl-derived and should be reported with that caveat.
- Wikipedia is smaller but has cleaner licensing and formal Turkish coverage.
- BOUN/TNC/METU-Sabanci style resources are valuable linguistic references, but
  they should not be the primary baseline training corpus unless redistribution
  and access terms are explicit.

Reference context checked on 2026-05-31:

- FineWeb-2 is released under ODC-By 1.0 and is documented as a multilingual
  pretraining corpus with reproducible processing.
- FineWeb2-HQ reports a Turkish `tur_Latn` split and is also ODC-By 1.0 subject
  to Common Crawl terms.
- OSCAR 23.01 documents that metadata/annotations are CC0 while the text is
  Common Crawl-derived content.
- CulturaX is a cleaned corpus built from mC4 and OSCAR-derived data.

## Size Targets

Do not treat these as LM pretraining sizes. These are tokenizer-training
baseline sizes.

Minimum useful claim-grade target:

```text
10M+ words
```

Better target:

```text
100M+ words
```

Preferred if practical:

```text
100M-500M tokens/words after cleaning
```

The project should not jump to very large multi-GB training unless the smaller
claim-grade sample is reproducible and leakage-checked first.

## Mixture Policy

Start simple:

```text
80-90% cleaned web corpus
10-20% Turkish Wikipedia
```

Avoid a hand-tuned multi-domain blend at first. A simple documented recipe is
more defensible than a complex mixture chosen after seeing eval results.

Optional later additions:

- small informal slice, only if hidden/heldout eval contains informal Turkish
- small technical/code-mixed slice, only if evaluating code-mixed behavior as a
  baseline dimension

## Leakage Policy

Exact sentence match is required but not enough.

Required stages:

1. exact raw sentence match against visible and private eval texts
2. normalized match with whitespace and punctuation normalization
3. Turkish-aware casing caution: do not use naive global lowercase as the only
   dedup view because `I/i/İ/ı` can be corrupted
4. n-gram overlap check, starting with 8-gram or 13-gram overlap
5. report counts removed due to leakage or near-duplicate overlap

Do not remove ordinary shared vocabulary. The target is sentence/document-level
overlap, not normal Turkish words.

## Vocab Sweep

The claim-grade sweep should include:

```text
1k, 4k, 8k, 16k, 32k, 48k, 64k
```

for both:

```text
SentencePiece BPE
SentencePiece Unigram
```

Interpretation:

- 1k is a low anchor and likely over-segments Turkish.
- 8k-16k is a useful middle range.
- 32k is a common production-style baseline point.
- 48k/64k test whether a large vocabulary erases the apparent morphology-aware
  boundary advantage.

## Current Config Status

The current config is:

```text
configs/v1_7_sentencepiece_sweep.toml
```

Enabled:

```text
sp_bpe_1000_demo
sp_unigram_1000_demo
```

Disabled until a larger leakage-checked corpus exists:

```text
4k, 8k, 16k, 32k, 48k, 64k BPE/Unigram claim-grade variants
```

This is intentional. Running 32k or 64k on the current tiny demo corpus would be
misleading.

## Implemented Engineering Step

The corpus-preparation skeleton now exists:

```text
scripts/prepare_claim_grade_corpus.py
configs/v1_7_claim_grade_corpus.toml
```

The first version supports local TXT and JSONL sources without downloading data
by default. On this machine, local CELIK_AI text sources were copied into:

```text
data/train/private/celik_ai/
```

That directory is ignored by git.

Current aggregate-only outputs:

```text
artifacts/v1_7_claim_grade_corpus_manifest.md
artifacts/v1_7_claim_grade_leakage_report.md
```

Guardrail:

```text
Do not commit large corpus text to the repo.
Commit only config, scripts, manifests, and aggregate reports.
```

Smoke command:

```powershell
python scripts/prepare_claim_grade_corpus.py configs/v1_7_claim_grade_corpus.toml --manifest-only --max-scan-lines 1000
```

The initial 1000-line-per-source smoke report found no exact, normalized, or
8-gram leakage hits against the visible expanded/challenge eval sets. This is
not a full corpus certification yet; it only proves that the pipeline and
reporting path work before larger scans.
