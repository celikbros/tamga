# v3.1 Vocab Ablation Findings

Date: 2026-06-18

## Status

Internal finding. Do not treat this as the final Gardaş tokenizer decision.

This run uses a 40k-line real-mix sample split, not the full 26 GB pretraining
corpus.

## Split

Source:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_0\real_mix_60k_sample.txt
```

Split:

| Split | Lines | Bytes |
| --- | ---: | ---: |
| train | 32311 | 35511533 |
| valid | 4039 | 4404796 |
| test | 4038 | 4435472 |

Report:

```text
artifacts/v3_1_vocab_ablation_split.md
```

## Token Pressure Results

All rows:

```text
model_type = unigram
normalization = identity
split_by_whitespace = true
remove_extra_whitespaces = false
max_sentence_length = 16384
```

| Candidate | Valid tokens/raw byte | Test tokens/raw byte | Test delta vs 64K | Relative test delta |
| --- | ---: | ---: | ---: | ---: |
| 32K | 0.173989 | 0.172849 | +0.010920 | +6.7449% |
| 48K | 0.166805 | 0.165755 | +0.003826 | +2.3626% |
| 64K | 0.162830 | 0.161929 | baseline | baseline |

## Embedding Parameter Trade-Off

Ignoring extra chat/tool control tokens and counting only SP vocab difference:

| Move | Vocab ids saved | Params saved at hidden=1024 | Params saved at hidden=2048 |
| --- | ---: | ---: | ---: |
| 64K -> 48K | 16000 | 16.384M | 32.768M |
| 64K -> 32K | 32000 | 32.768M | 65.536M |

## Reading

32K looks too expensive on this sample:

```text
+6.74% test token pressure versus 64K
```

48K is the interesting candidate:

```text
+2.36% test token pressure versus 64K
32.8M embedding params saved at hidden=2048
```

This is close enough that 48K deserves the next confirmation step before we
declare 64K final.

## Caveats

This is not final because:

```text
sample is 44 MB, not the full 26 GB corpus
special tokens are not embedded/frozen
sidecar wrapper/fallback is not included in the raw SP pressure table
no BPB comparison yet
no LLM dataloader smoke for 48K yet
```

## Recommendation

Do not use 32K for the main branch unless a much larger-corpus run contradicts
this sample.

Keep both 48K and 64K alive:

```text
48K = parameter-efficient candidate
64K = compression/fertility reference
```

Next step:

```text
Run v3.1 sidecar smoke and fertility on 48K and 64K with the same special-token
policy. If 48K stays within ~2-3% token pressure and BPB is not worse, prefer
48K for Gardaş.
```
