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

Latest diagnostic update:

```text
finite_protected_sp64_numeric_sp_floor is the active protected null baseline
morph-vocab coverage shows SP64 already contains most high-value morph surfaces
boundary-biased Unigram decode is promising but attribution is unresolved
because lambda 0 already differs from official SentencePiece / the protected
floor
lambda 4 currently raises Challenge F1 from 0.6913 to 0.7701 at near-floor token
pressure, but this mixes decoder/pipeline effect with morphology penalty effect
tiny-LM shows lambda 4 is BPB-positive vs SP64 and protected floor in the
300-step screen:
  lambda 0 test BPB: 4.769027
  lambda 4 test BPB: 4.721480
  SP64 test BPB: 4.860352
  protected floor test BPB: 4.911037
lambda 0 explains most of the protected-floor -> lambda4 BPB gain; lambda4
still improves over lambda0 by -0.047547 test BPB and +0.0279 Challenge F1
lambda 8 is high-F1 and still slightly BPB-positive vs SP64, but less efficient
than lambda 4
next branch is blocked on correctness/generalization controls: decoder
alignment audit, roundtrip/stateless decode, separated morphology/protected
metrics, and longer/seeded lambda0-vs-lambda4 BPB
```

Follow-up advisor consensus after lambda 0 decomposition and roundtrip smoke:

```text
boundary-biased runtime decode is diagnostic-only until exact roundtrip passes
0/20 roundtrip on lambda0/lambda4 blocks all longer BPB
lambda4 must not be promoted or handed off
the next high-value work is roundtrip failure classification and wrapper-tax
reduction on clean no-protected lines
if the runtime fix is not local/trivial, move the morphology prior into a
boundary-weighted Unigram / constrained training objective instead
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
lossless protected wrapper and diagnostic morphology-prior path
```

Required behavior:

```text
keep raw-hard level token pressure near SP64
make protected spans operational, not just metadata
recover at least part of custom morphology boundary advantage
avoid serializing custom token labels into the training view
avoid arbitrary open-vocabulary tokens as fixed model IDs
prove decode(encode(text)) == text before any LLM-facing BPB claim
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
scripts/materialize_v2_train_only_marker_views.py
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

Continue with a train-only marker shaping candidate, not more tiny-LM rows:

```text
materialize train/valid/test markerized SentencePiece training views
train a train-only Unigram model from the train view
evaluate with markers stripped at encode time plus finite protected routing
gate on token pressure and visible intrinsic metrics before any BPB run
```

The current finite protected soft-marker candidate showed useful morphology and
protected-span signal, but it is still too token-expensive for handoff or broad
tiny-LM screening.

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

Train-only marker view smoke:

```text
script: scripts/materialize_v2_train_only_marker_views.py
smoke report: artifacts/v2_0_train_only_marker_views_suffix_chain2_smoke.md
policy: suffix_chain, min_suffix_count=2
valid view/raw bytes: 1.086996
valid marker keep rate: 0.559449
interpretation: selective train-only markers materially reduce view inflation
versus the all-soft train view and are worth a train-only Unigram intrinsic
probe
```

Train-only marker frontier:

```text
findings: docs/v2_0_train_only_marker_findings.md
frontier: artifacts/v2_0_train_only_marker_frontier.md
all-soft train-only marker-stripped test tokens/raw byte: 0.196236
all-soft train-only challenge F1: 0.7703
suffix-chain2 test tokens/raw byte: 0.184619
suffix-chain2 challenge F1: 0.7632
high-value suffix test tokens/raw byte: 0.191068
high-value suffix challenge F1: 0.7665
decision: no tiny-LM yet; current train-only marker policies improve pressure
but do not pass the preferred visible intrinsic gate
```

Follow-up controls:

```text
marker vocab audit: artifacts/v2_0_sentencepiece_marker_vocab_audit.md
all marker-trained models learned only one marker-containing vocab piece:
the standalone U+E000 marker
frontier CI: artifacts/v2_0_train_only_marker_frontier_ci.md
train-only marker F1 intervals overlap heavily
decision: the current marker policies form a noisy pressure/F1 frontier;
do not keep changing marker dose as the next lever
```

Tiny-LM marker calibration:

```text
config: configs/v2_0_tiny_lm_marker_calibration.toml
plan: docs/v2_0_tiny_lm_marker_calibration_plan.md
encoder kind: finite_protected_marker_stripped
smoke report: artifacts/v2_0_tiny_lm_marker_calibration_suffix_chain2_dry_run.md
full dry-run report: artifacts/v2_0_tiny_lm_marker_calibration_dry_run.md
dry-run valid/test tokens/raw byte:
  sp64: 0.159020 / 0.159620
  finite_protected_sp64_floor: 0.182112 / 0.183362
  suffix_chain2: 0.184500 / 0.185337
  all_soft: 0.196313 / 0.196954
