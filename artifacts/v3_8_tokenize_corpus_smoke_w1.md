# Production Corpus Tokenization Report

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`
Output dir: `artifacts/private/v3_8_tokenize_corpus_smoke_w1`
Tokenizer: `sp64k_stratified_480mb_protected_passthrough_sidecar`
Append EOS: `True`
Workers: `1`
Chunk lines: `7`

## Outputs

| File | Meaning |
| --- | --- |
| `tokens.bin` | Flat little-endian uint32 token ids. |
| `loss_mask.bin` | One uint8 per token: 1=train, 0=masked protected overlap. |
| `index.jsonl` | Per-line token offsets into the flat token stream. |
| `sidecar.jsonl` | Protected span byte/char offsets. |
| `manifest.json` | Machine-readable summary and output paths. |
| `checksums.json` | SHA-256 checksums for produced files. |

## Summary

| Metric | Value |
| --- | ---: |
| lines | 20 |
| raw bytes | 12396 |
| tokens | 2088 |
| tokens/raw byte | 0.168441 |
| eos tokens | 20 |
| fallback tokens | 0 |
| fallback rate | 0.000000 |
| masked tokens | 100 |
| masked token rate | 0.047893 |
| protected spans | 53 |
| protected bytes | 233 |
| sp alignment mismatches | 0 |
| max token id | 59180 |

## Routes

| Route | Spans |
| --- | ---: |
| `numeric_like` | 41 |
| `file_like` | 10 |
| `apostrophe_surface` | 2 |

## Checksums

| File | SHA-256 |
| --- | --- |
| `tokens.bin` | `5ca6b39d6e5b9bf3047c54281e0376a7982c2ab306724041417612bee320343d` |
| `loss_mask.bin` | `d6d298d9c52a67490472d036a907a1dfa1c4c970443d8fcc0ff5a2e5aa25706d` |
| `index.jsonl` | `997c6c39bbe20a35ff3763e81d76db8846a8a222020e21ed4520bdb5557de53b` |
| `sidecar.jsonl` | `d6b72023f1071b61d86fa0d649ca5753fedee1f5dc61d5affa4097b54495bcc3` |
| `manifest.json` | `feade48e1595a495ac3ac81708072391955f4cf932065084c72360df0a3462a3` |

## Gate

- `sp_alignment_mismatches` must be zero before using `loss_mask.bin`
  as a training artifact.
- `checksums.json` should travel with the binary fixture.
- Production serving can port this behavior later; this script is the
  deterministic offline preprocessing path.
