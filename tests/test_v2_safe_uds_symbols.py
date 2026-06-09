from pathlib import Path

from scripts.materialize_v2_safe_uds_symbols import (
    format_report,
    load_policy,
    select_rows,
    write_symbols,
)


HEADER = (
    "token\tsurface\ttotal_count\trecommendation\taction\treason\t"
    "soft_share\thard_share\texact_collision_rate\n"
)


def test_select_rows_keeps_only_requested_action(tmp_path: Path):
    policy = tmp_path / "policy.tsv"
    policy.write_text(
        HEADER
        + "+ecek\tecek\t1000\tuds_or_seed_candidate\tsafe_uds_candidate_later\tlong\t1.0\t0.0\t0.0\n"
        + "+lar\tlar\t2000\tuds_or_seed_candidate\tseed_bias\tsafe\t1.0\t0.0\t0.0\n"
        + "+nin\tnin\t300\tprotected_tail_review\tholdout\tprotected\t0.1\t0.9\t0.0\n",
        encoding="utf-8",
    )

    selection = select_rows(load_policy(policy), action="safe_uds_candidate_later")

    assert [row.surface for row in selection.rows] == ["ecek"]
    assert selection.total_count == 1000


def test_write_symbols_and_report(tmp_path: Path):
    policy = tmp_path / "policy.tsv"
    policy.write_text(
        HEADER
        + "+ecek\tecek\t1000\tuds_or_seed_candidate\tsafe_uds_candidate_later\tlong\t1.0\t0.0\t0.0\n"
        + "+acak\tacak\t500\tuds_or_seed_candidate\tsafe_uds_candidate_later\tlong\t1.0\t0.01\t0.001\n",
        encoding="utf-8",
    )
    selection = select_rows(load_policy(policy), action="safe_uds_candidate_later")
    out = tmp_path / "symbols.txt"

    write_symbols(selection, out)
    report = format_report(
        policy_path=policy,
        symbols_out=out,
        action="safe_uds_candidate_later",
        selection=selection,
    )

    assert out.read_text(encoding="utf-8") == "ecek\nacak\n"
    assert "selected symbols | 2" in report
    assert "`+ecek`" in report
    assert "stop this cheap UDS branch" in report
