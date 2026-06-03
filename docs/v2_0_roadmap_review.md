# v2.0 Roadmap Review

Date: 2026-06-02

## Current Position

```text
v1.x deterministic Turkish morphology core: useful but not LLM-final
v1.8 tiny-LM smoke: informative but not decisive
v2.0 direction: finite protected-aware learned hybrid
```

The project should not return to broad hand-written morphology rules now. The
main engineering problem is no longer "can we split Turkish suffixes?" It is:

```text
can we keep morphology/protection signal while reducing lossless LM token pressure?
```

## Advisor Decision

Recent advisor feedback converges on an Option 1 + Option 3 hybrid:

```text
hard pretokenization for protected spans and text regions
learned BPE/Unigram inside finite boundaries
dedicated protected-subword/byte fallback for protected spans
optional user-defined symbols for frequent protected literals/patterns
morphology as soft prior / marker / seed
plain SP64 remains the null hypothesis
```

Key invariant:

```text
LLM-safe means stateless decode(ids)
```

Rejected direction:

```text
placeholder + side-channel payload decoding
```

Reason:

```text
it is not a pure function of token IDs
generation can emit malformed placeholder sequences
it does not fit ordinary HF/vLLM-style tokenizer expectations
```

Design spec:

```text
docs/v2_0_protected_aware_tokenizer_spec.md
```

## What Is Done

Evidence and hygiene:

```text
visible eval baselines
SentencePiece sweep
eval leakage checks
tiny-LM smoke
token accounting audit
soft-morph materialization
seed vocab analysis
seed policy selection
candidate train/valid/test serialization
first candidate SentencePiece token-pressure probe
raw-hard candidate SentencePiece token-pressure probe
raw-hard candidate visible intrinsic eval
raw-soft-marker candidate token-pressure and visible intrinsic eval
advisor feedback triage for finite protected-aware architecture
```

Most important results:

```text
pure custom lossless mode is too token-expensive for direct LLM handoff
standard custom is close to SP64 in token pressure but not generation-safe
lossless+64k byte fallback is about 2.66x-2.67x SP64 tokens/byte on valid/test
64k seed policy covers 95.11% of non-whitespace seed occurrences
suffix inventory is small and cheap to seed
main remaining pressure is word_start long-tail + whitespace serialization
first token-label serialization candidate failed token-pressure gate
raw-hard candidate passed token-pressure gate
raw-hard candidate failed visible intrinsic gate
raw-soft-marker candidate improved morphology categories but failed protected
span and overall visible gates
protected-aware upper-bound diagnostic shows protection routing is the missing
piece
open-vocab protected tokens are diagnostic only, not final LLM-safe design
finite protected encoder + soft-marker model passes the visible morphology and
protected-span intrinsic gate
finite protected encoder + soft-marker model has valid/test token pressure
around 0.249 tokens/raw byte, well below pure custom lossless but above SP64
```

## Candidate 1: Rejected

```text
protected_hard_soft_morph_seeded_sp64
```

Policy:

```text
hard boundaries: whitespace/protected/script/punctuation
soft boundaries: morphology suffix boundaries
seed all suffix tokens
seed punctuation/symbol tokens
seed protected surface tokens only when count >= 10
seed top word_start pieces up to 64k budget
do not seed the word_start long-tail by default
learned tokenizer must handle long-tail without byte fallback explosion
```

Intrinsic probe result:

```text
report: artifacts/v2_0_candidate_sentencepiece_probe.md
valid/test SP tokens/raw byte: 0.398475 / 0.397593
SP64 baseline valid/test: about 0.1566 / 0.1570
custom lossless+64k valid/test: about 0.4162 / 0.4194
decision: reject before tiny-LM screening
```

Why it failed:

```text
the train view serialized custom token labels and morphology markers
view bytes/raw byte was about 1.51
SentencePiece learned over the synthetic view, not over raw surface text
token pressure stayed much closer to pure custom lossless than SP64
```

Additional hygiene note:

```text
the first SP run skipped 603 too-long train-view lines at the default
SentencePiece max_sentence_length; future configs set max_sentence_length=16384
```

## Candidate 2: Rejected Before Tiny-LM

```text
protected_hard_raw_sp64
```

Policy:

```text
hard boundaries remain train-view whitespace
soft morphology boundaries collapse back into raw surface text
custom token labels are not serialized into the learned-tokenizer view
morphology remains metadata/diagnostic signal, not mandatory token pressure
```

Intrinsic token-pressure result:

```text
view report: artifacts/v2_0_raw_hard_candidate_views.md
SP report: artifacts/v2_0_raw_hard_candidate_sentencepiece_probe.md
view/raw bytes train/valid/test: 1.020919 / 1.020813 / 1.020957
valid/test SP tokens/raw byte: 0.162884 / 0.163117
SP64 baseline valid/test: about 0.1566 / 0.1570
custom lossless+64k valid/test: about 0.4162 / 0.4194
decision: passes token-pressure gate
```

