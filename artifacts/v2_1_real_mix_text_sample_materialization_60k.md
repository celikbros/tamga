# v2.1 Real-Mix Text Sample Materialization

Output: `artifacts/private/v2_1_real_mix/real_mix_60k_sample.txt`
Text field: `text`
Seed: `20260613`
Sample probability: `1.000000`

## Summary

| Metric | Value |
| --- | ---: |
| scanned lines | 40388 |
| written text lines | 40388 |
| output bytes | 44392189 |

## Sources

| Source | Path | Scanned | Written | Bytes written | Invalid JSON | Missing text | Empty/non-string text |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `trt_news` | `data/train/private/celik_ai/trt_news_corpus.jsonl` | 388 | 388 | 1083409 | 0 | 0 | 0 |
| `academic` | `data/train/private/celik_ai/academic_corpus.jsonl` | 20000 | 20000 | 27009371 | 0 | 0 | 0 |
| `ttk` | `data/train/private/celik_ai/ttk_corpus.jsonl` | 20000 | 20000 | 16299409 | 0 | 0 | 0 |

## Next

Use the output file as `--input` for route-density and operation
simulation audits. This materialization writes raw text lines only;
JSON syntax and metadata are not included in the tokenizer audit input.
