from __future__ import annotations

import json

from scripts.run_v3_8_final_release_gates import (
    ReleaseGatePlan,
    build_gate_commands,
    run_plan,
)


def make_plan(tmp_path, *, tokenizer_config=None) -> ReleaseGatePlan:
    if tokenizer_config is None:
        tokenizer_config = tmp_path / "tokenizer_config.json"
    return ReleaseGatePlan(
        base_dir=tmp_path,
        snapshot_dir=tmp_path / "snapshot",
        corpus_text=tmp_path / "final_corpus_text.txt",
        tokenizer_config=tokenizer_config,
        sidecar_config=tmp_path / "v3_8_final_sidecar_sp64k.toml",
        tokenizer_name="sp64k_final_test",
        tokenized_out_dir=tmp_path / "tokenized",
        report_dir=tmp_path / "reports",
        max_lines=100,
        smoke_max_lines=10,
        tokenization_max_lines=0,
        workers=2,
        chunk_lines=7,
        progress=50,
        batch_size=4,
        seq_len=128,
        execute=False,
        continue_on_fail=False,
    )


def test_release_gate_plan_uses_sidecar_handoff_smoke(tmp_path) -> None:
    config = tmp_path / "tokenizer_config.json"
    config.write_text(
        json.dumps(
            {
                "model": {
                    "sp_model_path": str(tmp_path / "sp_unigram_64000_final.model")
                }
            }
        ),
        encoding="utf-8",
    )
    plan = make_plan(tmp_path, tokenizer_config=config)

    commands = build_gate_commands(plan)
    names = [command.name for command in commands]

    assert names == [
        "config_validation",
        "route_density",
        "fertility",
        "handoff_smoke",
        "tokenize_corpus",
        "tokenized_package",
    ]
    handoff = next(command for command in commands if command.name == "handoff_smoke")
    assert "audit_v2_2_llm_handoff_smoke.py" in " ".join(handoff.argv)
    assert "report_v1_8_canary_diagnostics.py" not in " ".join(
        item for command in commands for item in command.argv
    )
    route_density = next(command for command in commands if command.name == "route_density")
    assert str(tmp_path / "sp_unigram_64000_final.model") in route_density.argv


def test_release_gate_dry_run_writes_summary_without_executing(tmp_path) -> None:
    plan = make_plan(tmp_path)

    results, summary_path = run_plan(plan)

    assert summary_path.exists()
    assert all(result.status == "planned" for result in results)
    report = summary_path.read_text(encoding="utf-8")
    assert "v3.8 Final Tokenizer Release Gate Runner" in report
    assert "handoff_smoke" in report
    assert "tokenize_corpus" in report
