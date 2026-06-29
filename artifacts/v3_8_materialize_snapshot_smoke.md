# v3.8 Final Corpus Text Materialization

Manifest: `artifacts\tokenizer_v3_0\v3_8_materialize_snapshot_smoke\manifest.json`
Base dir: `C:\CELIK-GARDASH`
Status: `PASS`

This materializes the frozen final corpus into the plain UTF-8 text view
expected by SentencePiece training and production tokenization.

## Summary

| Metric | Value |
| --- | ---: |
| corpus format | `jsonl` |
| source path | `C:\CELIK-GARDASH\artifacts\tokenizer_v3_0\v3_8_materialize_snapshot_smoke\source.jsonl` |
| output path | `artifacts\tokenizer_v3_0\v3_8_materialize_snapshot_smoke\final_text.txt` |
| scanned lines | 2 |
| written lines | 2 |
| output bytes | 26 |
| invalid JSON | 0 |
| missing text | 0 |
| non-string text | 0 |

## Failures

None.

## Manifest Warnings

None.

## Next

Use the output path as `--input` for `scripts/tokenize_corpus.py` and
as the text corpus view for final SentencePiece retrain.
