from __future__ import annotations

import json
from pathlib import Path

from scripts.prepare_downstream_probe import (
    format_report,
    load_probe_config,
    prepare_probe_outputs,
)


def _posix(path: Path) -> str:
    return path.as_posix()


def test_prepare_downstream_probe_writes_private_token_jsonl_and_report(
    tmp_path: Path,
) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(
        "\n".join(
            [
                "Türkiye'den gelen kitapları ayırdık.",
                "README.md dosyasını açtım.",
                "Gelicem dedim ama gelmedim.",
                "Kadın yakın sokakta bekledi.",
                "OpenAI'den API token aldık.",
                "2026'da yeni rapor yazıldı.",
                "Kedilerden birini gördüm.",
                "Don't split this English line.",
                "config_v2.json dosyası güncellendi.",
                "Arabalarımızdakilerden haber aldık.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "probe"
    report_out = tmp_path / "report.md"
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'corpus_path = "{_posix(corpus)}"',
                f'output_dir = "{_posix(output_dir)}"',
                f'report_out = "{_posix(report_out)}"',
                "max_lines = 10",
                "seed = 7",
                "train_parts = 8",
                "valid_parts = 1",
                "test_parts = 1",
                "write_tokenized = true",
                "allow_download = false",
                "",
                "[[tokenizers]]",
                'name = "custom_tr_morph"',
                'kind = "custom"',
                "",
                "[[tokenizers]]",
                'name = "unicode_char"',
                'kind = "unicode_char"',
            ]
        ),
        encoding="utf-8",
    )

    config = load_probe_config(config_path)
    splits, stats = prepare_probe_outputs(config)
    report = format_report(config, splits, stats, wrote_tokenized=True)
    report_out.write_text(report, encoding="utf-8")

    assert [split.name for split in splits] == ["train", "valid", "test"]
    assert sum(split.line_count for split in splits) == 10
    assert len(stats) == 6
    assert all(row.status == "ok" for row in stats)
    assert (output_dir / "custom_tr_morph" / "train.jsonl").exists()
    assert (output_dir / "unicode_char" / "test.jsonl").exists()

    first_private_line = json.loads(
        (output_dir / "custom_tr_morph" / "train.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    assert sorted(first_private_line) == ["byte_len", "line_index", "tokens"]
    assert isinstance(first_private_line["tokens"], list)

    public_report = report_out.read_text(encoding="utf-8")
    assert "Tokenizer Prep Summary" in public_report
    assert "Türkiye'den gelen kitapları ayırdık." not in public_report


def test_prepare_downstream_probe_supports_report_only_mode(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("Bir satır.\nİki satır.\n", encoding="utf-8")
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        "\n".join(
            [
                "[settings]",
                f'corpus_path = "{_posix(corpus)}"',
                f'output_dir = "{_posix(tmp_path / "probe")}"',
                f'report_out = "{_posix(tmp_path / "report.md")}"',
                "seed = 1",
                "train_parts = 1",
                "valid_parts = 0",
                "test_parts = 1",
                "write_tokenized = true",
            ]
        ),
        encoding="utf-8",
    )

    config = load_probe_config(config_path)
    splits, stats = prepare_probe_outputs(config, write_tokenized_override=False)

    assert len(splits) == 2
    assert stats
    assert not config.output_dir.exists()
