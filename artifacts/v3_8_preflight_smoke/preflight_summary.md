# v3.8 Final Corpus Preflight Summary

Manifest: `artifacts\private\v3_8_materialize_smoke\manifest.json`
Base dir: `C:\TÜRKÇE-TOKENIZER`
Canonical text output: `artifacts\private\v3_8_preflight_smoke\final_corpus_text.txt`
Status: `PASS`

This preflight validates the final corpus handoff and materializes the
canonical plain-text corpus view used by SP retrain and production
tokenization.

## Gate Results

| Gate | Status | Failures | Warnings | Report |
| --- | --- | ---: | ---: | --- |
| `manifest` | `PASS` | 0 | 0 | `artifacts\v3_8_preflight_smoke\manifest_validation.md` |
| `materialization` | `PASS` | 0 | 0 | `artifacts\v3_8_preflight_smoke\text_materialization.md` |

## Failures

None.

## Warnings

None.

## Next

Use the canonical text output as the input to final SP retrain, route
density/fertility reports, and `scripts/tokenize_corpus.py`.
