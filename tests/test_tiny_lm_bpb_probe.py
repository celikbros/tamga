from pathlib import Path

from scripts.run_tiny_lm_bpb_probe import (
    UNK_ID,
    TokenizerConfig,
    _processor_encode_ids_lossless_or_byte_fallback,
    _processor_encode_presplit_segment_ids,
    _processor_encode_ids_with_boundary_byte_fallback,
    encode_boundary_biased_unigram_line_ids,
    encode_finite_protected_soft_marker_line_ids,
    encode_tokenizer,
    format_report,
    load_probe_config,
    load_split_texts,
)
from scripts.sweep_v2_boundary_biased_unigram import BoundaryBiasedVocab, VocabEntry


def _write_split(root: Path):
    root.mkdir()
    for split in ("train", "valid", "test"):
        (root / f"{split}.txt").write_text(
            "Türkiye'de test yaptık.\nREADME.md dosyası hazır.\n",
            encoding="utf-8",
        )


class FakeIdProcessor:
    def EncodeAsIds(self, surface: str) -> list[int]:
        return [10 + len(surface)]


class RecordingProcessor:
    def __init__(self):
        self.surfaces: list[str] = []

    def EncodeAsIds(self, surface: str) -> list[int]:
        self.surfaces.append(surface)
        return [10 + len(surface)]


class FakePieceProcessor:
    def __init__(self):
        self.piece_to_id = {
            "Kitaplar": 11,
            "Kitap": 12,
            "lar": 13,
            "2024": 14,
        }
        self.surfaces: list[str] = []

    def PieceToId(self, piece: str) -> int:
        return self.piece_to_id.get(piece, -1)

    def EncodeAsIds(self, surface: str) -> list[int]:
        self.surfaces.append(surface)
        return [self.piece_to_id.get(surface, 99)]


class FakeLossyDecodeProcessor:
    def EncodeAsIds(self, surface: str) -> list[int]:
        mapping = {
            "A": [101],
            "B": [102],
            "AB": [103],
        }
        return mapping.get(surface, [0])

    def DecodeIds(self, ids: list[int]) -> str:
        mapping = {
            (101,): "A",
            (102,): "B",
            (103,): "AB",
            (0,): "�",
        }
        return mapping.get(tuple(ids), "�")


def _toy_boundary_vocab() -> BoundaryBiasedVocab:
    return BoundaryBiasedVocab(
        entries_by_surface={
            "Kitaplar": VocabEntry(
                piece="Kitaplar",
                surface="Kitaplar",
                score=-1.0,
                word_start=False,
            ),
            "Kitap": VocabEntry(
                piece="Kitap",
                surface="Kitap",
                score=-0.7,
                word_start=False,
            ),
            "lar": VocabEntry(piece="lar", surface="lar", score=-0.7, word_start=False),
        },
        start_entries_by_surface={},
        max_entry_len=8,
        max_start_entry_len=0,
    )


def test_utf8_byte_encoding_is_fixed_vocab(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    splits = load_split_texts(split_dir)

    encoded = encode_tokenizer(TokenizerConfig("utf8_byte", "utf8_byte"), splits)

    assert encoded.status == "ok"
    assert encoded.vocab_size == 257
    assert encoded.splits["train"].tokens > encoded.splits["train"].bytes


def test_custom_encoding_reports_oov_on_eval_split(tmp_path: Path):
    split_dir = tmp_path / "split"
    split_dir.mkdir()
    (split_dir / "train.txt").write_text("Eğitim satırı.\n", encoding="utf-8")
    (split_dir / "valid.txt").write_text("Görülmeyen satır.\n", encoding="utf-8")
    (split_dir / "test.txt").write_text("Başka satır.\n", encoding="utf-8")
    splits = load_split_texts(split_dir)

    encoded = encode_tokenizer(
        TokenizerConfig("custom_tr_morph_lossless", "custom", max_vocab_size=300),
        splits,
    )

    assert encoded.status == "ok"
    assert encoded.splits["train"].oov_tokens == 0
    assert encoded.splits["valid"].oov_tokens > 0
    assert UNK_ID not in encoded.splits["valid"].ids


def test_finite_protected_soft_marker_line_ids_preserve_protected_piece_path():
    ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
        "README.md'yi kitaplardan.",
        processor=FakeIdProcessor(),
        selected_pieces=["README", ".md"],
        protected_piece_offset=1000,
    )

    assert 1000 in ids
    assert 1001 in ids
    assert byte_tokens == 0
    assert ids


