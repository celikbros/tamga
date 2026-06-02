from pathlib import Path
import json

from scripts.run_v2_candidate_sentencepiece_probe import (
    ViewStats,
    format_report,
    load_config,
    raw_bytes_from_candidate_jsonl,
)


def test_load_config_reads_candidate_sentencepiece_settings(tmp_path: Path):
    config_path = tmp_path / "candidate_sp.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                'candidate_name = "candidate_a"',
                'train_view = "train.txt"',
                'valid_view = "valid.txt"',
                'test_view = "test.txt"',
                'model_prefix = "models/candidate_a"',
                'model_type = "unigram"',
                "vocab_size = 32000",
                'report_out = "report.md"',
                'normalization_rule_name = "identity"',
                "character_coverage = 1.0",
                "hard_vocab_limit = false",
                "split_by_whitespace = true",
                "remove_extra_whitespaces = false",
                "train_extremely_large_corpus = false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.candidate_name == "candidate_a"
    assert config.vocab_size == 32000
    assert config.model_path == Path("models/candidate_a.model")
    assert config.vocab_path == Path("models/candidate_a.vocab")


def test_raw_bytes_from_candidate_jsonl_uses_matching_jsonl_path(tmp_path: Path):
    view_path = tmp_path / "candidate.valid.txt"
    jsonl_path = tmp_path / "candidate.valid.jsonl"
    view_path.write_text("serialized view\n", encoding="utf-8")
    jsonl_path.write_text(
        json.dumps({"text": "raw one"}, ensure_ascii=True)
        + "\n"
        + json.dumps({"text": "raw two"}, ensure_ascii=True)
        + "\n",
        encoding="utf-8",
    )

    assert raw_bytes_from_candidate_jsonl(view_path) == len("raw oneraw two".encode("utf-8"))


def test_format_report_includes_gate_and_seed_caveat(tmp_path: Path):
    config_path = tmp_path / "candidate_sp.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                'candidate_name = "candidate_a"',
                'train_view = "train.txt"',
                'valid_view = "valid.txt"',
                'test_view = "test.txt"',
                'model_prefix = "models/candidate_a"',
                'model_type = "unigram"',
                "vocab_size = 64000",
                'report_out = "report.md"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    config = load_config(config_path)
    rows = [
        ViewStats(split="valid", lines=2, raw_bytes=100, view_bytes=150, sp_tokens=20),
        ViewStats(split="test", lines=2, raw_bytes=200, view_bytes=300, sp_tokens=40),
    ]

    report = format_report(config, rows)

    assert "v2.0 Candidate SentencePiece Probe" in report
    assert "does not" in report
    assert "force every selected seed" in report
    assert "SP tokens/raw byte" in report
    assert "| valid | 2 | 100 | 150 | 1.500000 | 20 | 0.133333 | 0.200000 |" in report
