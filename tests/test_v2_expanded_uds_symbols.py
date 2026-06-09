from pathlib import Path

from scripts.materialize_v2_expanded_uds_symbols import (
    format_report,
    load_candidates,
    select_rows,
    write_symbols,
)


HEADER = (
    "token\tsurface\ttotal_count\tsoft_count\thard_count\t"
    "non_suffix_exact_count\tword_start_exact_count\tother_exact_count\t"
    "surface_len\tsoft_share\thard_share\texact_collision_rate\trecommendation\n"
)


def _row(
    token: str,
    surface: str,
    *,
    count: int = 1000,
    surface_len: int = 3,
    hard_share: float = 0.0,
    collision: float = 0.0,
    recommendation: str = "uds_or_seed_candidate",
) -> str:
    return (
        f"{token}\t{surface}\t{count}\t{count}\t0\t0\t0\t0\t"
        f"{surface_len}\t1.0\t{hard_share}\t{collision}\t{recommendation}\n"
    )


def test_select_rows_uses_conservative_thresholds(tmp_path: Path):
    candidates = tmp_path / "candidates.tsv"
    candidates.write_text(
        HEADER
        + _row("+ler", "ler", count=2000)
        + _row("+ecek", "ecek", count=3000, surface_len=4)
        + _row("+de", "de", surface_len=2)
        + _row("+dan", "dan", hard_share=0.02)
        + _row("+den", "den", collision=0.01)
        + _row("+foo", "foo", recommendation="seed_bias_candidate"),
        encoding="utf-8",
    )

    selection = select_rows(
        load_candidates(candidates),
        min_count=100,
        min_surface_len=3,
        max_hard_share=0.01,
        max_collision_rate=0.001,
        recommendation="uds_or_seed_candidate",
        max_symbols=64,
    )

    assert [row.surface for row in selection.rows] == ["ecek", "ler"]


def test_write_symbols_and_report(tmp_path: Path):
    candidates = tmp_path / "candidates.tsv"
    candidates.write_text(
        HEADER
        + _row("+ecek", "ecek", count=3000, surface_len=4)
        + _row("+ler", "ler", count=2000),
        encoding="utf-8",
    )
    selection = select_rows(
        load_candidates(candidates),
        min_count=100,
        min_surface_len=3,
        max_hard_share=0.01,
        max_collision_rate=0.001,
        recommendation="uds_or_seed_candidate",
        max_symbols=64,
    )
    out = tmp_path / "symbols.txt"

    write_symbols(selection, out)
    report = format_report(
        candidates_path=candidates,
        symbols_out=out,
        selection=selection,
        min_count=100,
        min_surface_len=3,
        max_hard_share=0.01,
        max_collision_rate=0.001,
        recommendation="uds_or_seed_candidate",
        max_symbols=64,
    )

    assert out.read_text(encoding="utf-8") == "ecek\nler\n"
    assert "selected symbols | 2" in report
    assert "`+ecek`" in report
    assert "constrained/MorphBPE" in report
