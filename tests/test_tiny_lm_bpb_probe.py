from pathlib import Path

from scripts.run_tiny_lm_bpb_probe import (
    UNK_ID,
    TokenizerConfig,
    encode_finite_protected_soft_marker_line_ids,
    encode_tokenizer,
    format_report,
    load_probe_config,
    load_split_texts,
)


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
