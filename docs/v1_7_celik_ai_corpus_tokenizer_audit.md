# v1.7 CELIK_AI Corpus And Tokenizer Audit

Date: 2026-05-31

Update on 2026-06-01:

```text
The older raw private copy has been moved locally to:
data/train/private/celik_ai/archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl

Active v1.7 baseline work now uses:
data/train/private/celik_ai/celik_gold_corpus.clean.jsonl
```

The original `C:\CELIK_AI` files were not modified.

Source path:

```text
C:\CELIK_AI
```

This audit is read-only. No files in `C:\CELIK_AI` were modified or deleted.

## Scope

The user noted that a previous LLM project used local corpus and tokenizer
artifacts. The purpose here is to decide whether those artifacts help
`tr-centric-tokenizer` v1.7 measurement work.

## Dataset Inventory

Large binary training packages:

```text
C:\CELIK_AI\datasets\train_corpus.bin
C:\CELIK_AI\datasets\val_corpus.bin
C:\CELIK_AI\datasets\gold_corpus_tokenized.bin
```

Decision:

```text
Do not use these for SentencePiece baseline training.
```

Reason:

- they are already tokenized/packed for LLM training
- they are not raw text
- they may still be useful only for that older LLM training stack

Raw or semi-raw text candidates:

```text
C:\CELIK_AI\celik_training\celik_gold_corpus.jsonl                 (~13.0 GB)
C:\CELIK_AI\datasets\pretrain\tr_corpus.txt        (~458 MB)
C:\CELIK_AI\datasets\pretrain\en_corpus.txt        (~519 MB)
C:\CELIK_AI\celik_training\data_pipeline\wiki_oscar_corpus.jsonl (~12.8 GB)
C:\CELIK_AI\celik_training\data_pipeline\academic_corpus.jsonl    (~65 MB)
C:\CELIK_AI\celik_training\data_pipeline\tdk_corpus.jsonl         (~16 MB)
C:\CELIK_AI\celik_training\data_pipeline\ttk_corpus.jsonl         (~113 MB)
C:\CELIK_AI\celik_training\data_pipeline\trt_news_corpus.jsonl    (~1.1 MB)
```

The JSONL files use records shaped like:

```json
{"text": "...", "source": "..."}
```

UTF-8 byte checks show that Turkish characters are stored correctly. The mojibake
seen in some PowerShell output is a display issue, not corpus corruption.

The main raw JSONL file reported by the user is:

```text
C:\CELIK_AI\celik_training\celik_gold_corpus.jsonl
```

It was originally copied into the repo's ignored private corpus area and later
archived as a deprecated raw copy:

```text
data/train/private/celik_ai/archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl
```

The active copied source is now the cleaned corpus:

```text
data/train/private/celik_ai/celik_gold_corpus.clean.jsonl
```

Private corpus copies are not committed to git.

## Corpus Builder Findings

Relevant files:

```text
C:\CELIK_AI\corpus_builder\sources.json
C:\CELIK_AI\corpus_builder\runner.py
C:\CELIK_AI\corpus_builder\merge_corpus.py
C:\CELIK_AI\celik_training\data_pipeline\build_corpus.py
C:\CELIK_AI\celik_training\data_pipeline\cleaner.py
```

Observed source plan:

- mC4 / AllenAI C4 multilingual web data
- Turkish Wikipedia
- TDK dictionary content
- TTK Belleten
- DergiPark academic abstracts
- TRT News RSS

Observed cleaning/dedup features:

- `ftfy.fix_text`
- URL/HTML/bracket cleanup
- repeated-character cleanup
- FastText language ID using `lid.176.bin`
- Turkish probability threshold around `0.90-0.95`
- exact MD5 dedup
- MinHash LSH near-duplicate filtering at threshold `0.8`

Important caveat:

```text
wiki_oscar_corpus.jsonl appears to be built from Turkish Wikipedia plus
allenai/c4 Turkish streaming data, not necessarily OSCAR despite the file name.
```

For claim-grade reporting, call it by its actual documented sources unless the
input provenance is confirmed.

## Old CELIK Tokenizer

Path:

```text
C:\CELIK_AI\celik_core\celik_core\tokenizer.json
```

Observed structure:

```text
type: BPE
vocab_size: 64000
merge_count: 63727
byte_fallback: true
normalizer: none
pre_tokenizer: ByteLevel(add_prefix_space=false, use_regex=true)
decoder: ByteLevel
post_processor: TemplateProcessing
special tokens: 17
```

