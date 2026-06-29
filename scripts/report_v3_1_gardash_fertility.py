from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    TokenizerConfig,
    _processor_piece_size,
    _processor_encode_ids_lossless_or_byte_fallback,
    encode_finite_protected_soft_marker_line_ids,
    encode_protected_surface_ids,
    load_probe_config,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


DEFAULT_SENTENCES = [
    "Türkiye'nin başkenti Ankara'dır.",
    "Mercimek çorbası Türk mutfağının vazgeçilmezidir.",
    "görüşebileceklerimizdenmisiniz",
    "güneşli",
    "The quick brown fox jumps over the lazy dog.",
]

WORD_RE = re.compile(r"\S+")


@dataclass(frozen=True)
class EncodedLine:
    text: str
    words: int
    tokens: int
    bytes: int
    fallback_tokens: int
    pieces: list[str]

    @property
    def tokens_per_word(self) -> float:
        return self.tokens / self.words if self.words else 0.0

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.bytes if self.bytes else 0.0

    @property
    def fallback_rate(self) -> float:
        return self.fallback_tokens / self.tokens if self.tokens else 0.0


@dataclass(frozen=True)
class CorpusSummary:
    lines: int
    words: int
    tokens: int
    bytes: int
    fallback_tokens: int
    max_tokens_per_word: float
    worst_lines: list[EncodedLine]

    @property
    def tokens_per_word(self) -> float:
        return self.tokens / self.words if self.words else 0.0

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.bytes if self.bytes else 0.0

    @property
    def fallback_rate(self) -> float:
        return self.fallback_tokens / self.tokens if self.tokens else 0.0


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def find_tokenizer(config_path: Path, tokenizer_name: str) -> TokenizerConfig:
    config = load_probe_config(config_path)
    for tokenizer in config.tokenizers:
        if tokenizer.name == tokenizer_name:
            return tokenizer
    available = ", ".join(tokenizer.name for tokenizer in config.tokenizers)
    raise ValueError(f"tokenizer {tokenizer_name!r} not found. Available: {available}")


def piece_strings(ids: list[int], *, processor: Any, piece_size: int) -> list[str]:
    pieces: list[str] = []
    for token_id in ids:
        if 0 <= token_id < piece_size:
            pieces.append(str(processor.IdToPiece(int(token_id))))
        elif piece_size <= token_id < piece_size + 256:
            pieces.append(f"<0x{token_id - piece_size:02X}>")
        else:
            pieces.append(f"<id:{token_id}>")
    return pieces


class GardashEncoder:
    def __init__(self, tokenizer: TokenizerConfig) -> None:
        if tokenizer.path is None:
            raise ValueError(f"tokenizer {tokenizer.name!r} has no model path")
        self.tokenizer = tokenizer
        self.processor = load_sp_processor(tokenizer.path)
        self.selected_pieces = (
            selected_piece_strings(tokenizer.selected_pieces)
            if tokenizer.selected_pieces
            else []
        )
        self.piece_size = _processor_piece_size(self.processor)
        self.byte_offset = self.piece_size + len(self.selected_pieces)
        self.piece_to_id = {
            piece: self.piece_size + index
            for index, piece in enumerate(self.selected_pieces)
        }
        self.teacher = TurkishTokenizer(preserve_whitespace=True)
        self.passthrough_routes = set(tokenizer.sp_passthrough_routes)
        if tokenizer.kind == "finite_protected_marker_stripped_numeric_sp":
            self.passthrough_routes.add("numeric_like")

    def encode_line(self, text: str) -> EncodedLine:
        ids, fallback_tokens = encode_finite_protected_soft_marker_line_ids(
            text,
            processor=self.processor,
            selected_pieces=self.selected_pieces,
            protected_piece_offset=self.piece_size,
            insert_soft_markers=self.tokenizer.kind == "finite_protected_soft_marker",
            numeric_sp_passthrough=(
                self.tokenizer.kind == "finite_protected_marker_stripped_numeric_sp"
            ),
            sp_passthrough_routes=self.tokenizer.sp_passthrough_routes,
            isolate_sp_passthrough_routes=self.tokenizer.isolate_sp_passthrough_routes,
            byte_fallback_crossing_pieces=self.tokenizer.byte_fallback_crossing_pieces,
            pre_split_sp_passthrough_routes=self.tokenizer.pre_split_sp_passthrough_routes,
        )
        return EncodedLine(
            text=text,
            words=count_words(text),
            tokens=len(ids),
            bytes=len(text.encode("utf-8")),
            fallback_tokens=fallback_tokens,
            pieces=piece_strings(ids, processor=self.processor, piece_size=self.piece_size),
        )

    def encode_line_counts(self, text: str) -> EncodedLine:
        if (
            self.tokenizer.kind != "finite_protected_marker_stripped_numeric_sp"
            or self.tokenizer.isolate_sp_passthrough_routes
            or self.tokenizer.byte_fallback_crossing_pieces
            or self.tokenizer.pre_split_sp_passthrough_routes
        ):
            return self.encode_line(text)

        tokens = 0
        fallback_tokens = 0
        segment = ""

        def flush_segment() -> None:
            nonlocal segment, tokens, fallback_tokens
            if not segment:
                return
            ids, byte_tokens = _processor_encode_ids_lossless_or_byte_fallback(
                self.processor,
                segment,
                byte_offset=self.byte_offset,
            )
            tokens += len(ids)
            fallback_tokens += byte_tokens
            segment = ""

        for piece in analyze_line(text, self.teacher):
            if piece.kind.startswith("protected:"):
                route = piece.kind.removeprefix("protected:")
                if route in self.passthrough_routes:
                    segment += piece.surface
                    continue
                flush_segment()
                ids, byte_tokens = encode_protected_surface_ids(
                    piece.surface,
                    selected_pieces=self.selected_pieces,
                    piece_to_id=self.piece_to_id,
                    byte_offset=self.byte_offset,
                )
                tokens += len(ids)
                fallback_tokens += byte_tokens
                continue
            segment += piece.surface

        flush_segment()
        return EncodedLine(
            text=text,
            words=count_words(text),
            tokens=tokens,
            bytes=len(text.encode("utf-8")),
            fallback_tokens=fallback_tokens,
            pieces=[],
        )


