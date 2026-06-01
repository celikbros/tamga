# Eval Leakage Report

Corpus: `data\train\claim_grade\celik_gold_clean_pilot.txt`
Scanned records: `100000`
Word shingle size: `8` with short-sentence fallback
Strict normalized-full minimum words: `3`
Normalization: NFC + Turkish-aware lowercase + word-token extraction

## Summary

| Eval set | Total | Raw exact | Normalized full | Short full | Partial n-gram | Clean | Policy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| challenge | 108 | 0 | 0 | 0 | 0 | 108 | informational |
| gold | 50 | 0 | 0 | 9 | 0 | 50 | strict |

## Hit Details

Gold/frozen hits should be removed from the training corpus, not from the eval set.
Challenge hits are reported for transparency and should not be used as headline claims.

### challenge

No leakage or partial overlap hits.

### gold

- row `24` category `verb_past` flags `short_full`
  - eval: `Geldim.`
  - corpus snippet: omitted from public report
- row `25` category `verb_past` flags `short_full`
  - eval: `Gittim.`
  - corpus snippet: omitted from public report
- row `26` category `verb_past` flags `short_full`
  - eval: `Aldılar.`
  - corpus snippet: omitted from public report
- row `27` category `verb_past` flags `short_full`
  - eval: `İndiler.`
  - corpus snippet: omitted from public report
- row `28` category `verb_past` flags `short_full`
  - eval: `Durdum.`
  - corpus snippet: omitted from public report
- row `29` category `verb_past` flags `short_full`
  - eval: `Beğendim.`
  - corpus snippet: omitted from public report
- row `30` category `verb_past` flags `short_full`
  - eval: `Yaptınız.`
  - corpus snippet: omitted from public report
- row `34` category `verb_future` flags `short_full`
  - eval: `Alacaklar.`
  - corpus snippet: omitted from public report
- row `35` category `verb_future` flags `short_full`
  - eval: `Alacaksınız.`
  - corpus snippet: omitted from public report