Special tokens:

```text
<pad>, <unk>, <bos>, <eos>, <sep>, <mask>,
<system>, <user>, <asst>,
<thinking>, </thinking>, <answer>, </answer>,
<verify>, </verify>, <reflect>, </reflect>
```

Interpretation:

- this is a local LLM-oriented ByteLevel BPE tokenizer
- it is not morphology-aware
- it is relevant as a historical/local production-like baseline
- it should not be treated as a claim-grade Turkish morphology baseline by
  itself

## Repo Integration

Added support for local Hugging Face `tokenizers` JSON baselines:

```text
kind = "tokenizers_json"
```

The v1.7 baseline config now includes this local reference disabled by default:

```text
[[baselines]]
name = "celik_64k_byte_bpe_local"
kind = "tokenizers_json"
path = "C:/CELIK_AI/celik_core/celik_core/tokenizer.json"
enabled = false
```

It is disabled because the path is machine-local. It can be enabled on this
machine for comparison runs, but the repo does not depend on that external file.

Visible eval reference reports:

```text
artifacts/v1_7_celik_64k_tokenizer_report_expanded.md
artifacts/v1_7_celik_64k_tokenizer_report_challenge.md
```

Observed boundary-F1 signal:

| Dataset | custom_tr_morph F1 | celik_64k_byte_bpe F1 |
| --- | ---: | ---: |
| expanded | 1.0000 | 0.2135 |
| challenge | 0.9220 | 0.2376 |

This does not mean the old CELIK tokenizer is bad for its original LLM purpose.
It means a generic ByteLevel BPE tokenizer does not preserve this project's
Turkish morphology-policy boundaries.

## Recommended Use

Use `C:\CELIK_AI` as a local source pool for v1.7 claim-grade corpus prep:

1. do not use `.bin` files
2. use `tr_corpus.txt` for a medium local smoke baseline
3. use `wiki_oscar_corpus.jsonl` as the strongest local candidate, after leakage
   checks and provenance documentation
4. keep all large corpus text outside git
5. commit only scripts, configs, manifests, and aggregate reports

## Local Copy Status

The usable local text candidates were copied into the repo workspace under an
ignored private directory:

```text
data/train/private/celik_ai/
```

Copied sources:

```text
archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl
celik_gold_corpus.clean.jsonl
tr_corpus.txt
wiki_oscar_corpus.jsonl
academic_corpus.jsonl
tdk_corpus.jsonl
ttk_corpus.jsonl
trt_news_corpus.jsonl
```

No files in `C:\CELIK_AI` were modified or deleted.

## Gold Corpus Quality Audit

Aggregate-only audit script:

```text
scripts/audit_jsonl_corpus_quality.py
```

Initial report:

```text
artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md
```

Command:

```powershell
python scripts/audit_jsonl_corpus_quality.py data/train/private/celik_ai/archive/deprecated/celik_gold_corpus.raw.deprecated.jsonl --max-lines 100000 --markdown-out artifacts/v1_7_celik_gold_corpus_quality_audit_100k.md
```

First 100,000-line findings:

| Signal | Value |
| --- | ---: |
| valid JSON | 100,000 / 100,000 |
| missing/empty text | 0 |
| exact duplicates in scan | 0 |
| normalized duplicates in scan | 0 |
| Turkish-like heuristic | 84.38% |
| mixed TR/EN heuristic | 15.47% |
| Latin script heuristic | 99.998% |
| chars > 4,192 | 1.58% |
| chars > 20,000 | 0.46% |
| mojibake suspects | 0.03% |
| replacement-char texts | 0.003% |
| control-char texts | 0.71% |

Interpretation:

- The file is structurally clean JSONL in the sampled prefix.
- The text appears mostly Turkish/formal, with a meaningful mixed Turkish/English
  slice.
- The corpus is promising for local SentencePiece and downstream probe work.
- Before claim-grade tokenizer training, long lines and control/replacement
  character cases should be filtered or explicitly documented.
- The 100k audit is not a full-file certification; it is a first quality signal.

Implemented engineering step:

```text
scripts/prepare_claim_grade_corpus.py
configs/v1_7_claim_grade_corpus.toml
artifacts/v1_7_claim_grade_corpus_manifest.md
artifacts/v1_7_claim_grade_leakage_report.md
```

The first smoke run used `--manifest-only --max-scan-lines 1000`; it publishes
aggregate source/leakage statistics only and does not commit corpus text.
