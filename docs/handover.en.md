# Handover Forensic Audit

> [Türkçe](handover.md) · English

Date: 2026-07-11
Scope: the tamga repository (state after v3.8.0)
Purpose: let an incoming engineer learn from a single document what this
project really is and where it is rotten. No praise; every finding carries
file/line references.

> For the step-by-step plan: `docs/roadmap.en.md`
> For the current project state: `docs/current_resume_point.md`
>
> This report is the record of the audit MOMENT (morning of 2026-07-11) and
> is kept unchanged as a historical document. For the current closure status
> of each finding see the Section 4 table below and the roadmap status
> table — B1-B5 were closed the same day.

---

## 0. The project's real identity (in 30 seconds)

This repository contains TWO things that look like one project:

1. **The prototype** — `src/tr_tokenizer/` (1,665 lines): a deterministic,
   rule-based Turkish morphology splitter. This is what the `tamga` CLI runs
   (`src/tr_tokenizer/__main__.py:30`). Its own docstring says "prototype"
   (`src/tr_tokenizer/__init__.py:1`). **It is NOT the production tokenizer.**
2. **The product** — the v3.8 production tokenizer
   (`sp64k_final_protected_passthrough_sidecar_controls128`): SentencePiece
   unigram 64k + protected-route passthrough + byte fallback + 128 control
   ids + sidecar. The losslessness (byte-exact roundtrip) guarantee belongs
   to THIS chain and is proven (`docs/v3_8_phase2_acceptance_status.md`).
   The model file is **not in the repo** (private handoff); the encode logic
   lived in the **script layer**, not in `src/`.

The research started from the v1.x deterministic-morphology idea; the v2.0
measurements showed that mechanism could not beat SP64k (closed negative
results: the `docs/v2_0_*_findings.md` series); the v3.x line shipped SP +
protection + sidecar to production. **The data won; the brand stayed on the
old mechanism.**

## 1. Proven main findings

### B1. Inverted dependency: production imports from the experiment archive (CRITICAL)

`scripts/tokenize_corpus.py:19-31` (the production tokenization entry point)
imported from these research scripts:

```text
scripts/audit_v2_1_sidecar_operation_simulation.py  -> protected_spans
scripts/evaluate_v2_finite_protected_sp64_intrinsic.py
scripts/materialize_v2_soft_morph_artifacts.py      -> analyze_line (the protected-span detector!)
scripts/run_tiny_lm_bpb_probe.py                    -> production "kind" resolution (a 1,589-line experiment harness; lines 195/1065/1087)
scripts/tokenize_v3_1_corpus_smoke.py
```

`scripts/` is not even a package (no `__init__.py`); the chain worked only
from the repo root via the `sys.path.insert` hack at
`tokenize_corpus.py:16-17`. Consequence: the U+2581 detector fix had to be
patched into THREE files (`docs/v3_8_detector_reconstruct_crash_fix.md`) —
proof of shotgun surgery.

### B2. The default mode is NOT lossless; the README claimed otherwise (CRITICAL)

Empirical (2026-07-11, `encode()`/`decode()` with default settings):

```text
FAIL 'two  spaces'    -> 'two spaces'     (double space lost)
FAIL 'tab\tthere'     -> 'tab there'
FAIL 'line\nbreak'    -> 'line break'
FAIL ' leading space' -> 'leading space'
FAIL 'question ?!'    -> 'question?!'     (punctuation heuristic loss)
```

Cause: `src/tr_tokenizer/__main__.py` constructs with
`preserve_whitespace=False`; `decode()` guesses spaces
(`tokenizer.py:134-178`, `_NO_SPACE_BEFORE` at line 27). The genuinely
lossless path (`_decode_lossless`, line 181) was opt-in. The guardrail set
(`tr_stress_public` 34/34) never caught this because it consists of
single-space examples. The "lossless" claim is true only for the v3.8
sidecar chain.

### B3. Dead absolute paths inside critical tooling (CRITICAL — blocked active work)

The `C:/CELIK-GARDASH` folder no longer exists (the LLM project moved to
`C:\CELIKBROS PROJECTS\gardash` on 2026-07-05). It was still hardcoded in:

```text
scripts/run_v3_8_final_release_gates.py   (lines 11, 362-379)  <- gates of the PII re-tokenize job
scripts/run_v3_8_final_sp_retrain.py      (lines 188-190, 309-315, 377)
scripts/tokenize_v3_1_corpus_smoke.py     (lines 400, 405)
scripts/materialize_v3_1_ablation_split.py (line 82)
scripts/report_v3_1_gardash_fertility.py  (lines 388, 398)
configs/v3_8_final_sidecar_sp64k.toml     (lines 2-4, 24)      <- the canonical v3.8 config
configs/v3_0_gardash_sidecar.toml, configs/v1_7_baselines.toml (archive)
```

The single queued reactive job (PII-clean re-tokenize,
`docs/v3_8_pii_clean_retokenize_readiness.md`) runs through exactly these
tools.

### B4. Stale defaults: the production script pointed at v3.5 (HIGH)

`scripts/tokenize_corpus.py:520-521` defaulted to
`configs/v3_5_sidecar_sp64k_stratified_480mb.toml` +
`sp64k_stratified_480mb_protected_passthrough_sidecar`. An operator who
forgot a flag silently loaded the WRONG GENERATION of tokenizer config.

### B5. Packaging inconsistency (MEDIUM)

