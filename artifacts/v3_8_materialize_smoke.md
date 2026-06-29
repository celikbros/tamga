# v3.8 Final Corpus Text Materialization

Manifest: `artifacts\private\v3_8_materialize_smoke\manifest.json`
Base dir: `C:\TÜRKÇE-TOKENIZER`
Status: `PASS`

This materializes the frozen final corpus into the plain UTF-8 text view
expected by SentencePiece training and production tokenization.

## Summary

| Metric | Value |
| --- | ---: |
| corpus format | `jsonl` |
| source path | `C:\TÜRKÇE-TOKENIZER\artifacts\private\v3_8_materialize_smoke\source.jsonl` |
| output path | `artifacts\private\v3_8_materialize_smoke\final_text.txt` |
| scanned lines | 2 |
| written lines | 2 |
| output bytes | 29 |
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
