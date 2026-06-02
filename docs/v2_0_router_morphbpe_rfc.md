# v2.0 Router + MorphBPE RFC

Date: 2026-06-02

Status: draft RFC, updated after v1.8 tiny-LM screening

## Purpose

This RFC sketches the v2.0 tokenizer architecture direction.

v1.x established a Turkish deterministic morphology core, protected-span guards,
evaluation scripts, baseline comparisons, do-no-harm smoke tests, and v1.8
tiny-LM screening. v2.0 should decide how to combine that core with routing and
learned vocabulary/fallback without turning the project into hand-written
morphology for every Turkic language.

## Design Goal

```text
Turkish-first, multilingual-aware, lossless tokenizer architecture.
```

The tokenizer should:

- preserve Turkish morphology where the deterministic core is reliable
- preserve code/file/URL/number/date spans before language-specific morphology
- avoid applying Turkish morphology to non-Turkish spans by default
- provide learned fallback for uncertain or non-Turkish spans
- keep byte fallback as the final lossless safety layer

## Non-Goals

v2.0 should not start by:

- writing full Azerbaijani/Kazakh/Kyrgyz/Uzbek/Tatar morphology by hand
- treating all Turkic languages as Turkish with small edits
- globally lowercasing or casefolding text
- applying global NFKC normalization
- freezing vocabulary allocation before routing/script policy is tested
- claiming production readiness before downstream probes

## Motivating Evidence

v1.8 now provides the strongest planning evidence:

```text
pure custom has strong byte-exposure/data-efficiency signal
pure custom has serious token/context/compute pressure
```

Tiny-LM smoke:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| sp_bpe_64000 step 500 | 1668920 | 3.729064 | 3.745292 |
| custom step 1258 | 1670292 | 2.943302 | 2.961183 |

Fixed-token smoke still favors SP:

| Tokenizer checkpoint | Approx bytes seen | Valid BPB | Test BPB |
| --- | ---: | ---: | ---: |
| custom step 500 | 663868 | 4.295575 | 4.312877 |
| sp_bpe_64000 step 500 | 1668920 | 3.729064 | 3.745292 |

Decision:

```text
do not hand pure custom to the LLM team as default
do not discard morphology-aware tokenization
design a learned hybrid/vocabulary layer to reduce tokens/byte
```

Earlier v1.6b ended with:

```text
tr_gold_expanded.tsv: 50/50
tr_challenge.tsv: 44/108, f1=0.8255
en_smoke.tsv: 8/10, f1=0.8889
multilingual_smoke.tsv: 17/20, f1=0.9404
protected span break_rate: 0.0000
```

R3 Azerbaijani routing was deferred because the visible failures require
span-level routing:

```text
Mənim adım Əli, Bakıda yaşayıram.
Xəbər: qız məktəbə gedir, dağ yolu uzundur.
```

The failing tokens (`adım`, `Bakıda`, `gedir`, `uzundur`) do not carry strong
Azerbaijani-only character cues. Token-level guards cannot solve this reliably.

## Proposed Layer Sketch

```text
0. Raw input + offset map
1. Minimal reversible cleanup
2. Cross-language protection layer
3. Script/span router
4. Turkish deterministic morphology layer
5. Learned MorphBPE/Unigram fallback
6. Byte fallback
```

This is a sketch. Exact mechanics remain subject to v1.7 heldout, baseline, and
downstream probe evidence.

## Layer 0: Raw Input + Offset Map

The tokenizer must keep enough mapping information to preserve:

- original string reconstruction
- offsets for downstream annotation tasks
- protected span boundaries
- diagnostics for normalization decisions

Invariant:

```text
decode(encode(x)) == x
```

If a normalized internal view is used, it must not replace the raw text for
decode.

## Layer 1: Minimal Reversible Cleanup

Allowed:

- normalize line endings if offsets are tracked
- remove or isolate BOM/clearly accidental controls if reversible or recorded
- NFC only on non-protected spans if explicitly enabled

Not allowed by default:

- global NFKC
- global lowercase
- global casefold
- diacritic stripping
- homoglyph normalization
- apostrophe unification across languages

Reason:

Turkish/Turkic dotted-dotless `i`, Azerbaijani `ə`, Kazakh/Kyrgyz Cyrillic
letters, and Uzbek apostrophe-like letters are linguistically meaningful.

## Layer 2: Cross-Language Protection Layer

This layer runs before morphology.

Protected span candidates:

```text
URL
email
file path
file-like token
package/version comparator
number
date
time
hash/identifier
inline code-like span
```

Examples:

```text
README.md'yi
config_v2.json
transformers>=4.40
https://example.com/2024-05-19
2026'da
34-ABC-1907
```

Policy:

- protect the base span first
- allow Turkish suffix tails only through explicit guarded flows
- never let morphology enter URL/code/file internals

