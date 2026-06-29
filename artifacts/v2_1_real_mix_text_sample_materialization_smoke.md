# v2.1 Real-Mix Text Sample Materialization

Output: `artifacts/private/v2_1_real_mix/real_mix_smoke.txt`
Text field: `text`
Seed: `20260613`
Sample probability: `1.000000`

## Summary

| Metric | Value |
| --- | ---: |
| scanned lines | 100 |
| written text lines | 100 |
| output bytes | 295921 |

## Sources

| Source | Path | Scanned | Written | Bytes written | Invalid JSON | Missing text | Empty/non-string text |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `trt_smoke` | `data/train/private/celik_ai/trt_news_corpus.jsonl` | 100 | 100 | 295921 | 0 | 0 | 0 |

## Next

Use the output file as `--input` for route-density and operation
simulation audits. This materialization writes raw text lines only;
JSON syntax and metadata are not included in the tokenizer audit input.
