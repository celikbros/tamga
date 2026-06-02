from pathlib import Path

from scripts.analyze_v2_protected_route_inventory import (
    format_report,
    load_route_inventory,
    summarize_by_route,
    threshold_rows,
)


def test_protected_route_inventory_analysis_summarizes_without_surfaces(tmp_path: Path):
    inventory_path = tmp_path / "inventory.tsv"
    inventory_path.write_text(
        "category\troute\tsurface\tcount\tbytes\n"
        "protected\tfile_like\tREADME.md\t10\t9\n"
        "protected\tfile_like\tconfig.json\t2\t11\n"
        "protected\tnumeric_like\t2026\t5\t4\n"
        "suffix_tail\tsuffix_tail_after_file_like\tyi\t3\t2\n",
        encoding="utf-8",
    )

    entries = load_route_inventory(inventory_path)
    summary = summarize_by_route([entry for entry in entries if entry.category == "protected"])
    rows = threshold_rows([entry for entry in entries if entry.category == "protected"], (1, 5, 10))

    assert summary["file_like"] == (2, 12, 112)
    assert summary["numeric_like"] == (1, 5, 20)
    assert [row.unique_kept for row in rows] == [3, 2, 1]

    report = format_report(
        inventory_path=inventory_path,
        entries=entries,
        thresholds=(1, 5, 10),
    )

    assert "Protected Route Inventory Analysis" in report
    assert "file_like" in report
    assert "README.md" not in report
    assert "config.json" not in report
