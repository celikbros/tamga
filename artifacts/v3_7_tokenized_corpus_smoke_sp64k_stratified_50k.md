# v3.1 Corpus Tokenization Smoke

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`
Output dir: `C:/CELIK-GARDASH/datasets/tokenizer_v3_7_smoke/sp64k_stratified_50k`
Tokenizer: `sp64k_stratified_480mb_protected_passthrough_sidecar`
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
| lines | 50000 |
| raw bytes | 48942124 |
| tokens | 9060436 |
| tokens/raw byte | 0.185126 |
| eos tokens | 50000 |
| fallback tokens | 5352 |
| fallback rate | 0.000591 |
| masked tokens | 575205 |
| masked token rate | 0.063485 |
| protected spans | 319592 |
| protected bytes | 1432490 |
| sp alignment mismatches | 0 |
| max token id | 64243 |
| token dtype | uint32_le |

## Routes

| Route | Spans |
| --- | ---: |
| `numeric_like` | 265647 |
| `file_like` | 25048 |
| `arabic_word` | 8085 |
| `apostrophe_surface` | 6801 |
| `cyrillic_word` | 6572 |
| `non_turkish_latin_word` | 6398 |
| `greek_word` | 649 |
| `azerbaijani_word` | 220 |
| `percent_encoded` | 149 |
| `url` | 18 |
| `uzbek_apostrophe_word` | 5 |

## Gate

- `sp_alignment_mismatches` should be zero or explained before using
  `loss_mask.bin` as a training artifact.
- This smoke validates the file contract; production throughput is a
  separate Rust/C++ or offline preprocessing task.
