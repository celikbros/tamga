from pathlib import Path
import json

from scripts.materialize_v2_raw_soft_marker_candidate_views import (
    SOFT_MARKER,
    build_raw_soft_marker_view,
    format_report,
    materialize_views,
)


def test_build_raw_soft_marker_view_marks_soft_boundaries_only():
    pieces = [
        {"surface": "kitap", "kind": "word_start", "boundary_before": "hard"},
        {"surface": "lar", "kind": "suffix", "boundary_before": "soft"},
        {"surface": " ", "kind": "whitespace", "boundary_before": "hard"},
        {"surface": "README.md", "kind": "protected:file_like", "boundary_before": "hard"},
        {"surface": "'", "kind": "apostrophe", "boundary_before": "hard"},
        {"surface": "den", "kind": "suffix", "boundary_before": "hard"},
    ]

    view, segments, soft, hard = build_raw_soft_marker_view(pieces)

    assert view == f"kitap{SOFT_MARKER}lar README.md ' den"
    assert segments == 4
    assert soft == 1
    assert hard == 5


def test_materialize_raw_soft_marker_views_writes_split_outputs(tmp_path: Path):
    source_root = tmp_path / "candidate"
    source_root.mkdir()
    source_candidate = "source"
    target_candidate = "soft_marker"
    for split in ("train", "valid", "test"):
        (source_root / f"{source_candidate}.{split}.jsonl").write_text(
            json.dumps(
                {
                    "text": "kitaplar README.md'den",
                    "pieces": [
                        {"surface": "kitap", "kind": "word_start", "boundary_before": "hard"},
                        {"surface": "lar", "kind": "suffix", "boundary_before": "soft"},
                        {"surface": " ", "kind": "whitespace", "boundary_before": "hard"},
                        {"surface": "README.md", "kind": "protected:file_like", "boundary_before": "hard"},
                        {"surface": "'", "kind": "apostrophe", "boundary_before": "hard"},
                        {"surface": "den", "kind": "suffix", "boundary_before": "hard"},
                    ],
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

    results = materialize_views(
        source_root=source_root,
        source_candidate=source_candidate,
        target_candidate=target_candidate,
        splits=("train", "valid", "test"),
        progress=0,
    )
    report = format_report(
        source_root=source_root,
        source_candidate=source_candidate,
        target_candidate=target_candidate,
        results=results,
    )

    assert len(results) == 3
    assert all(result.view_out.exists() for result in results)
    assert SOFT_MARKER in (source_root / "soft_marker.train.txt").read_text(encoding="utf-8")
    assert "v2.0 Raw-Soft-Marker Candidate Views" in report
