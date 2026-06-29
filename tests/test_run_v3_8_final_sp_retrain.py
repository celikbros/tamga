from __future__ import annotations

import json

from scripts.run_tiny_lm_bpb_probe import load_probe_config
from scripts.run_v3_8_final_sp_retrain import RetrainPlan, run_plan


def make_plan(tmp_path, *, corpus_text=None) -> RetrainPlan:
    if corpus_text is None:
        corpus_text = tmp_path / "final_corpus_text.txt"
    return RetrainPlan(
        corpus_text=corpus_text,
        model_prefix=tmp_path / "models" / "sp_unigram_64000_final",
        tokenizer_name="sp64k_final_test",
        toml_out=tmp_path / "configs" / "v3_8_final_sidecar_sp64k.toml",
        tokenizer_config_out=tmp_path / "configs" / "tokenizer_config.json",
        report_out=tmp_path / "artifacts" / "v3_8_final_sp_retrain_plan.md",
        template_config=None,
        vocab_size=64000,
        model_type="unigram",
        max_sentence_length=16384,
        num_threads=16,
        input_sentence_size=0,
        shuffle_input_sentence=True,
        train_extremely_large_corpus=True,
        effective_vocab_size=64384,
        train=False,
        force=False,
        status="training_final_candidate_pending_gates",
    )


def test_retrain_plan_writes_configs_without_training(tmp_path) -> None:
    corpus = tmp_path / "final_corpus_text.txt"
    corpus.write_text("Turkiye icin final corpus smoke.\n", encoding="utf-8")
    plan = make_plan(tmp_path, corpus_text=corpus)

    failures, warnings = run_plan(plan)

    assert failures == []
    assert warnings == []
    assert plan.report_out.exists()
    assert plan.toml_out.exists()
    assert plan.tokenizer_config_out.exists()
    assert not plan.model_path.exists()

    probe_config = load_probe_config(plan.toml_out)
    assert probe_config.tokenizers[0].name == "sp64k_final_test"
    assert probe_config.tokenizers[0].path == plan.model_path
    assert "url" in probe_config.tokenizers[0].sp_passthrough_routes
    assert "numeric_like" not in probe_config.tokenizers[0].sp_passthrough_routes

    config = json.loads(plan.tokenizer_config_out.read_text(encoding="utf-8"))
    assert config["tokenizer_name"] == "sp64k_final_test"
    assert config["model"]["sp_model_path"].endswith("sp_unigram_64000_final.model")
    assert config["id_space"]["byte_fallback_start"] == 64000
    assert config["id_space"]["control_token_start"] == 64256
    assert config["id_space"]["current_effective_vocab_size"] == 64384
    assert config["special_token_registry"]["assigned"]["<pad>"] == 64256
    assert config["special_token_registry"]["assigned"]["<thinking>"] == 64260
    assert config["sidecar"]["token_boundary_alignment"] is False
    assert "numeric_like" in config["sidecar"]["sp_passthrough_routes"]


def test_retrain_plan_fails_before_writing_configs_when_corpus_missing(tmp_path) -> None:
    plan = make_plan(tmp_path, corpus_text=tmp_path / "missing.txt")

    failures, _warnings = run_plan(plan)

    assert any("corpus text does not exist" in failure for failure in failures)
    assert plan.report_out.exists()
    assert not plan.toml_out.exists()
    assert not plan.tokenizer_config_out.exists()
