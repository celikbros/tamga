from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    BYTE_OFFSET,
    BYTE_VOCAB_SIZE,
    EOS_ID,
    build_custom_vocab,
    encode_custom_split,
    encode_sentencepiece_split,
    load_split_texts,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class AccountingRow:
    mode: str
    split: str
    lines: int
    bytes: int
    tokens: int
    vocab_size: int | None = None
    unique_source_tokens: int | None = None
    whitespace_source_tokens: int = 0
    fallback_source_tokens: int = 0
    fallback_byte_ids: int = 0
    notes: str = ""

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.bytes if self.bytes else 0.0

    @property
    def bytes_per_token(self) -> float:
        return self.bytes / self.tokens if self.tokens else 0.0

    @property
    def fallback_source_rate(self) -> float:
        return self.fallback_source_tokens / self.tokens if self.tokens else 0.0


def _limited_lines(lines: list[str], max_lines: int | None) -> list[str]:
    if max_lines is None:
        return lines
    return lines[:max_lines]


def _token_is_whitespace(token: str) -> bool:
    return token != "" and token.strip() == ""


def _count_custom_mode(
    *,
    mode: str,
    split_name: str,
    lines: list[str],
    byte_count: int,
    preserve_whitespace: bool,
) -> AccountingRow:
    tokenizer = TurkishTokenizer(preserve_whitespace=preserve_whitespace)
    tokens = 0
    source_counts: Counter[str] = Counter()
    whitespace_tokens = 0
    for line in lines:
        pieces = tokenizer.encode(line)
        tokens += len(pieces) + 1
        source_counts.update(pieces)
        whitespace_tokens += sum(1 for piece in pieces if _token_is_whitespace(piece))

    return AccountingRow(
        mode=mode,
        split=split_name,
        lines=len(lines),
        bytes=byte_count,
        tokens=tokens,
        unique_source_tokens=len(source_counts),
        whitespace_source_tokens=whitespace_tokens,
    )


def _count_custom_lossless_fallback(
    *,
    split_name: str,
    lines: list[str],
    byte_count: int,
    vocab: dict[str, int],
    max_vocab_size: int,
) -> AccountingRow:
    encoded = encode_custom_split(lines, vocab, byte_count, split_name)
    fallback_byte_ids = sum(
        1
        for token_id in encoded.ids
        if BYTE_OFFSET <= token_id < BYTE_OFFSET + BYTE_VOCAB_SIZE
    )
    return AccountingRow(
        mode=f"custom_lossless_{max_vocab_size}_byte_fallback",
        split=split_name,
        lines=encoded.lines,
        bytes=encoded.bytes,
        tokens=encoded.tokens,
        vocab_size=len(vocab),
        fallback_source_tokens=encoded.oov_tokens,
        fallback_byte_ids=fallback_byte_ids,
        notes="same custom encoding mode used by tiny-LM BPB probe",
    )


def _count_sentencepiece(
    *,
    mode: str,
    split_name: str,
    lines: list[str],
    byte_count: int,
    model_path: Path,
) -> AccountingRow:
    encoded = encode_sentencepiece_split(model_path, lines, byte_count, split_name)
    import sentencepiece as spm  # type: ignore[import-not-found]

    processor = spm.SentencePieceProcessor()
    processor.Load(str(model_path))
    return AccountingRow(
        mode=mode,
        split=split_name,
        lines=encoded.lines,
        bytes=encoded.bytes,
        tokens=encoded.tokens,
        vocab_size=int(processor.GetPieceSize()),
        notes=f"SentencePiece model: {model_path.as_posix()}",
    )


def audit_token_accounting(
    *,
    split_dir: Path,
    sp_model: Path | None,
    custom_vocab_size: int,
    max_lines: int | None,
) -> list[AccountingRow]:
    raw_splits = load_split_texts(split_dir)
    splits = {
        name: _limited_lines(split.lines, max_lines)
        for name, split in raw_splits.items()
    }
    split_bytes = {
        name: sum(len(line.encode("utf-8")) for line in lines)
        for name, lines in splits.items()
    }

    print(
        f"Loaded split_dir={split_dir} max_lines={max_lines or 'all'} "
        f"train_lines={len(splits['train'])}",
        flush=True,
    )
    print("Building custom lossless train-only vocabulary...", flush=True)
    custom_vocab = build_custom_vocab(splits["train"], max_vocab_size=custom_vocab_size)

    rows: list[AccountingRow] = []
    for split_name in ("train", "valid", "test"):
        print(f"Counting split={split_name}", flush=True)
        lines = splits[split_name]
        byte_count = split_bytes[split_name]
        rows.append(
            _count_custom_mode(
                mode="custom_standard_no_whitespace",
                split_name=split_name,
                lines=lines,
                byte_count=byte_count,
                preserve_whitespace=False,
            )
        )
        rows.append(
            _count_custom_mode(
                mode="custom_lossless_open_vocab",
                split_name=split_name,
                lines=lines,
                byte_count=byte_count,
                preserve_whitespace=True,
            )
        )
        rows.append(
            _count_custom_lossless_fallback(
                split_name=split_name,
                lines=lines,
                byte_count=byte_count,
                vocab=custom_vocab,
                max_vocab_size=custom_vocab_size,
            )
        )
        if sp_model is not None:
            rows.append(
                _count_sentencepiece(
                    mode=sp_model.stem,
                    split_name=split_name,
                    lines=lines,
                    byte_count=byte_count,
                    model_path=sp_model,
                )
            )
    return rows