`pyproject.toml:25` had `dependencies = []`, but the production chain needs
`sentencepiece` — which lived only in the optional `[baselines]` extra
(lines 31-35). On a fresh install, `tokenize_corpus.py` raised ImportError.

### B6. Dead/closed code inside the installable package (MEDIUM)

```text
src/tr_tokenizer/boundary_weighted_bpe.py  (208 lines)  closed research branch
  (docs say "demoted/diagnostic-only"); sole user: 1 probe script + its test
src/tr_tokenizer/baseline_bpe.py           (145 lines)  v1.5 toy BPE baseline
src/tr_tokenizer/external_baselines.py     (163 lines)  comparison wrappers
```

None of these belong in the installable package API.

### B7. A research notebook in the shape of code (LOW but a noise source)

109 scripts / 37,432 lines (25 `audit_*`, 22 `materialize_*`, …) versus a
1,665-line core. Most belong to experiments declared CLOSED in the docs.
Valuable as an archive; entangled with production while sitting in
`scripts/` (B1).

### B8. Smaller items

```text
- the "lexicon-aware" flow is in practice a hand list: stems.py ~69,
  informal.py ~19, morphology.py ~55 entries. It works; the naming oversells.
- docs/current_resume_point.md is 1,900 lines with 6+ mutually superseding
  "Latest Actual State" headings — the current truth had to be hunted for
  INSIDE the file.
- 8 undeletable pytest junk dirs (foreign NTFS owner) at the repo root +
  the tests/fixtures/tmp5yzyy371 leftover (needs admin cleanup).
```

## 2. Philosophy assessment

- **The root idea is right and field-proven:** Turkish-first +
  protection-first + lossless + measurement-driven decisions. The v3.8
  package was consumed in real training (the 130M run, ~0.2B tokens) with
  zero loader defects.
- **The methodology also worked:** the project eliminated its own founding
  mechanism (deterministic morphology) by measurement and followed the data.
  Negative results were closed and documented.
- **The contradictions are in execution:** (1) what an install gives you is
  the lossy prototype while the storefront says "lossless" (B2); (2) the
  "production-final/FROZEN" stamp froze the numbers, not the engineering
  that carries them (B1/B3/B4); (3) the brand points at the prototype while
  the product has no address in the repo (B0/B5).

## 3. Verdict: do NOT rewrite from scratch. DO the surgical extraction.

Greenfield rewrite REJECTED, because:

1. The repo's real asset is not code: the frozen v3.8 contract + the
   bit-exact reproducibility evidence chain (checksums, gate reports; the
   consumer TRAINED on these) + the eval sets + 319 tests + the archive of
   closed negative results. A rewrite improves none of these and puts the
   first at risk.
2. The production code worth saving is small (~3-4k lines: `analyze_line`,
   `protected_spans`, the finite-protected encoder, `tokenize_corpus`, the
   gates).
3. The acceptance gate already exists: every move can be proven with
   bit-identity against `checksums.json`. With zero behavior change this
   does not count as "reopening" the frozen algorithmic line.

Execution order and gates: `docs/roadmap.en.md`.

## 4. Finding closure status (last update: 2026-07-11)

| Finding | Status | How / Where |
|---|---|---|
| B1 inverted dependency | ✅ CLOSED (repo-side) | Faz 2, commit `5625c02`: the v3.8 chain moved into `src/tr_tokenizer/production/` (detector/spans/sp/config); old script locations are re-export shims; `tokenize_corpus.py` imports only from the package. Evidence: 319/319 tests + 4 output artifacts bit-identical across 3 comparisons (workers=1/2, literal U+2581 included). Remaining: the 10k-sample confirmation from Gardash (with Faz 1) + the independent U+2581 copy inside `boundary_weighted_bpe.py` (Faz 3). |
| B2 lossy default vs "lossless" claim | ✅ CLOSED | Faz 0.5, commit `3cb5080`: `--lossless` CLI flag (6/6 roundtrip verified); the CLI description + README (TR/EN) scope the claim to the v3.8 production chain. Default behavior deliberately UNCHANGED (guardrail compliance); the honesty was fixed. |
| B3 dead absolute paths | ✅ CLOSED | Faz 0.1, commit `3df0523`: 5 scripts resolve via the `GARDASH_ROOT` environment variable (historical literal as fallback); placeholder template `configs/v3_8_pii_clean_retokenize_sp64k.toml` for the PII job; the original v3.8 config marked as a historical record. |
| B4 stale v3.5 defaults | ✅ CLOSED | Faz 0.2, commit `3df0523`: `--config/--tokenizer` are required in `tokenize_corpus.py`; silent wrong-generation selection is impossible. |
| B5 packaging (sentencepiece) | ✅ CLOSED | Faz 0.4, commit `3cb5080`: `[production]` extra in `pyproject.toml`. |
| B6 dead code in the package | ⏳ OPEN | In Faz 3.2: `boundary_weighted_bpe.py`, `baseline_bpe.py`, `external_baselines.py` leave the package (with the version decision). |
| B7 archive in the shape of code | ⏳ OPEN | In Faz 3.1: closed experiment scripts move under `research/`; safe now thanks to the Faz 2 shims. |
| B8 smaller items | ⏳ PARTIAL | The undeletable temp dirs await the admin command (roadmap "first hour" note); the `current_resume_point.md` simplification is Faz 3.4. |

Reading order at handover time: this table → the roadmap status table →
the top section of `docs/current_resume_point.md`. The three must stay
consistent; when a phase closes, all three are updated together.
