from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from scripts.run_sentencepiece_sweep import (
    load_sentencepiece_sweep_config,
    run_sentencepiece_sweep,
)


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("sentencepiece") is None,
    reason="sentencepiece optional dependency is not installed",
)


def _posix(path: Path) -> str:
    return path.as_posix()


def test_run_sentencepiece_sweep_trains_and_reports(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(
        "\n".join(
            [
                "Geldim ve kitabimi aldim.",
                "Turkiye'den Istanbul'a gittim.",
                "README.md dosyasini actim.",
                "Gelicem birazdan.",
            ]
        ),
        encoding="utf-8",
    )
    eval_path = tmp_path / "eval.tsv"
    eval_path.write_text(
        "verb_past\tGeldim.\t"
        + json.dumps(["\u2581Gel", "+di", "+m", "."])
        + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.md"
    model_prefix = tmp_path / "sp_bpe_demo"
    config_path = tmp_path / "sweep.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'corpus = "{_posix(corpus)}"',
                'corpus_label = "unit_test_demo"',
                "claim_grade = false",
                "allow_train = true",
                "",
                "[[eval_sets]]",
                'name = "tiny"',
                f'path = "{_posix(eval_path)}"',
                f'markdown_out = "{_posix(report_path)}"',
                "",
                "[[models]]",
                'name = "sp_bpe_demo"',
                'model_type = "bpe"',
                "vocab_size = 64",
                f'model_prefix = "{_posix(model_prefix)}"',
                "enabled = true",
            ]
        ),
        encoding="utf-8",
    )

    written = run_sentencepiece_sweep(load_sentencepiece_sweep_config(config_path))

    assert written == [report_path]
    assert model_prefix.with_suffix(".model").exists()
    assert model_prefix.with_suffix(".vocab").exists()
    report = report_path.read_text(encoding="utf-8")
    assert "# v1.7 SentencePiece Sweep: tiny" in report
    assert "sp_bpe_demo" in report
    assert "demo-only" in report
