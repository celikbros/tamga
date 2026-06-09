# Fable5 Advisor Response Triage

Date: 2026-06-10

## Bottom Line

Fable5 agrees with our stop decisions:

```text
stop marker-dose tuning
stop seed appendix
stop broad UDS expansion
keep finite protected routing
keep safe UDS7 as a useful control/prior
```

But Fable5 challenges our proposed next step:

```text
Do not build constrained/MorphBPE yet.
First run two cheaper diagnostics:
1. finite protected wrapper cost audit
2. encode-time boundary-biased Unigram/Viterbi lambda sweep
```

I agree with this critique. It is the sharper next move.

## Key Critique 1: Wrapper Cost Is Unexplained

Fable5 points out that the protected wrapper itself is expensive:

```text
SP64 test tokens/raw byte:                  0.159620
finite protected SP64 floor test tokens/raw byte: 0.183362
increase: ~14-15%
```

That is too large to accept without decomposition. Protected spans should be a
small part of a Turkish-primary corpus.

Possible causes:

```text
protected detector over-triggers on ordinary text
finite protected encoder is too token-hungry
hard span-edge boundaries fragment adjacent prose
metric/eval cases overrepresent protected material
```

Decision:

```text
Audit wrapper cost before building MorphBPE.
```

Required audit:

```text
fraction of bytes routed through finite protected path
protected vs normal tokens/raw byte
category-level token pressure
span-edge window fragmentation
over-trigger examples
```

## Key Critique 2: 300-Step BPB May Be Too Early

Fable5 argues that a 300-step tiny-LM mostly measures compression/unigram
statistics, not morphological generalization.

This means our marker BPB results are useful but not a final verdict:

```text
marker branches lost BPB at 300 steps
but this may not detect rare-inflection generalization
```

Updated interpretation:

```text
Do not resurrect marker-dose tuning.
But avoid claiming that 300-step BPB fully disproves morphology priors.
```

Future tiny-LM improvements:

```text
matched compute
longer training
>=3 seeds for close comparisons
rare-word-heavy slice
domain-shifted slice
BPB by slice, not only aggregate
```

## Key Critique 3: Separate H1 and H2

Fable5 gives a very useful split:

```text
H1 vocabulary problem:
  morph-aligned pieces are absent from the vocabulary

H2 decoding problem:
  morph-aligned pieces exist, but Unigram/Viterbi chooses non-aligned paths
```

Our seed appendix result may suggest H2:

```text
adding suffix surfaces to training barely moved F1
therefore the issue may not be surface availability alone
```

Next diagnostic:

```text
coverage analysis of teacher morph surfaces in SP64 / safe UDS7 vocab
```

Questions to answer:

```text
what fraction of high-confidence suffix surfaces already exist as pieces?
what fraction of teacher stem/surface pieces exist?
which categories are missing from vocab?
if pieces exist, are they simply not selected at encode time?
```

## Key Critique 4: Decode-Time Boundary-Biased Viterbi Before Trainer

This is the most important recommendation.

Instead of immediately building MorphBPE, use the existing Unigram vocabulary
and modify decode/inference scoring:

```text
score(path) = unigram_score(path) + lambda * teacher_boundary_alignment(path)
```

Sweep lambda and plot:

```text
tokens/raw byte
Challenge F1
protected stress
category F1
```

Why this is attractive:

```text
no retraining
same vocabulary
directly tests whether soft morphology prior can move decode decisions
separates vocabulary availability from decoding preference
cheaper than custom trainer
```

Suggested success gate from Fable5:

```text
>= +3 F1 over finite protected floor
<= floor + 1% token-pressure cost
25/25 protected stress
```

If the lambda Pareto curve is flat or too steep:

```text
soft morphology prior likely cannot help this vocabulary enough
do not build a constrained trainer yet
```

## Updated Roadmap

Old next step:

```text
Build constrained/MorphBPE prototype.
```

New next step:

```text
1. finite protected wrapper audit
2. vocab coverage analysis
3. decode-time boundary-biased Viterbi lambda sweep
4. only then decide whether constrained/MorphBPE is worth building
```

## Updated Kill Criteria

We should precommit stop conditions.

Accept the null or deprioritize morphology-prior work if:

```text
wrapper audit shows most cost is unavoidable
coverage analysis shows morph pieces are present but unused
lambda sweep cannot reach >= +3 F1 over floor at <= floor + 1% token pressure
rare-word/domain-shift slices show no advantage
```

In that case:

```text
ship finite_protected + safe UDS7 as experimental v2.0 baseline
or hand it to LLM team only as a protected-aware SP baseline, not as a
full morphology-aware breakthrough
```

## My Recommendation

Follow Fable5's sequence.

Do not implement MorphBPE yet.

Immediate implementation order:

```text
1. wrapper cost audit script
2. SP64/safe-UDS vocab coverage script
3. if coverage suggests decode issue, implement boundary-biased Viterbi sweep
```

This is the first time the next step is not "try another tokenizer variant" but
"diagnose the mechanism." That is healthier for the project.