results: artifacts/v2_0_tiny_lm_marker_calibration_results.md
300-step test BPB:
  sp64: 4.860352
  finite_protected_sp64_floor: 4.976850
  suffix_chain2: 5.094965
  all_soft: 5.157444
decision: train-only marker shaping did not pay back its token-pressure cost
in fixed-step tiny-LM BPB
next: stop marker-dose tuning and switch to a different mechanism
```

Updated next step:

```text
keep finite protected routing
use finite_protected_sp64_floor as the true protected null baseline
prototype selected morph seed vocabulary / curated morph pieces rather than
more marker-density variants
```

Morph seed vocabulary branch:

```text
plan: docs/v2_0_morph_seed_vocab_plan.md
analyzer: scripts/analyze_v2_morph_seed_candidates.py
policy selector: scripts/select_v2_morph_seed_policy.py
default report: artifacts/v2_0_morph_seed_candidate_analysis.md
default private TSV: artifacts/private/v2_0_morph_seed_vocab/morph_seed_candidates.train.tsv
purpose: identify train-only suffix/morph candidates before any UDS/seed policy
policy report: artifacts/v2_0_morph_seed_policy_selection.md
policy findings: docs/v2_0_morph_seed_policy_findings.md
decision: use seed_bias first; do not force broad UDS
augmentation script: scripts/materialize_v2_morph_seed_augmented_view.py
SP config: configs/v2_0_morph_seed_bias_sentencepiece.toml
augmentation report: artifacts/v2_0_morph_seed_augmented_view.md
SP probe report: artifacts/v2_0_morph_seed_bias_sentencepiece_probe.md
findings: docs/v2_0_morph_seed_bias_findings.md
valid/test tokens/raw byte: 0.158312 / 0.158901
decision: token-pressure gate passed; next finite-protected intrinsic eval
intrinsic report: artifacts/v2_0_morph_seed_bias_finite_protected_intrinsic_eval.md
intrinsic findings: docs/v2_0_morph_seed_bias_intrinsic_findings.md
challenge F1 with finite protection: 0.6913
decision: weak appendix did not move morphology F1
strong config: configs/v2_0_morph_seed_bias_strong_sentencepiece.toml
strong augmentation report: artifacts/v2_0_morph_seed_bias_strong_augmented_view.md
strong SP probe report: artifacts/v2_0_morph_seed_bias_strong_sentencepiece_probe.md
strong intrinsic report: artifacts/v2_0_morph_seed_bias_strong_finite_protected_intrinsic_eval.md
strong valid/test tokens/raw byte: 0.158315 / 0.158913
strong challenge F1 with finite protection: 0.6918
decision: stop simple morph-seed appendix branch; compression-safe but not
morphology-effective
next: keep finite protected routing and move to a more structural mechanism
```

Safe UDS branch:

```text
plan: docs/v2_0_safe_uds_plan.md
symbol materializer: scripts/materialize_v2_safe_uds_symbols.py
symbols report: artifacts/v2_0_safe_uds_symbols.md
symbols output: artifacts/private/v2_0_morph_seed_vocab/safe_uds_symbols.train.txt
SP config: configs/v2_0_safe_uds_sentencepiece.toml
selected symbols: 7
purpose: test only the audited safe_uds_candidate_later pool as
SentencePiece user_defined_symbols
SP pressure report: artifacts/v2_0_safe_uds_sentencepiece_probe.md
intrinsic report: artifacts/v2_0_safe_uds_finite_protected_intrinsic_eval.md
findings: docs/v2_0_safe_uds_findings.md
valid/test tokens/raw byte: 0.159109 / 0.159684
challenge F1, bare: 0.7556
challenge F1, finite protected: 0.7081
protected stress, finite protected: 25/25
decision: safe UDS is the current best cheap structural morphology prior, but
not enough for tiny-LM or LLM handoff
next: cautiously expand audited UDS or move to constrained/MorphBPE objective
```

Expanded UDS22 branch:

```text
plan: docs/v2_0_expanded_uds22_plan.md
symbol materializer: scripts/materialize_v2_expanded_uds_symbols.py
symbols report: artifacts/v2_0_expanded_uds22_symbols.md
symbols output: artifacts/private/v2_0_morph_seed_vocab/expanded_uds22_symbols.train.txt
SP config: configs/v2_0_expanded_uds22_sentencepiece.toml
selected symbols: 22
selection: recommendation=uds_or_seed_candidate, min_count>=100,
surface_len>=3, hard_share<=0.01, collision<=0.001
SP pressure report: artifacts/v2_0_expanded_uds22_sentencepiece_probe.md
findings: docs/v2_0_expanded_uds22_findings.md
valid/test tokens/raw byte: 0.183675 / 0.184059
decision: failed token-pressure gate; no finite-protected intrinsic eval
decision: stop UDS expansion; keep safe UDS7 as the best cheap structural prior
next: move to constrained/MorphBPE-style objective or another learned mechanism
that treats morphology as a soft preference instead of hard UDS forcing
```

Fable5 advisor triage:

```text
triage: docs/advisor_response_fable5_triage.md
main critique: constrained/MorphBPE is plausible but premature
first issue: finite protected wrapper costs ~14-15% tokens/raw byte and must be
decomposed before new morphology trainer work
second issue: 300-step BPB may be too early to detect morphology generalization
third issue: separate vocabulary coverage (H1) from decode preference (H2)
updated next:
  1. wrapper cost audit
  2. vocab coverage analysis for teacher morph surfaces in SP64/safe UDS7
  3. decode-time boundary-biased Unigram/Viterbi lambda sweep
  4. build constrained/MorphBPE only if these diagnostics justify it
