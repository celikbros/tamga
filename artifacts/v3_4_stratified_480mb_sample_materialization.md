# v3.4 Stratified Text Sample Materialization

Output: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`
Seed: `20260619`
Requested chunks/source: `96`

This sample is built from deterministic byte-region chunks instead of
prefix-only source reads. It is intended as a larger tokenizer-training
candidate sample, not as an LLM pretraining dataset.

## Summary

| Metric | Value |
| --- | ---: |
| target bytes | 505413632 |
| target bytes readable | 482.00 MiB |
| written text lines | 498086 |
| output bytes | 496019404 |
| output bytes readable | 473.04 MiB |

## Sources

| Source | Kind | File bytes | Target bytes | Written bytes | Written lines | Read lines | Scanned bytes | Invalid JSON/UTF-8 | Missing text | Empty text | Short chunks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `trt_news` | `jsonl` | 1098941 | 2097152 | 552129 | 200 | 388 | 1098941 | 0 | 0 | 0 | 1 |
| `academic` | `jsonl` | 64958602 | 33554432 | 33555794 | 24057 | 25129 | 36322186 | 0 | 0 | 0 | 0 |
| `ttk` | `jsonl` | 113165227 | 50331648 | 50332217 | 38799 | 40471 | 55403359 | 0 | 0 | 0 | 0 |
| `tdk` | `jsonl` | 16177989 | 16777216 | 8921058 | 98604 | 118455 | 16177989 | 0 | 0 | 0 | 1 |
| `wiki_oscar` | `jsonl` | 12811797729 | 167772160 | 167773096 | 55484 | 55493 | 170398455 | 0 | 0 | 0 | 0 |
| `celik_gold` | `jsonl` | 13001668604 | 167772160 | 167775782 | 56809 | 56817 | 170374274 | 0 | 0 | 0 | 0 |
| `tr_corpus` | `text` | 457814564 | 67108864 | 67109328 | 224133 | 227259 | 68458004 | 0 | 0 | 0 | 0 |

## Next

Use this text file for v3.4 SentencePiece ablation only after checking
token pressure and route-density on the current v3 sidecar path.
