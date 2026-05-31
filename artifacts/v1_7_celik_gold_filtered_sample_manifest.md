# v1.7 Claim-Grade Corpus Manifest

Config: `configs/v1_7_celik_gold_filtered_sample.toml`
Output path: `data/train/claim_grade/celik_gold_filtered_pilot.txt`
Mode: `prepare-sample`
Min chars: `80`
Max chars: `4192`
Max UTF-8 bytes: `4192`
Drop control chars: `True`
Drop replacement char: `True`
Drop mojibake suspects: `True`
Dedupe exact: `True`
Dedupe normalized: `True`

Large corpus text is private/local and must not be committed to git.

## Sources

| Source | Format | Bytes | Scanned | Usable | Filtered | Duplicates | Written | Truncated |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| celik_gold_corpus_jsonl | jsonl | 12.11 GiB | 120001 | 120000 | 7779 | 11 | 100000 | True |

## Filter Details

| Source | Short | Long chars | Long bytes | Control | Replacement | Mojibake | Exact dup | Normalized dup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| celik_gold_corpus_jsonl | 4329 | 2466 | 217 | 744 | 2 | 21 | 0 | 11 |
