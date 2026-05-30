from __future__ import annotations

import json
from pathlib import Path

from scripts.report_baseline_matrix import (
    build_specs_from_config,
    load_baseline_config,
    run_matrix,
)


def _posix(path: Path) -> str:
    return path.as_posix()


def test_load_baseline_config_and_build_specs(tmp_path: Path) -> None:
    config_path = tmp_path / "baselines.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                "allow_download = false",
                "",
                "[[datasets]]",
                'name = "tiny"',
                f'path = "{_posix(tmp_path / "tiny.tsv")}"',
                "",
                "[[baselines]]",
                'name = "custom_tr_morph"',
                'kind = "custom"',
                "enabled = true",
                "",
                "[[baselines]]",
                'name = "qwen"',
                'kind = "hf"',
                'model = "Qwen/Qwen2.5-0.5B"',
                "enabled = false",
            ]
        ),
        encoding="utf-8",
    )

    config = load_baseline_config(config_path)
    specs = build_specs_from_config(config)

    assert config.allow_download is False
    assert config.datasets[0].name == "tiny"
    assert [spec.name for spec in specs] == ["custom_tr_morph"]


def test_run_matrix_writes_visible_report(tmp_path: Path) -> None:
    eval_path = tmp_path / "eval.tsv"
    eval_path.write_text(
        "verb_past\tGeldim.\t"
        + json.dumps(["\u2581Gel", "+di", "+m", "."])
        + "\n",
        encoding="utf-8",
    )
    report_path = tmp_path / "report.md"
    config_path = tmp_path / "baselines.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                "allow_download = false",
                "",
                "[[datasets]]",
                'name = "tiny"',
                f'path = "{_posix(eval_path)}"',
                f'markdown_out = "{_posix(report_path)}"',
                "",
                "[[baselines]]",
                'name = "custom_tr_morph"',
                'kind = "custom"',
                "enabled = true",
                "",
                "[[baselines]]",
                'name = "unicode_char"',
                'kind = "unicode_char"',
                "enabled = true",
            ]
        ),
        encoding="utf-8",
    )

    written = run_matrix(load_baseline_config(config_path))

    assert written == [report_path]
    report = report_path.read_text(encoding="utf-8")
    assert "# v1.7 Baseline Matrix: tiny" in report
    assert "custom_tr_morph" in report
    assert "unicode_char" in report