```

Finite protected wrapper cost audit:

```text
report: artifacts/v2_0_finite_protected_wrapper_cost_audit.md
findings: docs/v2_0_finite_protected_wrapper_cost_findings.md

SP64 test tokens/raw byte: 0.159620
finite protected test tokens/raw byte: 0.183362
relative delta: 14.87%
protected bytes share: 2.67%

largest protected-vs-SP route deltas:
  numeric_like: +137807 tokens
  file_like: +120580 tokens
  non_turkish_latin_word: +94661 tokens
  apostrophe_surface: +51203 tokens

private top-delta examples show Turkish rows with legacy encoding artifacts
such as ý/þ/ð/Ý, so part of the non_turkish_latin_word cost is likely a
data-quality/over-trigger issue.

decision: the next step is protected-route optimization before morphology
trainer work.
```

Non-Turkish Latin route quality audit:

```text
report: artifacts/v2_0_non_turkish_latin_route_quality_audit.md
findings: docs/v2_0_non_turkish_latin_route_quality_findings.md

route occurrences: 18984
turkish_loan_diacritic: 17333 / 91.30%
other_non_turkish_latin: 960 / 5.06%
legacy_turkish_encoding_artifact: 691 / 3.64%

decision: reroute Turkish loan-diacritic words back to normal learned text
flow before constrained/MorphBPE or Viterbi work.
```

Turkish loan-diacritic pass-through:

```text
findings: docs/v2_0_turkish_loan_diacritic_pass_findings.md
route-quality after report:
  artifacts/v2_0_non_turkish_latin_route_quality_audit_after_loan_pass.md
