from pathlib import Path

from scripts.materialize_v2_partial_boundary_sp_view import (
    BOUNDARY_MARKER,
    marked_line,
    materialize_train_view,
)


def test_marked_line_inserts_marker_before_soft_suffix_boundary():
    view, inserted = marked_line("Kitaplardan geldim.", marker=BOUNDARY_MARKER)

    assert inserted > 0
    assert BOUNDARY_MARKER in view
    assert view.replace(BOUNDARY_MARKER, "") == "Kitaplardan geldim."


def test_materialize_train_view_respects_zero_rho(tmp_path: Path):
    source = tmp_path / "train.txt"
    target = tmp_path / "view.txt"
    source.write_text("Kitaplardan geldim.\n", encoding="utf-8")

    stats = materialize_train_view(
        input_path=source,
        output_path=target,
        rho=0.0,
        seed=1,
        marker=BOUNDARY_MARKER,
        progress=0,
    )

    assert stats.inserted_markers == 0
    assert target.read_text(encoding="utf-8") == "Kitaplardan geldim.\n"