def test_finite_protected_marker_stripped_line_ids_do_not_insert_marker():
    processor = RecordingProcessor()

    ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
        "Kitaplardan geldim.",
        processor=processor,
        selected_pieces=[],
        protected_piece_offset=1000,
        insert_soft_markers=False,
    )

    assert ids
    assert byte_tokens == 0
    assert processor.surfaces == ["Kitaplardan geldim."]
    assert all("\ue000" not in surface for surface in processor.surfaces)


def test_finite_protected_numeric_sp_passthrough_uses_processor():
    processor = RecordingProcessor()

    ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
        "2024 test.",
        processor=processor,
        selected_pieces=[],
        protected_piece_offset=1000,
        insert_soft_markers=False,
        numeric_sp_passthrough=True,
    )

    assert processor.surfaces == ["2024 test."]
    assert byte_tokens == 0
    assert ids


def test_finite_protected_route_sp_passthrough_keeps_inline_segment():
    processor = RecordingProcessor()

    ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
        "README.md dosyası hazır.",
        processor=processor,
        selected_pieces=["README", ".md"],
        protected_piece_offset=1000,
        insert_soft_markers=False,
        sp_passthrough_routes=frozenset({"file_like"}),
    )

    assert processor.surfaces == ["README.md dosyası hazır."]
    assert byte_tokens == 0
    assert ids
    assert 1000 not in ids
    assert 1001 not in ids


def test_finite_protected_route_sp_passthrough_can_isolate_segment():
    processor = RecordingProcessor()

    ids, byte_tokens = encode_finite_protected_soft_marker_line_ids(
        "README.md dosyası hazır.",
        processor=processor,
        selected_pieces=["README", ".md"],
        protected_piece_offset=1000,
        insert_soft_markers=False,
        sp_passthrough_routes=frozenset({"file_like"}),
        isolate_sp_passthrough_routes=True,
    )

    assert processor.surfaces == ["README.md", " dosyası hazır."]
    assert byte_tokens == 0
    assert ids
    assert 1000 not in ids
    assert 1001 not in ids


def test_finite_protected_route_sp_passthrough_can_byte_fallback_crossing_piece():
    class CrossingProcessor:
        def EncodeAsImmutableProto(self, surface: str):
            class Piece:
                def __init__(self, begin, end, piece_id):
                    self.begin = begin
                    self.end = end
                    self.id = piece_id

            class Proto:
                pieces = [Piece(0, 9, 42)]

            return Proto()

    ids, byte_tokens = _processor_encode_ids_with_boundary_byte_fallback(
        CrossingProcessor(),
        "README.md",
        boundaries={6},
        byte_offset=1002,
    )

    assert ids == [1002 + byte for byte in b"README.md"]
    assert byte_tokens == len(b"README.md")


def test_boundary_byte_fallback_also_replaces_unknown_piece():
    class UnknownProcessor:
        def unk_id(self):
            return 0

        def EncodeAsImmutableProto(self, surface: str):
            class Piece:
                def __init__(self, begin, end, piece_id):
                    self.begin = begin
                    self.end = end
                    self.id = piece_id

            class Proto:
                pieces = [Piece(0, 1, 11), Piece(1, 2, 0), Piece(2, 3, 12)]

            return Proto()

    ids, byte_tokens = _processor_encode_ids_with_boundary_byte_fallback(
        UnknownProcessor(),
        "AâB",
        boundaries=set(),
        byte_offset=1000,
    )

    assert ids == [11, 1000 + 0xC3, 1000 + 0xA2, 12]
    assert byte_tokens == 2


