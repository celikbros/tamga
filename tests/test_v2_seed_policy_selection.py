from pathlib import Path

from scripts.analyze_v2_seed_vocab import SeedEntry
from scripts.select_v2_seed_policy import (
    format_report,
    seed_category,
    select_seed_entries,
    write_selected_tsv,
)


def test_seed_policy_selects_mandatory_groups_and_top_word_start(tmp_path: Path):
    entries = [
        SeedEntry("+ler", 20),
        SeedEntry("README.md", 18),
        SeedEntry(".", 15),
        SeedEntry("abc", 5),
        SeedEntry("▁high", 10),
        SeedEntry("▁low", 1),
    ]

    selected, stats = select_seed_entries(
        entries,
        budget=5,
        min_word_start_count=2,
        min_protected_count=2,
    )

    tokens = {entry.token for entry in selected}
    assert "+ler" in tokens
    assert "README.md" in tokens
    assert "." in tokens
    assert "abc" in tokens
    assert "▁high" in tokens
    assert "▁low" not in tokens
    assert stats.selected_unique == 5


def test_seed_policy_report_and_private_tsv(tmp_path: Path):
    selected, stats = select_seed_entries(
        [
            SeedEntry("+ler", 20),
            SeedEntry("README.md", 18),
            SeedEntry("▁high", 10),
        ],
        budget=10,
        min_word_start_count=1,
        min_protected_count=2,
    )
    selected_path = tmp_path / "selected.tsv"
    write_selected_tsv(selected_path, selected)

    assert "category" in selected_path.read_text(encoding="utf-8")
    assert seed_category("README.md").startswith("protected:")

    report = format_report(
        seed_path=tmp_path / "seed.tsv",
        selected_path=selected_path,
        selected=selected,
        stats=stats,
        min_protected_count=2,
        include_protected=True,
    )

    assert "v2.0 Seed Policy Selection" in report
    assert "selected coverage" in report
