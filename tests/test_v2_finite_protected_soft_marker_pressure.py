from pathlib import Path

from scripts.measure_v2_finite_protected_soft_marker_pressure import (
    format_report,
    measure_split,
)


class FakeSoftMarkerProcessor:
    def EncodeAsPieces(self, surface: str) -> list[str]:
        return ["\u2581" + surface]


def test_measure_finite_protected_soft_marker_pressure(tmp_path: Path):
    split_path = tmp_path / "valid.txt"
    split_path.write_text("README.md'yi aç.\nkitaplardan geldim.\n", encoding="utf-8")

    row = measure_split(
        split="valid",
        path=split_path,
        processor=FakeSoftMarkerProcessor(),
        selected_pieces=["README", ".md"],
        progress=0,
    )

    assert row.lines == 2
    assert row.bytes > 0
    assert row.model_tokens > 0
    assert row.logical_tokens > 0
    assert row.protected_piece_tokens == 2
    assert row.protected_byte_tokens == 0
    assert row.model_tokens_per_byte > 0

    report = format_report(
        split_dir=tmp_path,
        soft_marker_model=tmp_path / "model.model",
        selected_pieces_path=tmp_path / "pieces.tsv",
        rows=[row],
    )
    assert "Finite Protected Soft-Marker Token Pressure" in report
    assert "SP64 baseline" in report
