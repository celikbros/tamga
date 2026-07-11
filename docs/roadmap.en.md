# Handover Remediation Roadmap

> [Türkçe](roadmap.md) · English

Date: 2026-07-11
Input: `docs/handover.en.md` (finding numbers B1-B8 come from there)
Principle: every phase ends with its own acceptance gate; a phase that does
not pass its gate is not merged.

---

## The incoming engineer's first hour

```text
1. Read README.md (bilingual overview).
2. Read CLAUDE.md (commit rules: author celikbros + the two co-author
   trailers, NO Claude trailer; the v3.8 freeze guardrails).
3. Read docs/handover.en.md (what is rotten, and why).
4. Read this file (what to do, in which order).
5. Read the FIRST section of docs/current_resume_point.md (the current state
   is always at the TOP of that file; lower sections are historical layers).
6. Verify the environment:
   python -m pytest --basetemp=<writable-temp>   -> expect 319 passed
   (bare pytest may show 93 environment errors due to a Windows temp ACL
   problem; see audit B8)
7. Guardrails (must stay green after EVERY change):
   - python -m pytest green
   - data/eval/tr_gold_expanded.tsv: 50/50 exact
   - data/eval/tr_stress_public.tsv: 34/34 roundtrip
   - protected span break rate 0.0000
   - the v3.8 id contract: SP 0..63999, byte fallback 64000..64255,
     controls 64256..64383, <pad>=64256 — IMMUTABLE
```

Roles: this repo = the tokenizer team. The LLM side (Gardash) and the data
factory (Derlem) are SEPARATE teams; we do not touch their folders, and we
serve their requests as documents/deliverables.

---

## Faz 0 — Urgent repair (blocking; target: immediately)

Goal: make the queued PII re-tokenize job's tooling work + close the most
embarrassing inconsistencies. Algorithmic behavior DOES NOT change.

```text
0.1  GARDASH_ROOT environment variable: the "C:/CELIK-GARDASH" hardcoded
     defaults in the 5 scripts of B3 become env-derived (the old literal
     stays as the fallback -> tests/docs backward compatible, portable via
     a single env var).
0.2  tokenize_corpus.py --config/--tokenizer become required arguments (B4;
     silent v3.5 selection becomes impossible).
0.3  Add the configs/v3_8_pii_clean_retokenize_sp64k.toml template (for the
     PII job; placeholder paths with fill-in instructions). The canonical
     v3_8_final_sidecar_sp64k.toml stays as a HISTORICAL RECORD with an
     explanatory header comment.
0.4  pyproject: [production] extra = sentencepiece (B5).
0.5  Honesty: --lossless CLI flag; the README scopes the "lossless" claim to
     the v3.8 sidecar chain only; the CLI is clearly labeled a deterministic
     PROTOTYPE (B2).
GATE: pytest 319 green + gold 50/50 + stress 34/34 + CLI --lossless
     roundtrip smoke (double space/tab/newline byte-exact).
```

## Faz 1 — PII-clean re-tokenize service (external trigger: the Derlem release)

The plan is ready: `docs/v3_8_pii_clean_retokenize_readiness.md`.

```text
- Trigger: the Derlem frozen release (full sha256 + exact line/byte counts +
  LF confirmation + the manifest explanation of the 224-line delta).
- The job runs in the Gardash environment; this repo provides the chain and
  validators and reviews the aggregate gate evidence.
- RULE (revised 2026-07-11): because the Derlem trigger is indefinitely far,
  Faz 2 was started EARLY with backward-compatible shims + the bit-identity
  gate (decision note in Faz 2). When the PII job arrives it runs from a
  green HEAD, or from the last pre-Faz-2 tag otherwise; the old script entry
  points keep working unchanged.
GATE: SP alignment mismatches 0 · smoke roundtrip 100% · max id < 64,384 ·
  tokens/raw byte near the 0.1843 band.
```

## Faz 2 — Surgical extraction (separate production from the archive; B1)

```text
2.1  src/tr_tokenizer/production/ package: analyze_line + protected_spans +
     the finite-protected encoder + kind resolution move HERE from scripts.
2.2  scripts/tokenize_corpus.py shrinks toward a thin CLI shell (imports only
     from tr_tokenizer.production; the sys.path hack dies).
2.3  U+2581-style sentinel logic gathered in ONE place (shotgun surgery ends).
GATE (non-negotiable): the existing test suite green + tokenize output
     BIT-IDENTICAL on in-repo smoke fixtures + BIT-IDENTICAL against
     checksums.json on a 10k-sample re-tokenize requested from Gardash.
     A move whose bit-identity cannot be proven is reverted.
```

