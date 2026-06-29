# v3.1 Ablation Split

Input: `C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt`
Output dir: `artifacts/private/v3_1_vocab_ablation_split`
Seed: `20260618`
Split parts: `8:1:1`

This split is for local vocab-size ablation only. It is not the final
Gardaş tokenizer training corpus.

## Summary

| Split | Lines | Bytes | Path |
| --- | ---: | ---: | --- |
| train | 32311 | 35511533 | `artifacts/private/v3_1_vocab_ablation_split/train.txt` |
| valid | 4039 | 4404796 | `artifacts/private/v3_1_vocab_ablation_split/valid.txt` |
| test | 4038 | 4435472 | `artifacts/private/v3_1_vocab_ablation_split/test.txt` |