def test_presplit_segment_suppresses_interior_dummy_prefix_with_piece():
    class PresplitProcessor:
        def unk_id(self):
            return 0

        def eos_id(self):
            return 2

        def IdToPiece(self, piece_id: int):
            return {11: "▁README", 12: "README"}[piece_id]

        def PieceToId(self, piece: str):
            return {"README": 12}.get(piece, -1)

        def EncodeAsImmutableProto(self, surface: str):
            class Piece:
                def __init__(self, begin, end, piece_id):
                    self.begin = begin
                    self.end = end
                    self.id = piece_id

            class Proto:
                pieces = [Piece(0, len(surface), 11)]

            return Proto()

    ids, byte_tokens = _processor_encode_presplit_segment_ids(
        PresplitProcessor(),
        "README",
        starts_at_line_start=False,
        byte_offset=1000,
    )

    assert ids == [12]
    assert byte_tokens == 0


def test_presplit_segment_falls_back_when_dummy_stripped_piece_missing():
    class PresplitProcessor:
        def unk_id(self):
            return 0

        def eos_id(self):
            return 2

        def IdToPiece(self, piece_id: int):
            return {11: "▁README"}[piece_id]

        def PieceToId(self, piece: str):
            return -1

        def EncodeAsImmutableProto(self, surface: str):
            class Piece:
                def __init__(self, begin, end, piece_id):
                    self.begin = begin
                    self.end = end
                    self.id = piece_id

            class Proto:
                pieces = [Piece(0, len(surface), 11)]

            return Proto()

    ids, byte_tokens = _processor_encode_presplit_segment_ids(
        PresplitProcessor(),
        "README",
        starts_at_line_start=False,
        byte_offset=1000,
    )

    assert ids == [1000 + byte for byte in b"README"]
    assert byte_tokens == len(b"README")


def test_lossless_sp_helper_falls_back_to_utf8_bytes_for_unknown_chars():
    ids, byte_tokens = _processor_encode_ids_lossless_or_byte_fallback(
        FakeLossyDecodeProcessor(),
        "A⌀B",
        byte_offset=1000,
    )

    assert ids == [101, 1000 + 0xE2, 1000 + 0x8C, 1000 + 0x80, 102]
    assert byte_tokens == 3


def test_boundary_biased_unigram_line_ids_use_boundary_penalty():
    processor = FakePieceProcessor()

    low_lambda_ids, _low_bytes = encode_boundary_biased_unigram_line_ids(
        "Kitaplar",
        processor=processor,
        boundary_vocab=_toy_boundary_vocab(),
        selected_pieces=[],
        protected_piece_offset=1000,
        boundary_lambda=0.0,
    )
    high_lambda_ids, _high_bytes = encode_boundary_biased_unigram_line_ids(
        "Kitaplar",
        processor=processor,
        boundary_vocab=_toy_boundary_vocab(),
        selected_pieces=[],
        protected_piece_offset=1000,
        boundary_lambda=1.0,
    )

    assert low_lambda_ids == [11]
    assert high_lambda_ids == [12, 13]


def test_config_and_dry_report(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        f"""
[settings]
split_dir = "{split_dir.as_posix()}"
output_dir = "{(tmp_path / 'private').as_posix()}"
report_out = "{(tmp_path / 'report.md').as_posix()}"
seed = 1

[model]
seq_len = 8
batch_size = 2
max_steps = 1
eval_interval = 1
learning_rate = 0.001
d_model = 16
n_layers = 1
n_heads = 1
ff_mult = 2
dropout = 0.0
device = "cpu"

[[tokenizers]]
name = "utf8_byte"
kind = "utf8_byte"
""",
        encoding="utf-8",
    )

    config = load_probe_config(config_path)
    encoded = [encode_tokenizer(config.tokenizers[0], load_split_texts(config.split_dir))]
    report = format_report(config, encoded, [], dry_run=True)

    assert "Tiny LM Bits-Per-Byte Probe" in report
    assert "utf8_byte" in report