def summarize_corpus(
    *,
    encoder: GardashEncoder,
    input_path: Path,
    max_lines: int | None,
    worst_limit: int,
    progress: int,
) -> CorpusSummary:
    lines = 0
    words = 0
    tokens = 0
    raw_bytes = 0
    fallback_tokens = 0
    max_tokens_per_word = 0.0
    worst: list[EncodedLine] = []

    with input_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            if max_lines is not None and lines >= max_lines:
                break
            text = raw_line.rstrip("\n")
            if not text:
                continue
            row = encoder.encode_line_counts(text)
            lines += 1
            words += row.words
            tokens += row.tokens
            raw_bytes += row.bytes
            fallback_tokens += row.fallback_tokens
            max_tokens_per_word = max(max_tokens_per_word, row.tokens_per_word)
            if len(worst) < worst_limit:
                worst.append(row)
                worst.sort(key=lambda item: item.tokens_per_word)
            elif row.tokens_per_word > worst[0].tokens_per_word:
                worst[0] = row
                worst.sort(key=lambda item: item.tokens_per_word)
            if progress > 0 and lines % progress == 0:
                print(
                    f"measured {lines:,} lines tokens={tokens:,} "
                    f"avg_tokens/word={tokens / words if words else 0.0:.4f}",
                    flush=True,
                )

    return CorpusSummary(
        lines=lines,
        words=words,
        tokens=tokens,
        bytes=raw_bytes,
        fallback_tokens=fallback_tokens,
        max_tokens_per_word=max_tokens_per_word,
        worst_lines=sorted(worst, key=lambda item: item.tokens_per_word, reverse=True),
    )