Interpretation:

```text
raw-hard serialization removed the artificial token-label pressure
the learned tokenizer is now close to SP64 compression
the candidate was worth Phase 3 intrinsic diagnostics
```

Visible intrinsic result:

```text
report: artifacts/v2_0_raw_hard_candidate_intrinsic_eval.md
gold boundary F1: 0.5931
challenge boundary F1: 0.5951
SP64 reference challenge boundary F1: 0.7351
protected span preservation: 1/25
decision: reject before tiny-LM screening
```

Why it failed:

```text
collapsing all soft morphology boundaries restored compression but removed the
main morphology advantage
protected spans were only metadata; SentencePiece still split almost all of
them
the candidate is a useful compression control, not an acceptable tokenizer
```

## Current Candidate Need

```text
unnamed next hybrid candidate
```

Required behavior:

```text
keep raw-hard level token pressure near SP64
make protected spans operational, not just metadata
recover at least part of custom morphology boundary advantage
avoid serializing custom token labels into the training view
avoid arbitrary open-vocabulary tokens as fixed model IDs
```

## Candidate 3: Rejected Before Tiny-LM

```text
protected_hard_soft_marker_raw_sp64
```

Policy:

```text
hard boundaries remain train-view whitespace
soft morphology boundaries are represented by a private-use marker
raw surface text is preserved around the marker
custom token labels such as word-start markers and suffix prefixes are not
serialized
```

Rationale:

```text
candidate 1 kept morphology but serialized custom token labels and was too
expensive
candidate 2 restored compression but erased morphology signal
candidate 3 tests whether a minimal soft-boundary marker can recover visible
boundary behavior without returning to pure custom token pressure
```

Results:

```text
view report: artifacts/v2_0_raw_soft_marker_candidate_views.md
SP report: artifacts/v2_0_raw_soft_marker_candidate_sentencepiece_probe.md
intrinsic report: artifacts/v2_0_raw_soft_marker_candidate_intrinsic_eval.md
valid/test SP tokens/raw byte: 0.236749 / 0.236700
challenge boundary F1: 0.6724
SP64 reference challenge boundary F1: 0.7351
protected span preservation: 1/25
decision: reject before tiny-LM screening
```

Protected-aware upper-bound diagnostic:

```text
same report: artifacts/v2_0_raw_soft_marker_candidate_intrinsic_eval.md
protected-aware challenge boundary F1: 0.8259
protected-aware protected span preservation: 25/25
protected-aware multilingual smoke F1: 0.8015
interpretation: operational protection routing is necessary
caveat: this row uses protected spans as atomic source tokens and is not a
final finite-vocabulary LLM design
```

Interpretation:

```text
soft markers recover useful morphology signal in suffix-heavy categories
but the overall challenge score remains below SP64
protected spans remain broken because they are still not operationally forced
the next candidate must solve protection at encode/vocab level
```

## Current Candidate Need

```text
finite protected-aware learned candidate
```

Required behavior:

```text
protected spans are losslessly shielded during learned tokenization
protected handling must not depend on arbitrary open-vocabulary IDs
decode(ids) must remain stateless
protected spans need a finite protected-subword/byte fallback path
frequent protected literals/patterns may be promoted as user-defined symbols
compression should stay closer to raw-hard than pure custom
morphology hints may be soft markers or metadata, but they cannot break
protected spans
```

Immediate next step:

```text
use the finite protected-aware tokenizer design/spec before another candidate
protected categories
protected internal encoding strategy
byte fallback token set
UDS promotion policy
decode invariants
evaluation gates
```

First implementation support:

```text
scripts/materialize_v2_protected_routes.py
scripts/analyze_v2_protected_route_inventory.py
scripts/select_v2_protected_piece_vocab.py
scripts/evaluate_v2_protected_encoder.py
```

Purpose:

```text
record protected route labels and protected suffix tails from train-only data
before selecting finite protected pieces or user-defined symbols
```

Protected inventory finding:

```text
report: artifacts/v2_0_protected_route_inventory_analysis.md
protected unique surfaces: 29811
protected occurrences: 96132
numeric_like occurrence share: 0.677111
file_like occurrence share: 0.101891
non_turkish_latin_word occurrence share: 0.157637
min-count 10 full-surface UDS coverage: 0.532923
decision: full-surface UDS is not the main solution
next: finite protected subword pieces plus byte fallback
```

Protected piece selection finding:

```text
report: artifacts/v2_0_protected_piece_vocab_selection.md
selected unique protected pieces: 374
mandatory byte fallback pieces: 256
candidate unique pieces: 2741
selected weighted coverage: 0.993236
unused protected-piece budget at 4096 cap: 3722
decision: start with a small protected char/extension piece set, then byte fallback
```