def test_config_accepts_finite_protected_soft_marker(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    model_path = tmp_path / "soft.model"
    selected_path = tmp_path / "pieces.tsv"
    model_path.write_text("fake", encoding="utf-8")
    selected_path.write_text("piece\tcount\tcategory\treason\tbytes\troutes\n", encoding="utf-8")
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        f"""
[settings]
split_dir = "{split_dir.as_posix()}"
output_dir = "{(tmp_path / 'private').as_posix()}"
report_out = "{(tmp_path / 'report.md').as_posix()}"
seed = 1

[model]
seq_len = 8
batch_size = 2
max_steps = 1
eval_interval = 1
learning_rate = 0.001
d_model = 16
n_layers = 1
n_heads = 1
ff_mult = 2
dropout = 0.0
device = "cpu"

[[tokenizers]]
name = "finite"
kind = "finite_protected_soft_marker"
path = "{model_path.as_posix()}"
selected_pieces = "{selected_path.as_posix()}"
""",
        encoding="utf-8",
    )

    config = load_probe_config(config_path)

    assert config.tokenizers[0].kind == "finite_protected_soft_marker"
    assert config.tokenizers[0].path == model_path
    assert config.tokenizers[0].selected_pieces == selected_path


def test_config_accepts_finite_protected_marker_stripped(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    model_path = tmp_path / "soft.model"
    selected_path = tmp_path / "pieces.tsv"
    model_path.write_text("fake", encoding="utf-8")
    selected_path.write_text("piece\tcount\tcategory\treason\tbytes\troutes\n", encoding="utf-8")
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        f"""
[settings]
split_dir = "{split_dir.as_posix()}"
output_dir = "{(tmp_path / 'private').as_posix()}"
report_out = "{(tmp_path / 'report.md').as_posix()}"
seed = 1

[model]
seq_len = 8
batch_size = 2
max_steps = 1
eval_interval = 1
learning_rate = 0.001
d_model = 16
n_layers = 1
n_heads = 1
ff_mult = 2
dropout = 0.0
device = "cpu"

[[tokenizers]]
name = "finite_marker_stripped"
kind = "finite_protected_marker_stripped"
path = "{model_path.as_posix()}"
selected_pieces = "{selected_path.as_posix()}"
""",
        encoding="utf-8",
    )

    config = load_probe_config(config_path)

    assert config.tokenizers[0].kind == "finite_protected_marker_stripped"
    assert config.tokenizers[0].path == model_path
    assert config.tokenizers[0].selected_pieces == selected_path


def test_config_accepts_finite_protected_numeric_sp(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    model_path = tmp_path / "soft.model"
    selected_path = tmp_path / "pieces.tsv"
    model_path.write_text("fake", encoding="utf-8")
    selected_path.write_text("README\t10\n", encoding="utf-8")
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        f"""
[settings]
split_dir = "{split_dir.as_posix()}"
output_dir = "{(tmp_path / 'private').as_posix()}"
report_out = "{(tmp_path / 'report.md').as_posix()}"
seed = 1

[model]
seq_len = 8
batch_size = 2
max_steps = 1
eval_interval = 1
learning_rate = 0.001
d_model = 16
n_layers = 1
n_heads = 1
ff_mult = 2
dropout = 0.0
device = "cpu"

[[tokenizers]]
name = "finite_numeric_sp"
kind = "finite_protected_marker_stripped_numeric_sp"
path = "{model_path.as_posix()}"
selected_pieces = "{selected_path.as_posix()}"
""",
        encoding="utf-8",
    )

    config = load_probe_config(config_path)

    assert config.tokenizers[0].kind == "finite_protected_marker_stripped_numeric_sp"
    assert config.tokenizers[0].path == model_path
    assert config.tokenizers[0].selected_pieces == selected_path


