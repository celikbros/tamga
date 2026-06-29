# v3.1 Ablation Split

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_4_sample/stratified_480mb.txt`
Output dir: `artifacts/private/v3_4_stratified_480mb_ablation_split`
Seed: `20260619`
Split parts: `8:1:1`

This split is for local vocab-size ablation only. It is not the final
Gardaş tokenizer training corpus.

## Summary

| Split | Lines | Bytes | Path |
| --- | ---: | ---: | --- |
| train | 398469 | 396217280 | `artifacts/private/v3_4_stratified_480mb_ablation_split/train.txt` |
| valid | 49809 | 49279753 | `artifacts/private/v3_4_stratified_480mb_ablation_split/valid.txt` |
| test | 49808 | 50024285 | `artifacts/private/v3_4_stratified_480mb_ablation_split/test.txt` |
