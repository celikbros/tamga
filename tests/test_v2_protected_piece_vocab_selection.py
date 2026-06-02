from pathlib import Path

from scripts.analyze_v2_protected_route_inventory import load_route_inventory
from scripts.select_v2_protected_piece_vocab import (
    build_candidates,
    format_report,
    select_candidates,
    write_selected_tsv,
)


def test_select_protected_piece_vocab_keeps_subpieces_not_full_surfaces(tmp_path: Path):
    inventory_path = tmp_path / "inventory.tsv"
    selected_path = tmp_path / "selected.tsv"
    inventory_path.write_text(
        "category\troute\tsurface\tcount\tbytes\n"
        "protected\tfile_like\tREADME.md\t20\t9\n"
        "protected\tfile_like\tconfig.json\t10\t11\n"
        "protected\turl\thttps://example.com/a.json\t8\t26\n"
        "protected\tnumeric_like\t2026\t50\t4\n",
        encoding="utf-8",
    )

    entries = load_route_inventory(inventory_path)
    candidates = build_candidates(entries)
    selected, stats = select_candidates(
        candidates,
        budget=100,
        min_char_count=1,
        min_delimiter_count=1,
        min_extension_count=1,
        min_literal_count=1,
    )
    write_selected_tsv(selected_path, selected)

    pieces = {candidate.piece for candidate in selected}
    assert ".md" in pieces
    assert ".json" in pieces
    assert "://" in pieces
    assert "https" in pieces
    assert "README.md" not in pieces
    assert "config.json" not in pieces
    assert stats.selected_unique > 0

    report = format_report(
        inventory_path=inventory_path,
        selected_path=selected_path,
        selected=selected,
        stats=stats,
        min_char_count=1,
        min_delimiter_count=1,
        min_extension_count=1,
        min_literal_count=1,
    )

    assert "Protected Piece Vocabulary Selection" in report
    assert "README.md" not in report
    assert "config.json" not in report
    assert "mandatory byte fallback pieces" in report
