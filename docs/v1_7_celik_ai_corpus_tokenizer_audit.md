# v1.7 CELIK_AI Corpus And Tokenizer Audit

Date: 2026-05-31

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

Next engineering step:

```text
Create a corpus-preparation/leakage-check script that can read local TXT and
JSONL sources, produce a private training text sample, and publish only manifest
and leakage statistics.
```