Protected encoder diagnostic:

```text
report: artifacts/v2_0_protected_encoder_diagnostic.md
selected protected pieces: 374
mandatory byte fallback pieces: 256
protected encoded tokens/source byte: 0.853723
overall byte fallback byte rate: 0.002679
file_like byte fallback byte rate: 0.000000
numeric_like byte fallback byte rate: 0.000018
decision: finite protected-piece path is viable for a full tokenizer prototype
```

Finite protected + plain SP64 intrinsic prototype:

```text
report: artifacts/v2_0_finite_protected_sp64_intrinsic_eval.md
normal text encoder: train-only SP64 Unigram
protected encoder: 374 finite protected pieces + UTF-8 byte fallback
protected span stress: 25/25 preserved
challenge boundary F1: 0.6913
SP64 challenge boundary F1: 0.7351
custom challenge boundary F1: 0.9220
decision: protected path works, but plain SP64 loses too much morphology signal
next: combine finite protected encoder with a soft-morph learned prior
```

Finite protected + soft-marker intrinsic prototype:

```text
report: artifacts/v2_0_finite_protected_soft_marker_intrinsic_eval.md
normal text encoder: train-only soft-marker Unigram model
protected encoder: 374 finite protected pieces + UTF-8 byte fallback
protected span stress: 25/25 preserved
challenge boundary F1: 0.8259
SP64 challenge boundary F1: 0.7351
custom challenge boundary F1: 0.9220
multilingual smoke F1: 0.8015
decision: morphology/protection gate passes intrinsically
open gate: measure split-level token pressure before tiny-LM
```

Finite protected + soft-marker token pressure:

```text
report: artifacts/v2_0_finite_protected_soft_marker_token_pressure.md
valid/test model tokens/raw byte: 0.249142 / 0.249758
raw-soft-marker valid/test tokens/raw byte: about 0.2367 / 0.2367
SP64 valid/test tokens/raw byte: about 0.1566 / 0.1570
pure custom lossless+64k valid/test tokens/raw byte: about 0.4162 / 0.4194
decision: token-pressure gate is conditionally acceptable for a narrow
tiny-LM screen, but the candidate carries a clear compression penalty versus
SP64 and must not be represented as final
```

Narrow tiny-LM dry-run:

```text
config: configs/v2_0_tiny_lm_finite_protected_soft_marker_probe.toml
report: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_dry_run.md
finite protected soft-marker valid/test tokens/raw byte: 0.251658 / 0.252212
SP64 null valid/test tokens/raw byte: 0.159020 / 0.159620
training run: not executed yet
decision: infrastructure is ready for one narrow BPB screen, not a broad matrix
```

Narrow tiny-LM smoke:

```text
findings: docs/v2_0_tiny_lm_finite_protected_soft_marker_findings.md
200-step report: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_200steps.md
finite 321-step iso-byte report: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_finite_321_iso_byte.md
SP64 321-step control: artifacts/v2_0_tiny_lm_finite_protected_soft_marker_probe_sp64_321steps.md
fixed-token 200-step test BPB: finite=7.067777, SP64=5.966637
approx iso-byte test BPB: finite_321=5.263920, SP64_200=5.966637
same-step 321-step test BPB: finite=5.263920, SP64=4.629442
interpretation: fixed-token view favors SP64, approximate iso-byte view favors
the finite protected soft-marker candidate
caveat: iso-byte is not iso-compute; the candidate used more tokens/steps to
see the same raw bytes
decision: do not hand off; do not discard; stop broad LM probing for this
candidate and reduce token pressure next
```

## Roadmap

### Phase 1: Candidate Serialization

Goal:

```text
turn the selected seed policy + soft/hard boundary JSONL into a training-ready
prototype corpus
```

Deliverables:

```text
private candidate training corpus
public serialization report
roundtrip design note
tokens/byte estimate before training
```

Current script:

```text
scripts/materialize_v2_candidate_serialization.py
scripts/materialize_v2_candidate_split_views.py
scripts/run_v2_candidate_sentencepiece_probe.py
scripts/materialize_v2_raw_hard_candidate_views.py
scripts/evaluate_v2_raw_hard_candidate_intrinsic.py
scripts/materialize_v2_raw_soft_marker_candidate_views.py
scripts/evaluate_v2_soft_marker_candidate_intrinsic.py
```

Current output:

```text
artifacts/v2_0_candidate_serialization.md
artifacts/v2_0_candidate_split_views.md
hard segments/raw byte: 0.130918
valid hard segments/raw byte: 0.130737
test hard segments/raw byte: 0.130560
train-view/raw bytes: 1.511092
```

Phase 1 status:

