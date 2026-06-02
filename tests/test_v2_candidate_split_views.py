from pathlib import Path

from scripts.materialize_v2_candidate_split_views import (
    format_report,
    materialize_split_views,
)


def test_materialize_candidate_split_views(tmp_path: Path):
    split_dir = tmp_path / "split"
    split_dir.mkdir()
    for split in ("valid", "test"):
        (split_dir / f"{split}.txt").write_text(
            "kitaplardan geldim.\nREADME.md hazir.\n",
            encoding="utf-8",
        )
    selected_seed = tmp_path / "selected.tsv"
    selected_seed.write_text(
        "token\tcount\tcategory\treason\n"
        "▁kitap\t10\tword_start\ttop_word_start\n"
        "+lar\t5\tsuffix\tall_suffix\n"
        "+dan\t4\tsuffix\tall_suffix\n",
        encoding="utf-8",
    )

    results = materialize_split_views(
        split_dir=split_dir,
        selected_seed=selected_seed,
        private_root=tmp_path / "private",
        splits=("valid", "test"),
        progress=0,
    )

    assert [result.split for result in results] == ["valid", "test"]
    assert all(result.boundary_jsonl.exists() for result in results)
    assert all(result.candidate_jsonl.exists() for result in results)
    assert all(result.train_view.exists() for result in results)

    report = format_report(
        split_dir=split_dir,
        selected_seed=selected_seed,
        results=results,
    )

    assert "v2.0 Candidate Split Views" in report
    assert "valid" in report
    assert "test" in report
