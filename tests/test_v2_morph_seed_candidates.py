import json
from pathlib import Path

from scripts.analyze_v2_morph_seed_candidates import (
    analyze_boundary_jsonl,
    recommendation_for,
    SuffixStats,
    write_tsv,
)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def test_morph_seed_candidate_analysis_counts_collisions(tmp_path: Path):
    boundary_jsonl = tmp_path / "boundaries.jsonl"
    write_jsonl(
        boundary_jsonl,
        [
            {
                "text": "a",
                "pieces": [
                    {"token": "stem", "surface": "stem", "kind": "word_start", "boundary_before": "hard"},
                    {"token": "+ler", "surface": "ler", "kind": "suffix", "boundary_before": "soft"},
                    {"token": "+den", "surface": "den", "kind": "suffix", "boundary_before": "soft"},
                ],
            },
            {
                "text": "b",
                "pieces": [
                    {"token": "ler", "surface": "ler", "kind": "word_start", "boundary_before": "hard"},
                    {"token": "stem", "surface": "stem", "kind": "word_start", "boundary_before": "hard"},
                    {"token": "+ler", "surface": "ler", "kind": "suffix", "boundary_before": "soft"},
                ],
            },
        ],
    )

    rows, summary = analyze_boundary_jsonl(
        boundary_jsonl,
        min_count=1,
        min_surface_len=3,
        max_collision_rate=0.10,
        protected_tail_hard_share=0.25,
        progress=0,
    )
    by_token = {row.token: row for row in rows}

    assert summary.lines == 2
    assert summary.suffix_unique == 2
    assert by_token["+ler"].total_count == 2
    assert by_token["+ler"].non_suffix_exact_count == 1
    assert by_token["+ler"].recommendation == "review"
    assert by_token["+den"].recommendation == "uds_or_seed_candidate"

    out = tmp_path / "candidates.tsv"
    write_tsv(out, rows)
    assert "exact_collision_rate" in out.read_text(encoding="utf-8")


def test_recommendation_for_protected_tail_review():
    stats = SuffixStats(token="+den", surface="den", total_count=10, soft_count=6, hard_count=4)

    assert (
        recommendation_for(
            stats,
            non_suffix_exact_count=0,
            min_count=5,
            min_surface_len=3,
            max_collision_rate=0.05,
            protected_tail_hard_share=0.25,
        )
        == "protected_tail_review"
    )

