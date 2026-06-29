# v2.2 to v3.0 Roadmap

Date: 2026-06-13

## Current Position

v2.1 is closed as the protected-sidecar baseline:

```text
sp64_protected_passthrough_sidecar
```

v2.1 answered the tokenizer-contract question:

```text
Use byte-offset sidecar metadata and avoid global pre-split by default.
```

v3.0 will be the first LLM-team handoff version, but only after the required
v2.x hardening phases are complete. Do not promote to v3.0 early.

## Version Meaning

### v2.1: Closed Baseline

Status:

```text
closed
```

Scope:

```text
protected passthrough sidecar
exact roundtrip
detector battery
real-mix masking/pressure audits
20M tiny-LM BPB row
```

Primary docs:

```text
docs/v2_1_final_handoff_package.md
docs/v2_1_closure_gauntlet_findings.md
docs/v2_1_regression_checklist.md
```

### v2.2: Handoff Hardening

Status:

```text
closed
```

Goal:

```text
turn the v2.1 baseline into an LLM-integration-ready package
```

Required work:

```text
single-command v2.2 smoke audit
sidecar JSONL schema freeze
larger real-mix smoke if needed
LLM dataloader/batch compatibility proof
clear failure thresholds
concise README for LLM consumers
```

Current progress:

```text
script: scripts/audit_v2_2_llm_handoff_smoke.py
tests: tests/test_v2_2_llm_handoff_smoke.py
valid/test 250-line smoke: PASS
real-mix 5k smoke: PASS
full real-mix 60k smoke: PASS
hardening gate doc: docs/v2_2_llm_handoff_hardening_gate.md
schema candidate: docs/v2_2_sidecar_jsonl_schema.md
LLM README draft: docs/v2_2_llm_team_integration_readme.md
```

### v2.3: Sidecar Schema Freeze

Status:

```text
closed
```

Required work:

```text
sidecar_schema_version
field types and required/optional keys
route enum policy
offset semantics: UTF-8 byte offsets and Python-style char offsets
backward compatibility rules
schema examples
```

Evidence:

```text
schema freeze doc: docs/v2_3_sidecar_schema_freeze.md
validator: scripts/audit_v2_3_sidecar_schema_contract.py
full real-mix schema audit: PASS
records: 40388
spans: 149999
failures: 0
```

### v2.4: LLM Consumer Simulation

Status:

```text
closed
```

Required work:

```text
masking/redaction/copy simulation
token-overlap policy
byte-offset reconciliation examples
batch record format expected by dataloaders
failure-mode examples
```

Evidence:

```text
findings: docs/v2_4_llm_consumer_simulation_findings.md
script: scripts/audit_v2_4_llm_consumer_simulation.py
full real-mix consumer simulation: PASS
copy failures: 0
redaction failures: 0
token-mask failures: 0
extra mask bytes/raw byte: 0.003983
```

### v2.5: Wider Robustness

Status:

```text
closed
```

Run only if time or LLM-team risk appetite requires it.

Possible checks:

```text
larger/private pretraining sample smoke
route-selective pre-split what-if for numeric_like
throughput benchmark
sidecar consumer simulation in actual dataloader code
```

Decision:

```text
closed as no-extra-run-required for experimental handoff
closeout doc: docs/v2_5_wider_robustness_closeout.md
```

Do not reopen:

```text
global pre-split as default
marker-dose morphology tuning
broad UDS
seed appendix
teacher-distilled static tokenizer
```

### v3.0: LLM Handoff Candidate

Status:

```text
experimental handoff package prepared
```

Definition:

```text
the first complete experimental tokenizer candidate that can be handed to the
LLM team with a stable contract, regression gate, and integration smoke report
```

v3.0 requires:

```text
all required v2.x phases closed
v2.1 regression checklist PASS
v2.2 handoff smoke PASS
20M BPB reference row present
sidecar schema documented
LLM-team README written
known limitations documented
```

## Current Recommendation

Continue v2.2 with this order:
Continue v2.x with this order:
Current v2.x closeout:

```text
v2.1 closed
v2.2 closed
v2.3 closed
v2.4 closed
v2.5 closed
v3.0 experimental handoff package prepared:
  docs/v3_0_experimental_handoff_package.md
```

## Success Criteria

We can say "v3.0 is complete" when:

```text
LLM team can run one command and get PASS/FAIL
sidecar JSONL schema is stable
encode/decode is exact on the handoff smoke
fallback and masking overhead are below thresholds
the model-token stream can form LM batches
known limitations are explicit
```
