from pathlib import Path
import json

from scripts.materialize_v2_soft_morph_artifacts import (
    materialize_soft_morph_artifacts,
    format_report,
)


def test_materialize_soft_morph_artifacts_writes_jsonl_and_seed(tmp_path: Path):
    input_path = tmp_path / "train.txt"
    jsonl_out = tmp_path / "soft.jsonl"
    seed_out = tmp_path / "seed.tsv"
    input_path.write_text(
        "testlerden geldim.\nREADME.md dosyasi hazir.\n",
        encoding="utf-8",
    )

    stats = materialize_soft_morph_artifacts(
        input_path=input_path,
        jsonl_out=jsonl_out,
        seed_out=seed_out,
        max_lines=None,
        progress=0,
    )

    assert stats.lines == 2
    assert stats.pieces > 0
    assert stats.soft_boundaries > 0
    assert jsonl_out.exists()
    assert seed_out.exists()

    first = json.loads(jsonl_out.read_text(encoding="utf-8").splitlines()[0])
    assert first["text"] == "testlerden geldim."
    assert any(piece["boundary_before"] == "soft" for piece in first["pieces"])

    seed_text = seed_out.read_text(encoding="utf-8")
    assert "token\tcount" in seed_text

    report = format_report(
        input_path=input_path,
        jsonl_out=jsonl_out,
        seed_out=seed_out,
        stats=stats,
        max_lines=None,
    )
    assert "v2.0 Soft Morph Artifact Materialization" in report
    assert "soft" in report
