# JSONL Corpus Quality Audit

Path: `data\train\private\celik_ai\celik_gold_corpus.jsonl`
Text field: `text`
Scan limit: `100000`

This report is aggregate-only. It does not publish corpus text.

## Structure

| Metric | Count | Rate |
| --- | ---: | ---: |
| scanned_lines | 100000 | 1.0000 |
| valid_json | 100000 | 1.0000 |
| invalid_json | 0 | 0.0000 |
| missing_text | 0 | 0.0000 |
| empty_text | 0 | 0.0000 |
| usable_texts | 100000 | 1.0000 |

## Quality Signals

| Signal | Count | Rate over usable |
| --- | ---: | ---: |
| exact_duplicates_in_scan | 0 | 0.0000 |
| normalized_duplicates_in_scan | 0 | 0.0000 |
| very_short_texts | 3 | 0.0000 |
| chars_over_4192 | 1585 | 0.0158 |
| chars_over_20000 | 456 | 0.0046 |
| mojibake_suspects | 25 | 0.0003 |
| replacement_char_texts | 3 | 0.0000 |
| url_texts | 0 | 0.0000 |
| html_texts | 0 | 0.0000 |
| control_char_texts | 706 | 0.0071 |

## Lengths

| Metric | Value |
| --- | ---: |
| min_chars | 51 |
| median_chars | 831.0 |
| avg_chars | 1201.8 |
| max_chars | 177353 |
| avg_words | 157.4 |

## Language Hints

| Value | Count | Rate |
| --- | ---: | ---: |
| tr_like | 84378 | 0.8438 |
| mixed_tr_en | 15472 | 0.1547 |
| unknown | 150 | 0.0015 |

## Script Hints

| Value | Count | Rate |
| --- | ---: | ---: |
| latin | 99998 | 1.0000 |
| mixed_script | 2 | 0.0000 |

## Sources

| Value | Count | Rate |
| --- | ---: | ---: |
| dergipark_oai | 45208 | 0.4521 |
| ttk_belleten_2022 | 367 | 0.0037 |
| ttk_belleten_422 | 349 | 0.0035 |
| ttk_belleten_1680 | 277 | 0.0028 |
| ttk_belleten_1435 | 269 | 0.0027 |
| ttk_belleten_1797 | 261 | 0.0026 |
| ttk_belleten_2086 | 259 | 0.0026 |
| ttk_belleten_1873 | 239 | 0.0024 |
| ttk_belleten_331 | 238 | 0.0024 |
| ttk_belleten_46 | 234 | 0.0023 |
| ttk_belleten_1457 | 226 | 0.0023 |
| ttk_belleten_1633 | 221 | 0.0022 |
| ttk_belleten_2206 | 221 | 0.0022 |
| ttk_belleten_103 | 212 | 0.0021 |
| ttk_belleten_2127 | 209 | 0.0021 |
| ttk_belleten_1687 | 204 | 0.0020 |
| ttk_belleten_1557 | 203 | 0.0020 |
| ttk_belleten_2136 | 202 | 0.0020 |
| trt_news | 200 | 0.0020 |
| ttk_belleten_2291 | 200 | 0.0020 |

## Interpretation Notes

- Language hints are heuristic counts, not a certified language-ID model.
- `mojibake_suspects` flags actual marker characters in parsed text; terminal
  mojibake alone is not counted.
- `chars_over_4192` matters because SentencePiece skipped longer lines in the
  local pilot unless max sentence length is changed or pre-filtering is added.
- Exact/normalized duplicate counts are only within the scanned slice.