Start decision and repo-side gate result (2026-07-11):

```text
Decision: with the Derlem trigger uncertain, Faz 2 started early; the risk
  was zeroed by (a) turning the old script locations into shims that
  re-export from the production package (historical commands/imports work
  unchanged) and (b) the bit-identity gate against a pre-move baseline.
Moved:
  production/detector.py  <- materialize_v2_soft_morph_artifacts (analyze_line family)
  production/spans.py     <- audit_v2_1 (Span/protected_spans) + tokenize_v3_1
                             (EncodedTokenSpan/span_to_json/token_mask_for_line)
  production/sp.py        <- evaluate_v2_finite (load_sp_processor) + run_tiny
                             (the _processor_* helpers)
  production/config.py    <- run_tiny (TokenizerConfig/ProbeConfig/load_probe_config)
                             + tokenize_v3_1 (find_tokenizer) + evaluate_v2_protected_encoder
                             (ProtectedPiece/load_selected_pieces)
  tokenize_corpus.py now imports only tr_tokenizer.production + stdlib.
Gate evidence (demo SP1k model; 2 inputs: a 15-line hostile set [literal
  U+2581 included] + the demo corpus; workers=1 and workers=2):
  tokens.bin / loss_mask.bin / index.jsonl / sidecar.jsonl: BIT-IDENTICAL
  in all 3 comparisons
  manifest.json difference: only the embedded output directory paths (expected)
  test suite: 319/319 green
Remaining: the 10k-sample bit-identity confirmation from Gardash (arrives
  naturally with the Faz 1 PII job); for 2.3, the independent U+2581 copy in
  boundary_weighted_bpe.py is handled in the Faz 3 quarantine.
```

## Faz 3 — Quarantine and package cleanup (B6/B7)

```text
3.1  Closed experiment scripts move from scripts/ to research/
     (CANNOT precede Faz 2; production used to import from them).
3.2  boundary_weighted_bpe.py, baseline_bpe.py, external_baselines.py leave
     the package (research/ or a separate archive). Their tests move along.
3.3  Package version decision: removing modules from the API = at least a
     minor bump (3.9.0); the v3.8 TOKENIZER contract is unaffected (that is
     the model/id contract, not the pip package).
3.4  Simplify docs/current_resume_point.md: historical layers move under
     docs/history/; the file keeps only the current state + pointers.
GATE: pytest green + guardrails + every command in the README works on a
     fresh clone.
```

## Faz 4 — The next version line ("v4"; external trigger)

```text
Trigger: a new corpus scope (multilingual / code-heavy; e.g. the Gardash v2
data: FineWeb-2/CulturaX TR 30-100B + The Stack + a synthetic textbook corpus).
Gates that must be re-run (docs/tamga_v3_8_release_and_maintenance_roadmap.md):
  vocabulary-size selection (Gardash lesson: a 64k vocab can be ~37% of the
  parameters of a small model -> 32k/48k are candidates again) · fertility +
  fallback canaries · fixed-byte LM comparison · roundtrip + sidecar gates ·
  LLM integration smoke.
Design inputs: docs/multilingual_strategy.md (layering-before-vocabulary,
  irreversibility flags) · the sentinel-collision lesson (the U+2581 case:
  assume a web corpus contains EVERY sentinel; an escape rule + an early
  full-scan reconstruct audit) · the SentencePiece training memory ceiling
  (the 1M-sample lesson).
v3.8 is NOT touched; a new line is a new version.
```

---

## Status tracking

| Faz | Status | Commit trace | Note |
|---|---|---|---|
| 0 | ✅ done (2026-07-11) | `3df0523` (0.1-0.3), `3cb5080` (0.4-0.5) | gate: 319/319 tests + lossless smoke 6/6 + env-override/required-arg checks |
| 1 | ⏳ waiting on the Derlem release | — | readiness: `docs/v3_8_pii_clean_retokenize_readiness.md` + template config; tooling repaired in Faz 0 |
| 2 | 🔄 repo-side gates PASSED (2026-07-11) | `5625c02` | production package + shims; 4 artifacts × 3 comparisons bit-identical; the external 10k confirmation arrives with Faz 1 |
| 3 | ⏸ after Faz 2 closeout | — | strict ordering; script moves are now low-risk thanks to the shims |
| 4 | ⏸ external trigger | — | new corpus scope (multilingual / code-heavy) |

Document chain (reading order at handover): the audit Section 4 closure
table → this table → the top section of `docs/current_resume_point.md`.
When a phase closes, all three are updated together; the commit messages
carry the evidence itself.

Update this table on every phase transition; the detailed current state is
always written at the top of `docs/current_resume_point.md`.