def markdown_report(
    *,
    config_path: Path,
    tokenizer_name: str,
    input_path: Path,
    sample_rows: list[EncodedLine],
    corpus: CorpusSummary,
) -> str:
    lines = [
        "# v3.1 Gardaş Fertility Benchmark",
        "",
        f"Config: `{config_path.as_posix()}`",
        f"Tokenizer: `{tokenizer_name}`",
        f"Corpus: `{input_path.as_posix()}`",
        "",
        "This report measures the actual v3 handoff encode path, including the",
        "finite protected passthrough sidecar configuration and UTF-8 byte fallback.",
        "EOS is not counted in fertility.",
        "",
        "## Requested Sentences",
        "",
        "| Text | Words | Tokens | Tokens/word | Tokens/byte | Fallback tokens | Pieces |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in sample_rows:
        pieces = " ".join(f"`{piece}`" for piece in row.pieces)
        lines.append(
            f"| {row.text} | {row.words} | {row.tokens} | "
            f"{row.tokens_per_word:.4f} | {row.tokens_per_byte:.6f} | "
            f"{row.fallback_tokens} | {pieces} |"
        )

    lines.extend(
        [
            "",
            "## Corpus Summary",
            "",
            "| Lines | Words | Bytes | Tokens | Tokens/word | Tokens/byte | Fallback tokens | Fallback rate | Max line tokens/word |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| {corpus.lines} | {corpus.words} | {corpus.bytes} | {corpus.tokens} | "
            f"{corpus.tokens_per_word:.6f} | {corpus.tokens_per_byte:.6f} | "
            f"{corpus.fallback_tokens} | {corpus.fallback_rate:.6f} | "
            f"{corpus.max_tokens_per_word:.6f} |",
            "",
            "## Highest-Fertility Lines",
            "",
            "| Tokens/word | Tokens | Words | Text prefix |",
            "| ---: | ---: | ---: | --- |",
        ]
    )
    for row in corpus.worst_lines:
        prefix = row.text[:220].replace("|", "\\|")
        lines.append(
            f"| {row.tokens_per_word:.6f} | {row.tokens} | {row.words} | {prefix} |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            "- Corpus-level fertility should be read together with BPB and fallback rate.",
            "- Very high line fertility is mostly caused by corpus formatting issues such as glued text without spaces.",
            "- Morphological stress words can still have high fertility even when corpus-level average is acceptable.",
            "- This report does not decide the final vocab size; it is an input to the 32K/48K/64K ablation.",
            "",
        ]
    )
    return "\n".join(lines)


def json_summary(
    *,
    tokenizer_name: str,
    sample_rows: list[EncodedLine],
    corpus: CorpusSummary,
) -> dict[str, object]:
    return {
        "tokenizer": tokenizer_name,
        "samples": [
            {
                "text": row.text,
                "words": row.words,
                "tokens": row.tokens,
                "tokens_per_word": row.tokens_per_word,
                "tokens_per_byte": row.tokens_per_byte,
                "fallback_tokens": row.fallback_tokens,
                "pieces": row.pieces,
            }
            for row in sample_rows
        ],
        "corpus": {
            "lines": corpus.lines,
            "words": corpus.words,
            "bytes": corpus.bytes,
            "tokens": corpus.tokens,
            "tokens_per_word": corpus.tokens_per_word,
            "tokens_per_byte": corpus.tokens_per_byte,
            "fallback_tokens": corpus.fallback_tokens,
            "fallback_rate": corpus.fallback_rate,
            "max_tokens_per_word": corpus.max_tokens_per_word,
            "worst_lines": [
                {
                    "text": row.text,
                    "words": row.words,
                    "tokens": row.tokens,
                    "tokens_per_word": row.tokens_per_word,
                }
                for row in corpus.worst_lines
            ],
        },
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Report Gardaş v3.1 tokenizer fertility.")
    parser.add_argument(
        "--config",
        default="C:/CELIK-GARDASH/configs/tokenizer_v3_0/v3_0_gardash_sidecar.toml",
        help="Tokenizer config containing the handoff tokenizer.",
    )
    parser.add_argument(
        "--tokenizer",
        default="sp64_protected_passthrough_sidecar",
        help="Tokenizer name from the config.",
    )
    parser.add_argument(
        "--input",
        default="C:/CELIK-GARDASH/datasets/tokenizer_v3_0/real_mix_60k_sample.txt",
        help="Plain text corpus, one sample per line.",
    )
    parser.add_argument("--max-lines", type=int, default=None)
    parser.add_argument("--progress", type=int, default=5000)
    parser.add_argument("--worst-limit", type=int, default=10)
    parser.add_argument("--sentence", action="append", default=[])
    parser.add_argument("--report-out", default="artifacts/v3_1_gardash_fertility_benchmark.md")
    parser.add_argument("--json-out", default="")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    input_path = Path(args.input)
    tokenizer = find_tokenizer(config_path, args.tokenizer)
    encoder = GardashEncoder(tokenizer)
    sentences = args.sentence or DEFAULT_SENTENCES
    sample_rows = [encoder.encode_line(sentence) for sentence in sentences]
    corpus = summarize_corpus(
        encoder=encoder,
        input_path=input_path,
        max_lines=args.max_lines,
        worst_limit=args.worst_limit,
        progress=args.progress,
    )

    report = markdown_report(
        config_path=config_path,
        tokenizer_name=args.tokenizer,
        input_path=input_path,
        sample_rows=sample_rows,
        corpus=corpus,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"wrote_report: {report_out}")

    if args.json_out:
        json_out = Path(args.json_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(
            json.dumps(
                json_summary(
                    tokenizer_name=args.tokenizer,
                    sample_rows=sample_rows,
                    corpus=corpus,
                ),
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote_json: {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
