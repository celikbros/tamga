# v1.7 SentencePiece Sweep Findings

Date: 2026-06-01

## Scope

This note summarizes the visible-set SentencePiece sweep trained on:

`data/train/claim_grade/celik_gold_clean_pilot.txt`

The sweep is useful for baseline pressure-testing, but it is not hidden-eval or
downstream LLM-quality evidence.

## Main Finding

The custom Turkish morphology-aware tokenizer keeps a clear boundary-F1 lead
over SentencePiece BPE/Unigram across the tested vocabulary range.

On `tr_challenge.tsv`, the closest fertility comparison is:

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.1749 | 0.9220 | 44/108 |
| sp_bpe_32000_celik_gold_clean | 2.1645 | 0.6819 | 0/108 |
| sp_unigram_32000_celik_gold_clean | 2.1932 | 0.7353 | 0/108 |

The best SentencePiece boundary-F1 on `tr_challenge.tsv` is:

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| sp_unigram_8000_celik_gold_clean | 2.5953 | 0.7369 | 0/108 |

Even when SentencePiece gets a much larger vocabulary, boundary F1 does not
approach the custom tokenizer:

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| sp_bpe_64000_celik_gold_clean | 1.9817 | 0.6926 | 0/108 |
| sp_unigram_64000_celik_gold_clean | 2.0078 | 0.7327 | 0/108 |

## Frozen Regression Set

On `tr_gold_expanded.tsv`, the custom tokenizer remains at the policy target:

| Model | Avg tokens/word | Boundary F1 | Exact match |
| --- | ---: | ---: | ---: |
| custom_tr_morph | 2.7438 | 1.0000 | 50/50 |
| sp_unigram_16000_celik_gold_clean | 2.7355 | 0.7425 | 0/50 |
| sp_bpe_64000_celik_gold_clean | 2.3140 | 0.6992 | 2/50 |
| sp_unigram_64000_celik_gold_clean | 2.3223 | 0.7329 | 2/50 |

This is expected to favor the policy tokenizer and should be treated as
regression/spec conformance, not independent quality proof.

## Interpretation

The result supports a narrow claim:

> On visible Turkish morphology-focused eval sets, the custom tokenizer preserves
> morpheme-like boundaries substantially better than SentencePiece BPE/Unigram,
> including at similar token fertility.

The result does not yet prove:

- Better downstream LM loss or bits-per-byte.
- Hidden-eval generalization.
- Production multilingual robustness.

## Next Decision

The next useful step is to prepare a small LLM-side probe package:

1. Use the sweep reports as intrinsic baseline evidence.
2. Keep leakage results attached as methodology hygiene.
3. Ask the LLM team to run a tiny byte-normalized LM probe comparing:
   - current project tokenizer,
   - best SP Unigram baseline,
   - best SP BPE baseline,
   - existing production tokenizer if available.

No new Turkish morphology rule should be added from this sweep alone.