## Layer 3: Script/Span Router

The router decides which processing layer may touch a span.

Possible route labels:

```text
tr_high_confidence
turkic_latin_uncertain
turkic_cyrillic
non_turkish_latin
arabic_script
greek_script
code_or_protected
unknown
```

Important rule:

```text
unknown must not default to Turkish morphology.
```

For v2.0, the router should be conservative. Wrong pass-through is usually less
harmful than wrong Turkish morphology.

## Layer 4: Turkish Deterministic Morphology

The current deterministic core remains valuable as a high-precision Turkish
layer.

It should run only when:

- the span is not protected
- the router permits Turkish morphology
- existing guardrails are satisfied

It should preserve:

- surface-stem policy
- apostrophe suffix policy
- short-suffix false-positive protection
- informal surface preservation
- deterministic encode/decode

It should not become:

- a full morphological analyzer
- a context disambiguator
- a pan-Turkic morphology engine

## Layer 5: Learned MorphBPE/Unigram Fallback

This is the likely main v2.0 research layer.

Purpose:

```text
Use learned subword segmentation while respecting hard boundaries and optionally
using soft morphology hints.
```

Inputs:

- raw or minimally normalized span
- hard protected boundaries
- optional Turkish morphology hard boundaries
- optional soft candidate boundaries

Candidate approaches:

```text
pre-segmented corpus + SentencePiece/Unigram
morph-boundary-constrained BPE
Morfessor-informed segmentation + subword fallback
hybrid deterministic Turkish core + learned fallback
```

Open decision:

```text
BPE vs Unigram vs MorphBPE-like constrained merges.
```

v1.7 missing baseline and downstream probe results should influence this choice.

## Layer 6: Byte Fallback

Byte fallback is the final safety net.

It should guarantee:

- no unknown token
- lossless representation
- rare Unicode coverage

It should not be used as a quality substitute. If frequent Turkish/Turkic
characters fall to bytes often, the vocabulary/router design is wrong.

Required metrics:

```text
byte fallback rate by language/script
byte fallback rate by domain
protected span break rate
roundtrip exactness
```

## Apostrophe Policy

Do not use one global apostrophe rule.

Different roles:

```text
Turkish: proper name / number / abbreviation + suffix separator
English/French/Italian: contraction or lexical apostrophe
Uzbek: letter/tutuq-like sign
code: string delimiter or literal character
URL/file: protected literal
```

Default:

```text
leave apostrophe-containing non-Turkish spans intact unless a Turkish suffix
flow is explicitly and safely triggered.
```

## Casing Policy

Default:

```text
preserve case
```

Do not globally apply:

```text
lower()
casefold()
English-centric casing
```

Turkish/Azerbaijani dotted-dotless `i` behavior must be tested separately if
case-aware lookup is introduced.

## Vocabulary Allocation

Do not freeze vocabulary allocation before:

- routing policy is defined
- script coverage is measured
- byte fallback rates are measured
- downstream probe has at least a first result

Future reports should include:

```text
TR token fertility
AZ token fertility
Turkic Cyrillic fertility
protected span break rate
byte fallback rate
vocab share by script/language cluster
```

## Evaluation Requirements

Before implementing v2.0 seriously, the project should have:

```text
v1.7 heldout eval plan
v1.7 missing baseline protocol
v1.7 downstream probe protocol
visible smoke/stress tests
protected span metrics
byte fallback metrics
```

v2.0 quality should be judged using:

- boundary F1
- token fertility
- protected span break rate
- byte fallback rate
- heldout policy and independent gold metrics
- byte-normalized LM loss / bits-per-byte

## Open Questions

1. Should the learned fallback be BPE, Unigram, or a constrained MorphBPE?
2. What corpus mix is required for Turkish-first but multilingual-aware training?
3. What is the minimum acceptable byte fallback rate by script/language?
4. Should Turkish deterministic boundaries be hard constraints or soft hints?
5. How should code-mixed English/Turkish words like `OpenAI`, `data`, `code` be
   routed?
6. What vocabulary size is realistic for the target LLM project?
7. Which scripts are first-class in v2.0: Latin only, Latin+Cyrillic, or more?

## Recommended Next Work

After this RFC skeleton:

```text
1. Create baseline config/protocol implementation tasks.
2. Prepare downstream probe handoff for the LLM team.
3. Design a small v2.0 router smoke set from public synthetic examples.
4. Only then prototype learned fallback.
```

## Final Principle

Do not let a small smoke-set improvement force an early architecture.

The v1.6b Azerbaijani decision is the example:

```text
17/20 -> 20/20 multilingual smoke would require span-level routing.
Span-level routing is v2.0 architecture, not a v1.6b guard.
```

Keep the Turkish deterministic core high-precision, and let learned fallback
handle uncertainty.
