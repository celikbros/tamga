# v3.6 Stratified Fixed-Byte BPB Findings

Date: 2026-06-19

## Status

v3.6 compared the v3.4-trained 48K and 64K protected-passthrough sidecar
tokenizers at approximately the same raw-byte budget.

This is still a tiny-LM screening result, not final production LLM evidence.

## Candidates

| Candidate | Effective vocab | Model params | Embedding params | Non-embedding params |
| --- | ---: | ---: | ---: | ---: |
| sp48k stratified sidecar | 48256 | 15545856 | 12386304 | 3159552 |
| sp64k stratified sidecar | 64256 | 19641856 | 16482304 | 3159552 |

The 64K row has about:

```text
16482304 - 12386304 = 4096000
```

more embedding parameters in this tiny-LM setup.

## Token Pressure

| Candidate | Train tokens/raw byte | Valid tokens/raw byte | Test tokens/raw byte | Test fallback rate |
| --- | ---: | ---: | ---: | ---: |
| sp48k stratified sidecar | 0.191076 | 0.190735 | 0.192455 | 0.000200 |
| sp64k stratified sidecar | 0.184332 | 0.184123 | 0.185791 | 0.000207 |

64K lowers test token pressure by:

```text
0.192455 - 0.185791 = 0.006664 tokens/raw byte
about 3.46% relative to 48K
```

## Fixed-Byte Tiny-LM Result

| Candidate | Steps | Approx bytes seen | Valid BPB | Test BPB | Test bits/token |
| --- | ---: | ---: | ---: | ---: | ---: |
| sp48k stratified sidecar | 7464 | 20000276 | 2.363120 | 2.386732 | 12.4015 |
| sp64k stratified sidecar | 7200 | 19998662 | 2.316947 | 2.340260 | 12.5962 |

64K improves test BPB by:

```text
2.386732 - 2.340260 = 0.046472 BPB
about 1.95% relative to 48K
```

## Reading

The 64K model wins this v3.6 selection screen.

The result is especially useful because it is not just a token-pressure win:

```text
64K has fewer tokens/raw byte
and
64K has lower fixed-byte BPB
```

The 64K row has higher bits/token, which is expected with fewer, broader
tokens. The byte-normalized result is the relevant comparison here.

## Decision

Promote the v3.4-trained 64K sidecar model as the current v3.x tokenizer
candidate for the next integration-smoke package.

Do not delete or invalidate the 48K path. Keep it as the smaller-embedding
fallback if the LLM architecture has a hard embedding-size constraint.

## Reports

```text
artifacts/v3_6_tiny_lm_sp48k_stratified_480mb_dry_run.md
artifacts/v3_6_tiny_lm_sp64k_stratified_480mb_dry_run.md
artifacts/v3_6_tiny_lm_sp48k_stratified_480mb_20m.md
artifacts/v3_6_tiny_lm_sp64k_stratified_480mb_20m.md
```

## Next

Build a v3.7 64K integration candidate:

```text
1. create a handoff config with SP64K + byte fallback + control ids
2. generate a full fixture on the stratified sample or a large heldout subset
3. validate exact roundtrip, token id ranges, loss mask, sidecar offsets
4. simulate binary dataloader consumption
5. copy the candidate package to C:\CELIK-GARDASH
```
