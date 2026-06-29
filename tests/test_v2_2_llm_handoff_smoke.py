from scripts.audit_v2_1_sidecar_operation_simulation import Span
from scripts.audit_v2_2_llm_handoff_smoke import (
    SmokeResult,
    SmokeStats,
    format_report,
    sidecar_record,
    validate_sidecar_spans,
)
from pathlib import Path


def test_validate_sidecar_spans_accepts_byte_exact_surface() -> None:
    text = "URL %20'si goruldu"
    span = Span(
        route="percent_encoded",
        surface="%20",
        char_start=4,
        char_end=7,
        byte_start=4,
        byte_end=7,
    )

    assert validate_sidecar_spans(text, [span]) == (0, 0, 0)


def test_validate_sidecar_spans_rejects_wrong_surface() -> None:
    text = "abc Ã§"
    span = Span(
        route="file_like",
        surface="wrong",
        char_start=4,
        char_end=5,
        byte_start=4,
        byte_end=6,
    )

    assert validate_sidecar_spans(text, [span]) == (1, 0, 0)


def test_sidecar_record_keeps_line_level_schema() -> None:
    span = Span(
        route="file_like",
        surface="README.md",
        char_start=0,
        char_end=9,
        byte_start=0,
        byte_end=9,
    )

    record = sidecar_record(
        split="valid",
        line_number=3,
        text="README.md hazir",
        spans=[span],
        token_count=5,
        fallback_source_tokens=0,
    )

    assert record["schema_version"] == "v2.2-sidecar-jsonl-1"
    assert record["tokenizer"] == "sp64_protected_passthrough_sidecar"
    assert record["split"] == "valid"
    assert record["line_number"] == 3
    assert record["token_count"] == 5
    assert record["spans"] == [
        {
            "route": "file_like",
            "byte_start": 0,
            "byte_end": 9,
            "char_start": 0,
            "char_end": 9,
            "surface": "README.md",
        }
    ]


def test_format_report_fails_on_roundtrip_failure(tmp_path: Path) -> None:
    result = SmokeResult(
        rows=[
            SmokeStats(
                split="valid",
                lines=1,
                exact=0,
                failures=1,
                raw_bytes=10,
                decoded_bytes=11,
                total_tokens=3,
                lm_tokens_with_eos=4,
            )
        ]
    )

    report, ok = format_report(
        config_path=Path("config.toml"),
        tokenizer_name="tok",
        input_desc="input",
        result=result,
        sidecar_out=tmp_path / "sidecar.jsonl",
        failures_out=tmp_path / "failures.jsonl",
        vocab_size=100,
        batch_size=1,
        seq_len=2,
        max_fallback_rate=0.1,
        max_extra_mask_bytes_per_byte=0.1,
        route_invariant_ok=True,
    )

    assert not ok
    assert "| `exact_roundtrip` | FAIL |" in report
    assert "| `overall` | FAIL |" in report
