from __future__ import annotations

from pathlib import Path

from scripts.materialize_hybrid_pretok_corpus import (
    morph_pretokenize_line,
    write_hybrid_pretok_corpus,
)


def test_morph_pretokenize_line_uses_custom_boundaries():
    assert morph_pretokenize_line("Turkiye'den geldim.") == [
        "\u2581Turkiye",
        "'",
        "+den",
        "\u2581gel",
        "+di",
        "+m",
        ".",
    ]


def test_write_hybrid_pretok_corpus_writes_space_separated_pieces(tmp_path: Path):
    source = tmp_path / "train.txt"
    target = tmp_path / "train.morph_pretok.txt"
    source.write_text("Turkiye'den geldim.\nREADME.md'yi actim.\n", encoding="utf-8")

    stats = write_hybrid_pretok_corpus(source, target)

    lines = target.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "\u2581Turkiye ' +den \u2581gel +di +m ."
    assert stats.lines == 2
    assert stats.morph_tokens > 0