wrapper-cost after report:
  artifacts/v2_0_finite_protected_wrapper_cost_audit_after_loan_pass.md
intrinsic after report:
  artifacts/v2_0_finite_protected_sp64_intrinsic_eval_after_loan_pass.md

non_turkish_latin_word occurrences: 18984 -> 1644
test finite protected tokens/raw byte: 0.183362 -> 0.180564
relative delta over SP64: 14.87% -> 13.12%
protected stress: 25/25
challenge F1: 0.6913

decision: keep the pass-through; next optimize numeric_like, file_like, and
apostrophe_surface route costs.
```

Protected route cost reduction:

```text
findings: docs/v2_0_protected_route_cost_reduction_findings.md
class audit:
  artifacts/v2_0_protected_route_cost_class_audit_after_file_glue_pass.md
wrapper-cost after report:
  artifacts/v2_0_finite_protected_wrapper_cost_audit_after_file_glue_pass.md
intrinsic after report:
  artifacts/v2_0_finite_protected_sp64_intrinsic_eval_after_file_glue_pass.md

apostrophe buffered suffix pass:
  examples: Üniversitesi'nde style Turkish buffered suffixes
  apostrophe_surface delta: +54055 -> +20662

file-like glued sentence pass:
  examples: değerlendirildi.Bulgular, amaçlanmıştır.Gereç
  file_like delta: +120800 -> +72043

test finite protected tokens/raw byte:
  0.183362 before route fixes
  0.180564 after loan-diacritic pass
  0.179465 after apostrophe pass
  0.177726 after file-glue pass

relative delta over SP64:
  14.87% -> 11.34%

protected stress remains: 25/25
challenge F1 remains: 0.6913

decision: route-cost optimization is paying off without harming protected
stress. Continue with numeric_like protected encoder/route policy before
constrained/MorphBPE.
```

Numeric protected encoder what-if:

```text
findings: docs/v2_0_numeric_protected_encoder_whatif_findings.md
audit report: artifacts/v2_0_numeric_protected_encoder_whatif.md
dry-run report: artifacts/v2_0_tiny_lm_marker_calibration_numeric_sp_dry_run.md
300-step report: artifacts/v2_0_tiny_lm_marker_calibration_numeric_sp_300steps.md
new experimental kind: finite_protected_marker_stripped_numeric_sp
new candidate: finite_protected_sp64_numeric_sp_floor

test tokens/raw byte:
  finite protected after route fixes: 0.177726
  finite protected + numeric SP passthrough: 0.172734
  digit2 finite numeric codec what-if: 0.175069

300-step tiny-LM:
  numeric-SP protected floor test BPB: 4.911037
  current finite protected floor test BPB: 4.939361
  historical finite protected floor test BPB: 4.976850
  SP64 test BPB: 4.860352

decision: numeric route redesign recovers meaningful token pressure.
Promote finite_protected_sp64_numeric_sp_floor as the active protected floor
for the next v2.0 experiments. Do not treat it as the final production numeric
codec yet; it is the best experimental protected null baseline. Resume
vocabulary coverage and decode-time boundary-bias diagnostics before any
constrained/MorphBPE trainer work.
```

Morph vocabulary coverage:

```text
findings: docs/v2_0_morph_vocab_coverage_findings.md
report: artifacts/v2_0_morph_vocab_coverage.md
private rows: artifacts/private/v2_0_morph_vocab_coverage.rows.jsonl

scope:
  action == seed_bias
  100 selected morph/suffix surfaces
  881151 weighted occurrences

exact-piece occurrence share:
  SP64: 0.963019
  safe UDS7: 0.962751

standalone-single occurrence share:
  SP64: 0.534474
  safe UDS7: 0.455065

interpretation:
  high-value morph surfaces mostly already exist in the SP64 vocabulary.
  safe UDS7 does not solve the broad morph-transfer problem.
  the next bottleneck is decode preference, not surface availability.

decision:
  do not expand UDS or seed appendix as the next move.
  implement a decode-time boundary-biased Unigram/Viterbi lambda sweep before
  building a constrained/MorphBPE trainer.
```
