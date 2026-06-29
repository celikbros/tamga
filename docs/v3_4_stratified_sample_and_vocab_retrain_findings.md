# v3.4 Stratified Sample And Vocab Retrain Findings

Date: 2026-06-19

## Status

v3.4 tested whether the current 44MB real-mix-trained tokenizer candidates are
too narrow for the broader Gardaş pretraining corpus.

The answer is yes:

```text
the broader corpus is noisier and more protected-span dense
larger stratified tokenizer training materially reduces token pressure
64K remains more robust than 48K on this broader sample
```

This does not cancel v3.2/v3.3. It means v3.2 remains the integration-smoke
candidate, while final training should not be frozen from the 44MB model alone.

## Stratified Sample

Output:

```text
C:\CELIK-GARDASH\datasets\tokenizer_v3_4_sample\stratified_480mb.txt
```

Materialization report:

```text
artifacts/v3_4_stratified_480mb_sample_materialization.md
```

| Metric | Value |
| --- | ---: |
| target bytes | 505413632 |
| output bytes | 496019404 |
| output size | 473.04 MiB |
| written lines | 498086 |

The sample uses deterministic byte-region chunks across multiple corpus files
instead of prefix-only reads.

## Source Mix

| Source | Target bytes | Written bytes | Written lines |
| --- | ---: | ---: | ---: |
| `trt_news` | 2097152 | 552129 | 200 |
| `academic` | 33554432 | 33555794 | 24057 |
| `ttk` | 50331648 | 50332217 | 38799 |
| `tdk` | 16777216 | 8921058 | 98604 |
| `wiki_oscar` | 167772160 | 167773096 | 55484 |
| `celik_gold` | 167772160 | 167775782 | 56809 |
| `tr_corpus` | 67108864 | 67109328 | 224133 |

## Route-Density Finding

Route-density report:

```text
artifacts/v3_4_stratified_480mb_route_density.md
```

| Metric | v3.3 real-mix | v3.4 stratified |
| --- | ---: | ---: |
| raw bytes | 44351801 | 495521318 |
| protected spans | 149999 | 3175697 |
| protected bytes/raw byte | 0.015398 | 0.028715 |

v3.4 exposed route classes that were absent or rare in the v3.3 real-mix
fixture:

```text
url
technical_comparator
```

Decision:

```text
Add url and technical_comparator to the protected sidecar route contract and
SP passthrough route list.
```

The route-expanded v3.2 config validates successfully:

```text
artifacts/v3_4_tokenizer_config_validation_route_expanded_sp48k_gardash.md
```

## 50K Fertility Window

The first 50K lines of the stratified sample are substantially harder than the
old real-mix sample.

| Model | Train source | Vocab | Tokens/word | Tokens/raw byte | Fallback rate |
| --- | --- | ---: | ---: | ---: | ---: |
| v3.1 48K | 44MB real-mix | 48000 | 1.730602 | 0.207934 | 0.004945 |
| v3.1 64K | 44MB real-mix | 64000 | 1.681739 | 0.202063 | 0.005089 |

The high-fertility rows are mostly URLs, code-like strings, glued web text,
foreign scripts, and formatting artifacts. This is useful stress evidence, not
only Turkish morphology evidence.

## v3.4 Split

Split report:

```text
artifacts/v3_4_stratified_480mb_ablation_split.md
```

| Split | Lines | Bytes |
| --- | ---: | ---: |
| train | 398469 | 396217280 |
| valid | 49809 | 49279753 |
| test | 49808 | 50024285 |

## SentencePiece Retrain Result

48K and 64K Unigram models were trained on the v3.4 train split.

| Model | Train source | Vocab | Valid tokens/raw byte | Test tokens/raw byte |
| --- | --- | ---: | ---: | ---: |
| v3.1 48K | 44MB real-mix | 48000 | 0.205437 | 0.208279 |
| v3.4 48K | 396MB stratified train | 48000 | 0.189704 | 0.191431 |
| v3.1 64K | 44MB real-mix | 64000 | 0.199638 | 0.202412 |
| v3.4 64K | 396MB stratified train | 64000 | 0.183092 | 0.184767 |

Retrain gain on v3.4 test:

| Vocab | Test tokens/raw byte delta | Relative |
| ---: | ---: | ---: |
| 48K | -0.016848 | -8.09% |
| 64K | -0.017645 | -8.72% |

v3.4 64K versus v3.4 48K:

```text
0.184767 - 0.191431 = -0.006664 tokens/raw byte
about 3.5% lower token pressure for 64K
```

## Interpretation

The 44MB real-mix models were good enough for integration smoke, but too narrow
to freeze as final tokenizer models.

The broader v3.4 sample changes the decision surface:

```text
48K is still attractive for integration smoke and parameter budget.
64K is more robust on broader/noisier corpus coverage.
larger tokenizer-training data matters more than another small v3.1 smoke.
```

## Decision

Do not freeze the 44MB-trained 48K model as final.

Keep:

```text
v3.2/v3.3 48K = integration-smoke candidate
v3.4 48K/64K = larger-corpus tokenizer candidates for next evaluation
```

## Next

v3.5 should evaluate the v3.4-trained 48K and 64K models through the same
protected sidecar path:

```text
1. create v3.4 sidecar configs for both models
2. run full fixture validation on the v3.4 test split or full stratified sample
3. run binary dataloader simulation
4. run fixed-byte tiny-LM BPB comparison if both pass
5. then decide whether 64K's robustness is worth the embedding-size cost
```
