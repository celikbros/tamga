import json
from pathlib import Path

from scripts.materialize_v2_1_real_mix_text_sample import (
    parse_source,
    text_from_record,
    main,
)


def test_parse_source_accepts_path_limit_and_label() -> None:
    source = parse_source("data.jsonl:10:news")

    assert source.path == Path("data.jsonl")
    assert source.max_lines == 10
    assert source.source_label == "news"


def test_text_from_record_rejects_missing_or_empty_text() -> None:
    assert text_from_record({"text": "  merhaba  "}, "text") == "merhaba"
    assert text_from_record({"body": "merhaba"}, "text") is None
    assert text_from_record({"text": ""}, "text") is None
    assert text_from_record(["not", "dict"], "text") is None


def test_main_writes_raw_text_lines_from_jsonl(tmp_path: Path) -> None:
    source = tmp_path / "source.jsonl"
    out = tmp_path / "sample.txt"
    report = tmp_path / "report.md"
    rows = [
        {"text": "birinci satir", "source": "a"},
        {"text": "ikinci\nsatir", "source": "b"},
        {"other": "skip"},
    ]
    source.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )

    result = main(
        [
            "--source",
            f"{source}:10:test",
            "--out",
            str(out),
            "--report-out",
            str(report),
        ]
    )

    assert result == 0
    assert out.read_text(encoding="utf-8").splitlines() == [
        "birinci satir",
        "ikinci satir",
    ]
    assert "written text lines | 2" in report.read_text(encoding="utf-8")
