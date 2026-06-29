# v3.1 Corpus Tokenization Smoke

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt`
Output dir: `C:/CELIK-GARDASH/datasets/tokenizer_v3_3_smoke/sp48k_real_mix_full`
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
| lines | 40388 |
| raw bytes | 44351801 |
| tokens | 7350435 |
| tokens/raw byte | 0.165730 |
| eos tokens | 40388 |
| fallback tokens | 336 |
| fallback rate | 0.000046 |
| masked tokens | 278873 |
| masked token rate | 0.037940 |
| protected spans | 149999 |
| protected bytes | 682931 |
| sp alignment mismatches | 0 |
| max token id | 48244 |
| token dtype | uint32_le |

## Routes

| Route | Spans |
| --- | ---: |
| `numeric_like` | 127588 |
| `file_like` | 10309 |
| `apostrophe_surface` | 7579 |
| `non_turkish_latin_word` | 3228 |
| `greek_word` | 606 |
| `arabic_word` | 391 |
| `percent_encoded` | 171 |
| `uzbek_apostrophe_word` | 69 |
| `cyrillic_word` | 50 |
| `azerbaijani_word` | 8 |

## Gate

- `sp_alignment_mismatches` should be zero or explained before using
  `loss_mask.bin` as a training artifact.
- This smoke validates the file contract; production throughput is a
  separate Rust/C++ or offline preprocessing task.
