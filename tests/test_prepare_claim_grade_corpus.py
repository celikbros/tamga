from __future__ import annotations

import json
from pathlib import Path

from scripts.prepare_claim_grade_corpus import (
    load_claim_grade_corpus_config,
    normalize_for_leakage,
    prepare_corpus,
)


def _posix(path: Path) -> str:
    return path.as_posix()


def test_normalize_for_leakage_preserves_case_by_default() -> None:
    assert (
        normalize_for_leakage(
            "Iğdır'ın ışığı!",
            lowercase=False,
            strip_punctuation=True,
        )
        == "Iğdırın ışığı"
    )


def test_prepare_corpus_filters_exact_and_normalized_leaks(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.tsv"
    eval_path.write_text(
        "default\tGeldim.\t[]\n",
        encoding="utf-8",
    )
    text_source = tmp_path / "source.txt"
    text_source.write_text(
        "Geldim.\nBaşka temiz satır.\n",
        encoding="utf-8",
    )
    jsonl_source = tmp_path / "source.jsonl"
    jsonl_source.write_text(
        json.dumps({"text": "Geldim!"}, ensure_ascii=False)
        + "\n"
        + json.dumps({"text": "Ek temiz satır."}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "out.txt"
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'output_path = "{_posix(output_path)}"',
                f'manifest_out = "{_posix(tmp_path / "manifest.md")}"',
                f'leakage_out = "{_posix(tmp_path / "leakage.md")}"',
                "max_output_lines = 10",
                "ngram_size = 2",
                "normalize_lowercase = false",
                "strip_punctuation = true",
                "",
                "[[eval_sets]]",
                'name = "tiny"',
                f'path = "{_posix(eval_path)}"',
                "",
                "[[sources]]",
                'name = "text_source"',
                'format = "text"',
                f'path = "{_posix(text_source)}"',
                "",
                "[[sources]]",
                'name = "jsonl_source"',
                'format = "jsonl"',
                f'path = "{_posix(jsonl_source)}"',
                'text_field = "text"',
            ]
        ),
        encoding="utf-8",
    )

    config = load_claim_grade_corpus_config(config_path)
    stats, examples = prepare_corpus(config)

    assert stats[0].exact_leaks == 1
    assert stats[1].normalized_leaks == 1
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "Başka temiz satır.",
        "Ek temiz satır.",
    ]
    assert examples
