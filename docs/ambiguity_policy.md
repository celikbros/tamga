# Ambiguity and Negative-Word Policy

This document is the v1.2 planning surface. It exists because many Turkish
forms are ambiguous without context, and a tokenizer can become brittle if every
challenge mismatch becomes a new rule.

## Principle

The tokenizer should prefer not splitting when a short suffix-like ending could
also be part of a lexical word.

Examples:

| Surface | Risk |
| --- | --- |
| kadın | false split as `kad +ın` |
| yakın | false split as `yak +ın` |
| altın | false split as `alt +ın` |
| Yazın | noun/adverb form or `Yaz +ın` |
| Gül | noun/name or verb stem |
| Yüz | number/body-part/verb stem ambiguity |
| Yazarım | lexical/professional reading or `yaz +ar +ım` |

## Current Policy

- Do not add short suffixes to the general greedy splitter.
- Use short suffixes only in guarded flows:
  - known surface-stem lexicon
  - apostrophe suffix flow
  - mixed-case/code flow
  - informal-only flow
- Keep `tr_gold_expanded.tsv` frozen at exact match.
- Treat `tr_challenge.tsv` as dev/error analysis, not as a blind target to force
  to 100%.

## Decision Needed

Before v1.2/v1.3 rule work, decide which strategy is preferred.

## Option A: Conservative Context-Free Tokenizer

Ambiguous forms remain unsplit unless a known surface stem explains the full
suffix chain.

Pros:

- Lower false-positive risk.
- Stable behavior for unknown common words.
- Good fit for deterministic tokenizer core.

Cons:

- Lower challenge exact match on ambiguous examples.
- Some real morpheme boundaries remain hidden.

## Option B: Aggressive Morphological Splitter

Split more possible suffix chains even when the stem is not known.

Pros:

- Higher recall on morpheme boundaries.
- Better for examples where all words are assumed to be analyzable.

Cons:

- High false-positive risk.
- Breaks words like `kadın`, `yakın`, `altın`.
- Requires many negative exceptions.

## Option C: Hybrid MorphBPE Direction

Keep deterministic morphology conservative, then let a MorphBPE fallback handle
unknown or ambiguous spans while respecting protected boundaries.

Pros:

- Preserves safe deterministic boundaries.
- Avoids hand-writing every productive Turkish pattern.
- Better path toward production research.

Cons:

- Requires corpus training infrastructure.
- Evaluation must compare deterministic-only and hybrid modes separately.

## Recommended v1.2 Direction

Adopt Option C as the long-term direction, while keeping Option A as the current
deterministic core policy.

Concrete next tasks:

- Expand the negative-word regression list.
- Add an ambiguity fixture file separate from gold regression.
- Mark challenge examples with one of:
  - `safe_rule_candidate`
  - `needs_lexicon`
  - `needs_context`
  - `hybrid_candidate`
- Do not change tokenizer behavior until those labels exist.
