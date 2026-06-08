from pathlib import Path

from scripts.materialize_v2_morph_seed_augmented_view import (
    load_policy,
    materialize_augmented_view,
    repeats_for_count,
    selected_policy_entries,
)


def test_repeats_for_count_caps_and_keeps_one():
    assert repeats_for_count(1, divisor=10, max_repeat=8) == 1
    assert repeats_for_count(10, divisor=10, max_repeat=8) == 1
    assert repeats_for_count(11, divisor=10, max_repeat=8) == 2
    assert repeats_for_count(1000, divisor=10, max_repeat=8) == 8


def test_materialize_augmented_view_appends_selected_policy(tmp_path: Path):
    base = tmp_path / "train.txt"
    base.write_text("Merhaba dünya\nBugün hava güzel\n", encoding="utf-8")
    policy = tmp_path / "policy.tsv"
    policy.write_text(
        "token\tsurface\ttotal_count\trecommendation\taction\treason\tsoft_share\thard_share\texact_collision_rate\n"
        "+lar\tlar\t100\tuds_or_seed_candidate\tseed_bias\tsafe_seed_not_forced\t1.0\t0.0\t0.0\n"
        "+ecek\tecek\t100\tuds_or_seed_candidate\tsafe_uds_candidate_later\tlong\t1.0\t0.0\t0.0\n"
        "+nin\tnin\t100\tprotected_tail_review\tholdout\tprotected\t0.1\t0.9\t0.0\n",
        encoding="utf-8",
    )
    out = tmp_path / "augmented.txt"

    entries = load_policy(policy)
    selected = selected_policy_entries(entries, include_safe_uds_later=False)
    assert [entry.surface for entry in selected] == ["lar"]

    stats = materialize_augmented_view(
        base_train=base,
        policy_path=policy,
        out=out,
        repeat_divisor=100,
        max_repeat_per_entry=8,
        include_safe_uds_later=False,
    )

    text = out.read_text(encoding="utf-8")
    assert "Merhaba dünya" in text
    assert "\nlar\n" in text
    assert "ecek" not in text
    assert stats.augmentation_lines == 1