```text
train/valid/test candidate views are materialized
token-label serialization candidate failed Phase 2 token-pressure gate
raw-hard serialization candidate passed Phase 2 token-pressure gate
raw-hard candidate failed Phase 3 visible intrinsic gate
raw-soft-marker candidate failed Phase 3 visible intrinsic gate
```

Gate:

```text
do not train a tokenizer if the serialization itself cannot be decoded losslessly
or if it already looks close to pure custom token pressure
do not evaluate a learned tokenizer on train-only serialization
```

### Phase 2: Learned Tokenizer Prototype

Goal:

```text
train one small learned tokenizer candidate using the candidate serialization
```

Initial candidate:

```text
protected-aware learned candidate
```

Control baselines:

```text
custom_tr_morph_lossless
sp_bpe_64000_train_only
hybrid_hard_unigram_64000
```

Gate:

```text
candidate must materially reduce tokens/byte versus custom_lossless_64000_byte_fallback
candidate must not destroy protected-span behavior
candidate must keep visible boundary F1 advantage over SP64
do not proceed to tiny-LM if token pressure remains near 0.40 tokens/raw byte
```

Current Phase 2 status:

```text
protected_hard_raw_sp64 passes the token-pressure part of the gate
protected_hard_raw_sp64 fails protected-span and visible-boundary diagnostics
do not run tiny-LM on protected_hard_raw_sp64
finite protected + soft-marker passes protected-span and visible-boundary
diagnostics, and token pressure is far from pure custom lossless
finite protected + soft-marker still costs about 59% more model tokens/raw byte
than SP64 on valid/test
```

### Phase 3: Intrinsic Evaluation

Run only after one candidate exists:

```text
roundtrip
tokens/byte
avg tokens/word
byte fallback/source fallback rate
protected span break rate
boundary F1 on gold/challenge
canary diagnostics
```

Current rejected candidate:

```text
protected_hard_raw_sp64
```

Gate:

```text
if protected span break rate is nonzero, fix serialization before LM probes
if tokens/byte is still close to pure custom, redesign candidate before LM probes
```

### Phase 4: Tiny-LM Screening

Run only for the best 1-2 candidates.

Budget views:

```text
fixed-token/fixed-step
approx iso-byte
optional iso-compute control if results are close or advisor asks
```

Gate:

```text
do not treat tiny-LM as final LLM proof
do not hand off if candidate loses badly on both fixed-token and iso-byte views
```

### Phase 5: Experimental Handoff Package

Only if Phase 2-4 pass:

```text
tokenizer artifact
training recipe
roundtrip/protected-span report
baseline comparison table
tiny-LM BPB report
known limitations
integration notes for LLM team
```

This handoff is experimental, not final production approval.

## Stop Conditions

Stop or redesign the v2.0 candidate if:

```text
lossless roundtrip fails
protected spans break
tokens/byte remains near pure custom
word_start long-tail still falls to byte fallback heavily
implementation requires hand-writing Turkic morphology for each language
```

## What Not To Do Now

```text
do not expand Turkish rules against visible challenge examples
do not train a full LLM
do not build Turkic morphology layers
do not send pure custom as final LLM tokenizer
do not seed every protected surface form
do not run broad tiny-LM matrices before a real v2.0 candidate exists
```

## Next Immediate Step

Run a narrow Phase 4 decision step, not a broad matrix:

```text
decide whether to run one tiny-LM screen:
finite_protected_soft_marker vs SP64 null baseline
report fixed-token and approximate iso-byte views
state the token-pressure penalty before interpreting BPB
```

The current finite protected soft-marker candidate is the first candidate that
passes the intrinsic gate strongly enough to justify considering a narrow
tiny-LM screen. It is not an LLM handoff candidate yet.

After the first smoke, the immediate question is no longer "does morphology
ever help?" but:

```text
can the candidate keep the iso-byte BPB gain while lowering token pressure
toward SP64?
```

Do not continue by adding more tiny-LM rows for the same candidate. The result
already exposes the tradeoff clearly enough for the next design iteration.

Selective marker next step:

```text
plan: docs/v2_0_selective_soft_marker_plan.md
advisor request: docs/advisor_request_v2_0_selective_soft_marker.md
goal: keep boundary/protected gains while reducing valid/test tokens/raw byte
preferred target: <=0.20
maximum for next tiny-LM screen: <=0.22
```

Marker-stripped mechanism check:

```text
report: artifacts/v2_0_marker_stripped_soft_marker_diagnostic.md
findings: docs/v2_0_marker_stripped_soft_marker_findings.md
valid/test tokens/raw byte: 0.195611 / 0.196236
challenge F1: 0.7703
protected stress: 25/25
interpretation: marker cost is largely in-stream; train-only vocab shaping is
promising but current F1 is below the preferred gate
decision: prioritize train-view vocab-shaping/constrained-Unigram style sweep;
do not tiny-LM this candidate yet
```