def test_config_accepts_sp_passthrough_routes(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    model_path = tmp_path / "soft.model"
    selected_path = tmp_path / "pieces.tsv"
    model_path.write_text("fake", encoding="utf-8")
    selected_path.write_text("README\t10\n", encoding="utf-8")
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        f"""
[settings]
split_dir = "{split_dir.as_posix()}"
output_dir = "{(tmp_path / 'private').as_posix()}"
report_out = "{(tmp_path / 'report.md').as_posix()}"
seed = 1

[model]
seq_len = 8
batch_size = 2
max_steps = 1
eval_interval = 1
learning_rate = 0.001
d_model = 16
n_layers = 1
n_heads = 1
ff_mult = 2
dropout = 0.0
device = "cpu"

[[tokenizers]]
name = "finite_route_sp"
kind = "finite_protected_marker_stripped_numeric_sp"
path = "{model_path.as_posix()}"
selected_pieces = "{selected_path.as_posix()}"
sp_passthrough_routes = ["file_like", "apostrophe_surface"]
isolate_sp_passthrough_routes = true
byte_fallback_crossing_pieces = true
pre_split_sp_passthrough_routes = true
""",
        encoding="utf-8",
    )

    config = load_probe_config(config_path)

    assert config.tokenizers[0].sp_passthrough_routes == frozenset(
        {"file_like", "apostrophe_surface"}
    )
    assert config.tokenizers[0].isolate_sp_passthrough_routes is True
    assert config.tokenizers[0].byte_fallback_crossing_pieces is True
    assert config.tokenizers[0].pre_split_sp_passthrough_routes is True


def test_v2_1_sidecar_configs_include_required_passthrough_routes():
    config = load_probe_config(Path("configs/v2_1_tiny_lm_edge_safe_route_passthrough.toml"))
    sidecar_names = {
        "sp64_protected_edge_safe_sidecar",
        "sp64_protected_passthrough_sidecar",
        "sp64_protected_presplit_sidecar",
    }
    required_routes = {"percent_encoded", "azerbaijani_word"}

    sidecar_configs = {
        tokenizer.name: tokenizer
        for tokenizer in config.tokenizers
        if tokenizer.name in sidecar_names
    }

    assert set(sidecar_configs) == sidecar_names
    for tokenizer in sidecar_configs.values():
        assert required_routes.issubset(tokenizer.sp_passthrough_routes)


def test_config_accepts_boundary_biased_unigram(tmp_path: Path):
    split_dir = tmp_path / "split"
    _write_split(split_dir)
    model_path = tmp_path / "sp.model"
    vocab_path = tmp_path / "sp.vocab"
    selected_path = tmp_path / "pieces.tsv"
    model_path.write_text("fake", encoding="utf-8")
    vocab_path.write_text("fake\t0\n", encoding="utf-8")
    selected_path.write_text("README\t10\n", encoding="utf-8")
    config_path = tmp_path / "probe.toml"
    config_path.write_text(
        f"""
[settings]
split_dir = "{split_dir.as_posix()}"
output_dir = "{(tmp_path / 'private').as_posix()}"
report_out = "{(tmp_path / 'report.md').as_posix()}"
seed = 1

[model]
seq_len = 8
batch_size = 2
max_steps = 1
eval_interval = 1
learning_rate = 0.001
d_model = 16
n_layers = 1
n_heads = 1
ff_mult = 2
dropout = 0.0
device = "cpu"

[[tokenizers]]
name = "biased"
kind = "boundary_biased_unigram_numeric_sp"
path = "{model_path.as_posix()}"
vocab_path = "{vocab_path.as_posix()}"
selected_pieces = "{selected_path.as_posix()}"
boundary_lambda = 4.0
""",
        encoding="utf-8",
    )

    config = load_probe_config(config_path)

    assert config.tokenizers[0].kind == "boundary_biased_unigram_numeric_sp"
    assert config.tokenizers[0].vocab_path == vocab_path
    assert config.tokenizers[0].boundary_lambda == 4.0
