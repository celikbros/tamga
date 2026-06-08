from pathlib import Path

from scripts.select_v2_morph_seed_policy import (
    choose_action,
    load_candidates,
    MorphSeedCandidate,
    select_policy,
    write_policy,
)


def candidate(
    token: str,
    *,
    surface: str,
    count: int,
    surface_len: int,
    recommendation: str,
    hard_share: float = 0.0,
    collision: float = 0.0,
) -> MorphSeedCandidate:
    return MorphSeedCandidate(
        token=token,
        surface=surface,
        total_count=count,
        soft_count=int(count * (1 - hard_share)),
        hard_count=int(count * hard_share),
        non_suffix_exact_count=int(count * collision),
        word_start_exact_count=int(count * collision),
        other_exact_count=0,
        surface_len=surface_len,
        soft_share=1 - hard_share,
        hard_share=hard_share,
        exact_collision_rate=collision,
        recommendation=recommendation,
    )


def test_choose_action_keeps_first_run_soft():
    safe_long = candidate(
        "+ecek",
        surface="ecek",
        count=1000,
        surface_len=4,
        recommendation="uds_or_seed_candidate",
    )
    short = candidate(
        "+ler",
        surface="ler",
        count=1000,
        surface_len=3,
        recommendation="uds_or_seed_candidate",
    )
    protected = candidate(
        "+nin",
        surface="nin",
        count=1000,
        surface_len=3,
        recommendation="protected_tail_review",
        hard_share=0.8,
    )

    kwargs = dict(
        min_count=100,
        safe_uds_min_len=4,
        safe_uds_max_collision=0.001,
        safe_uds_max_hard_share=0.01,
    )

    assert choose_action(safe_long, **kwargs)[0] == "safe_uds_candidate_later"
    assert choose_action(short, **kwargs)[0] == "seed_bias"
    assert choose_action(protected, **kwargs)[0] == "holdout"


def test_policy_tsv_roundtrip(tmp_path: Path):
    rows = [
        candidate("+ecek", surface="ecek", count=1000, surface_len=4, recommendation="uds_or_seed_candidate"),
        candidate("+da", surface="da", count=900, surface_len=2, recommendation="seed_bias_candidate"),
        candidate("+nin", surface="nin", count=800, surface_len=3, recommendation="protected_tail_review"),
    ]
    entries, stats = select_policy(
        rows,
        min_count=100,
        safe_uds_min_len=4,
        safe_uds_max_collision=0.001,
        safe_uds_max_hard_share=0.01,
    )
    assert stats.selected_unique == 2
    assert stats.heldout_unique == 1

    out = tmp_path / "policy.tsv"
    write_policy(out, entries)
    assert "safe_uds_candidate_later" in out.read_text(encoding="utf-8")

