import json
from pathlib import Path

from scripts.audit_v2_3_sidecar_schema_contract import audit_sidecar


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _valid_record() -> dict[str, object]:
    return {
        "schema_version": "v2.2-sidecar-jsonl-1",
        "tokenizer": "sp64_protected_passthrough_sidecar",
        "split": "sample",
        "line_number": 1,
        "raw_bytes": len("README.md hazır".encode("utf-8")),
        "token_count": 3,
        "fallback_source_tokens": 0,
        "spans": [
            {
                "route": "file_like",
                "byte_start": 0,
                "byte_end": 9,
                "char_start": 0,
                "char_end": 9,
                "surface": "README.md",
            }
        ],
    }


def test_schema_contract_accepts_valid_sidecar(tmp_path: Path) -> None:
    raw_path = tmp_path / "sample.txt"
    raw_path.write_text("README.md hazır\n", encoding="utf-8")
    sidecar_path = tmp_path / "sidecar.jsonl"
    _write_jsonl(sidecar_path, [_valid_record()])

    stats = audit_sidecar(
        sidecar_path=sidecar_path,
        raw_lines=["README.md hazır"],
        expected_schema_version="v2.2-sidecar-jsonl-1",
        expected_tokenizer="sp64_protected_passthrough_sidecar",
        closed_route_enum=True,
    )

    assert stats.ok
    assert stats.records == 1
    assert stats.spans == 1


def test_schema_contract_rejects_wrong_surface(tmp_path: Path) -> None:
    sidecar_path = tmp_path / "sidecar.jsonl"
    row = _valid_record()
    row["spans"][0]["surface"] = "WRONG"  # type: ignore[index]
    _write_jsonl(sidecar_path, [row])

    stats = audit_sidecar(
        sidecar_path=sidecar_path,
        raw_lines=["README.md hazır"],
        expected_schema_version="v2.2-sidecar-jsonl-1",
        expected_tokenizer="sp64_protected_passthrough_sidecar",
        closed_route_enum=True,
    )

    assert not stats.ok
    assert stats.surface_failures == 1


def test_schema_contract_rejects_missing_required_field(tmp_path: Path) -> None:
    sidecar_path = tmp_path / "sidecar.jsonl"
    row = _valid_record()
    del row["schema_version"]
    _write_jsonl(sidecar_path, [row])

    stats = audit_sidecar(
        sidecar_path=sidecar_path,
        raw_lines=["README.md hazır"],
        expected_schema_version="v2.2-sidecar-jsonl-1",
        expected_tokenizer="sp64_protected_passthrough_sidecar",
        closed_route_enum=True,
    )

    assert not stats.ok
    assert stats.missing_field_failures == 1
