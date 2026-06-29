# v3.1 Corpus Tokenization Smoke

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt`
Output dir: `C:/CELIK-GARDASH/datasets/tokenizer_v3_2_smoke/sp48k_real_mix_5000`
Tokenizer: `sp48k_protected_passthrough_sidecar`
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
| lines | 5000 |
| raw bytes | 6119247 |
| tokens | 980486 |
| tokens/raw byte | 0.160230 |
| eos tokens | 5000 |
| fallback tokens | 4 |
| fallback rate | 0.000004 |
| masked tokens | 30323 |
| masked token rate | 0.030926 |
| protected spans | 16683 |
| protected bytes | 81822 |
| sp alignment mismatches | 0 |
| max token id | 48195 |
| token dtype | uint32_le |

## Routes

| Route | Spans |
| --- | ---: |
| `numeric_like` | 14402 |
| `file_like` | 1659 |
| `apostrophe_surface` | 413 |
| `non_turkish_latin_word` | 157 |
| `greek_word` | 43 |
| `percent_encoded` | 9 |

## Gate

- `sp_alignment_mismatches` should be zero or explained before using
  `loss_mask.bin` as a training artifact.
- This smoke validates the file contract; production throughput is a
  separate Rust/C++ or offline preprocessing task.
