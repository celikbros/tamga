from pathlib import Path
import json

from scripts.materialize_v2_candidate_serialization import (
    SOFT_MARKER,
    build_training_view,
    materialize_candidate_serialization,
)


def test_build_training_view_uses_soft_marker_and_hard_spaces():
    pieces = [
        {"token": "▁kitap", "surface": "kitap", "kind": "word_start", "boundary_before": "hard"},
        {"token": "+lar", "surface": "lar", "kind": "suffix", "boundary_before": "soft"},
        {"token": " ", "surface": " ", "kind": "whitespace", "boundary_before": "hard"},
        {"token": "README.md", "surface": "README.md", "kind": "protected:file_like", "boundary_before": "hard"},
    ]

    train_view, annotated, segments = build_training_view(pieces, {"▁kitap", "+lar"})

    assert train_view == f"▁kitap{SOFT_MARKER}+lar README.md"
    assert segments == 2
    assert annotated[0]["selected_seed"] is True
    assert annotated[-1]["selected_seed"] is False


def test_materialize_candidate_serialization_writes_outputs(tmp_path: Path):
    boundary_jsonl = tmp_path / "boundaries.jsonl"
    selected_seed = tmp_path / "selected.tsv"
    jsonl_out = tmp_path / "candidate.jsonl"
    train_view_out = tmp_path / "candidate.txt"

    boundary_jsonl.write_text(
        json.dumps(
            {
                "text": "kitaplar README.md",
                "pieces": [
                    {"token": "▁kitap", "surface": "kitap", "kind": "word_start", "boundary_before": "hard"},
                    {"token": "+lar", "surface": "lar", "kind": "suffix", "boundary_before": "soft"},
                    {"token": " ", "surface": " ", "kind": "whitespace", "boundary_before": "hard"},
                    {"token": "README.md", "surface": "README.md", "kind": "protected:file_like", "boundary_before": "hard"},
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    selected_seed.write_text(
        "token\tcount\tcategory\treason\n▁kitap\t10\tword_start\ttop_word_start\n+lar\t5\tsuffix\tall_suffix\n",
        encoding="utf-8",
    )

    stats = materialize_candidate_serialization(
        boundary_jsonl=boundary_jsonl,
        selected_seed=selected_seed,
        jsonl_out=jsonl_out,
        train_view_out=train_view_out,
        max_lines=None,
        progress=0,
    )

    assert stats.lines == 1
    assert stats.selected_pieces == 2
    assert stats.unselected_pieces == 1
    assert json.loads(jsonl_out.read_text(encoding="utf-8"))["text"] == "kitaplar README.md"
    assert SOFT_MARKER in train_view_out.read_text(encoding="utf-8")
