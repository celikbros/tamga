# v3.1 Corpus Tokenization Smoke

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt`
Output dir: `artifacts/private/v3_1_tokenized_corpus_smoke_250`
Tokenizer: `sp64_protected_passthrough_sidecar`
Append EOS: `True`

This is a reference smoke for the binary LLM handoff format. It is not
an optimized production tokenizer.

## Outputs

| File | Meaning |
| --- | --- |
| `tokens.bin` | Flat little-endian uint32 token ids. |
| `loss_mask.bin` | One uint8 per token: 1=train, 0=masked protected overlap. |
| `index.jsonl` | Per-line token offsets into the flat token stream. |
| `sidecar.jsonl` | Protected span byte/char offsets. |
| `manifest.json` | Machine-readable summary and format metadata. |

## Summary

| Metric | Value |
| --- | ---: |
| lines | 250 |
| raw bytes | 764850 |
| tokens | 133683 |
| tokens/raw byte | 0.174783 |
| eos tokens | 250 |
| fallback tokens | 57 |
| fallback rate | 0.000426 |
| masked tokens | 4450 |
| masked token rate | 0.033288 |
| protected spans | 3192 |
| protected bytes | 8711 |
| sp alignment mismatches | 0 |
| max token id | 64239 |
| token dtype | uint32_le |

## Routes

| Route | Spans |
| --- | ---: |
| `numeric_like` | 3121 |
| `file_like` | 40 |
| `apostrophe_surface` | 31 |

## Gate

- `sp_alignment_mismatches` should be zero or explained before using
  `loss_mask.bin` as a training artifact.
- This smoke validates the file contract; production throughput is a
  separate Rust/C++ or offline preprocessing task.
