from __future__ import annotations

import json

from scripts.tokenize_corpus import iter_line_chunks, sha256_file


def test_iter_line_chunks_preserves_order_and_limit(tmp_path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("a\nb\nc\nd\n", encoding="utf-8")

    chunks = list(iter_line_chunks(path, max_lines=3, chunk_lines=2))

    assert chunks == [[(1, "a"), (2, "b")], [(3, "c")]]


def test_sha256_file_is_stable(tmp_path) -> None:
    path = tmp_path / "data.bin"
    path.write_bytes(b"abc")

    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_checksums_json_shape(tmp_path) -> None:
    path = tmp_path / "checksums.json"
    path.write_text(
        json.dumps({"algorithm": "sha256", "files": {"tokens.bin": "abc"}}),
        encoding="utf-8",
    )

    value = json.loads(path.read_text(encoding="utf-8"))
    assert value["algorithm"] == "sha256"
    assert value["files"]["tokens.bin"] == "abc"