def _fmt(value: float | int | None, digits: int = 6) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.{digits}f}"
    return str(value)


def format_report(
    *,
    split_dir: Path,
    sp_model: Path | None,
    custom_vocab_size: int,
    max_lines: int | None,
    rows: list[AccountingRow],
) -> str:
    lines = [
        "# v1.8 Token Accounting Audit",
        "",
        f"Split dir: `{split_dir.as_posix()}`",
        f"SentencePiece model: `{sp_model.as_posix() if sp_model else 'not used'}`",
        f"Custom vocab cap: `{custom_vocab_size}`",
        f"Max lines per split: `{max_lines if max_lines is not None else 'all'}`",
        "",
        "This audit explains tokenizer accounting differences before using the",
        "tiny-LM BPB smoke as evidence. It deliberately compares multiple custom",
        "encoding modes on the same raw split.",
        "",
        "## Summary",
        "",
        "| Mode | Split | Lines | Bytes | Tokens | Tokens/byte | Bytes/token | Vocab | Unique source tokens | Whitespace source tokens | Fallback source tokens | Fallback byte ids | Fallback source rate | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.mode} | {row.split} | {row.lines} | {row.bytes} | {row.tokens} | "
            f"{row.tokens_per_byte:.6f} | {row.bytes_per_token:.6f} | "
            f"{_fmt(row.vocab_size)} | {_fmt(row.unique_source_tokens)} | "
            f"{row.whitespace_source_tokens} | {row.fallback_source_tokens} | "
            f"{row.fallback_byte_ids} | {row.fallback_source_rate:.6f} | {row.notes} |"
        )

    lines.extend(
        [
            "",
            "## How To Read This",
            "",
            "- `custom_standard_no_whitespace` matches the older intrinsic/fertility-style custom view.",
            "- `custom_lossless_open_vocab` adds whitespace-preserving serialization pressure.",
            "- `custom_lossless_64000_byte_fallback` is the tiny-LM custom mode and is the row that should be compared to BPB runs.",
            "- If the old custom tokens/byte is near SP but the lossless/fallback row is much larger, the apparent contradiction is an encoding-mode change, not a BPB discovery.",
            "- BPB claims should use the lossless mode because generation needs `decode(encode(x)) == x`.",
            "- If `--max-lines` is used for a smoke test, fallback rates may be exaggerated because the temporary custom vocabulary is built from a tiny train subset.",
            "",
            "## Decision Rule",
            "",
            "Do not treat the v1.8 iso-byte smoke as a strong morphology data-efficiency claim until this audit and an iso-compute/learning-curve control are recorded.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit v1.8 tokenizer token accounting modes.")
    parser.add_argument(
        "--split-dir",
        default="artifacts/private/v1_8_local_lm_probe/celik_tr_primary_multilingual_mix_lm_probe_pilot_20k/filtered_split",
    )
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_bpe_64000_train_only.model",
        help="SentencePiece model to include. Use an empty string to skip.",
    )
    parser.add_argument("--custom-vocab-size", type=int, default=64000)
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--out", default="artifacts/v1_8_token_accounting_audit.md")
    args = parser.parse_args(argv)

    split_dir = Path(args.split_dir)
    sp_model = Path(args.sp_model) if args.sp_model else None
    if sp_model is not None and not sp_model.exists():
        raise FileNotFoundError(sp_model)
    if args.max_lines is not None and args.max_lines <= 0:
        raise ValueError("--max-lines must be positive")

    rows = audit_token_accounting(
        split_dir=split_dir,
        sp_model=sp_model,
        custom_vocab_size=args.custom_vocab_size,
        max_lines=args.max_lines,
    )
    report = format_report(
        split_dir=split_dir,
        sp_model=sp_model,
        custom_vocab_size=args.custom_vocab_size,
        max_lines=args.max_lines,
        rows=rows,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
