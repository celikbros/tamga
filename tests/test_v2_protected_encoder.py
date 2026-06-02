from pathlib import Path

from scripts.analyze_v2_protected_route_inventory import load_route_inventory
from scripts.evaluate_v2_protected_encoder import (
    evaluate_encoder,
    format_report,
    greedy_encode_surface,
    load_selected_pieces,
)


def test_greedy_protected_encoder_uses_pieces_then_byte_fallback():
    encoded = greedy_encode_surface("abç", ["ab"])

    assert encoded.piece_tokens == 1
    assert encoded.byte_tokens == len("ç".encode("utf-8"))
    assert encoded.total_tokens == 3


def test_evaluate_protected_encoder_reports_route_pressure(tmp_path: Path):
    inventory_path = tmp_path / "inventory.tsv"
    selected_path = tmp_path / "selected.tsv"
    inventory_path.write_text(
        "category\troute\tsurface\tcount\tbytes\n"
        "protected\tfile_like\tREADME.md\t2\t9\n"
        "protected\tnumeric_like\t2026\t3\t4\n",
        encoding="utf-8",
    )
    selected_path.write_text(
        "piece\tcount\tcategory\treason\tbytes\troutes\n"
        ".md\t2\textension\tprotected_extension\t3\tfile_like\n"
        "R\t2\tchar_ascii_alpha\tprotected_char\t1\tfile_like\n"
        "E\t2\tchar_ascii_alpha\tprotected_char\t1\tfile_like\n"
        "A\t2\tchar_ascii_alpha\tprotected_char\t1\tfile_like\n"
        "D\t2\tchar_ascii_alpha\tprotected_char\t1\tfile_like\n"
        "M\t2\tchar_ascii_alpha\tprotected_char\t1\tfile_like\n"
        "0\t3\tchar_digit\tprotected_char\t1\tnumeric_like\n"
        "2\t3\tchar_digit\tprotected_char\t1\tnumeric_like\n"
        "6\t3\tchar_digit\tprotected_char\t1\tnumeric_like\n",
        encoding="utf-8",
    )

    stats, route_summary = evaluate_encoder(
        inventory_entries=load_route_inventory(inventory_path),
        selected_pieces=load_selected_pieces(selected_path),
    )

    assert stats.protected_surfaces == 2
    assert stats.byte_fallback_bytes == 0
    assert route_summary["file_like"][0] == 1
    assert route_summary["numeric_like"][1] == 3

    report = format_report(
        inventory_path=inventory_path,
        selected_path=selected_path,
        stats=stats,
        route_summary=route_summary,
    )

    assert "Protected Encoder Diagnostic" in report
    assert "tokens/source byte" in report
