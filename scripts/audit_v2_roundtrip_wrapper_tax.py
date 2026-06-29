from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.audit_v2_boundary_roundtrip import (  # noqa: E402
    decode_mixed_ids,
    encode_line,
    first_diff_index,
    load_split_lines,
)
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    BoundaryBiasedVocab,
    TokenizerConfig,
    _processor_piece_size,
    load_probe_config,
)
from tr_tokenizer import TurkishTokenizer  # noqa: E402


PUNCT_CATEGORIES = {"Pc", "Pd", "Pe", "Pf", "Pi", "Po", "Ps"}
APOSTROPHES = {"'", "\u2019", "\u2018", "\u02bc"}


@dataclass
class TokenizerRuntime:
    config: TokenizerConfig
    processor: Any
    selected_pieces: list[str]
    boundary_vocab: BoundaryBiasedVocab | None


@dataclass
class RoundtripSummary:
    tokenizer: str
    lines: int = 0
    exact: int = 0
    failures: int = 0
    tokens: int = 0
    raw_bytes: int = 0
    decoded_bytes: int = 0
    classes: Counter[str] = field(default_factory=Counter)

    @property
    def exact_rate(self) -> float:
        return self.exact / self.lines if self.lines else 0.0

    @property
    def tokens_per_byte(self) -> float:
        return self.tokens / self.raw_bytes if self.raw_bytes else 0.0


@dataclass
class WrapperTaxSummary:
    name: str
    lines: int = 0
    official_tokens: int = 0
    candidate_tokens: int = 0
    candidate_shorter: int = 0
    candidate_longer: int = 0
    candidate_equal: int = 0
    line_tags: Counter[str] = field(default_factory=Counter)

    @property
    def avg_official(self) -> float:
        return self.official_tokens / self.lines if self.lines else 0.0

    @property
    def avg_candidate(self) -> float:
        return self.candidate_tokens / self.lines if self.lines else 0.0

    @property
    def avg_delta(self) -> float:
        return self.avg_candidate - self.avg_official


def char_kind(char: str | None) -> str:
    if char is None:
        return "missing"
    if char.isspace():
        return "whitespace"
    if char in APOSTROPHES:
        return "apostrophe"
    category = unicodedata.category(char)
    if category in PUNCT_CATEGORIES:
        return "punctuation"
    if category.startswith("M"):
        return "combining"
    if char.isdigit():
        return "digit"
    return "other"


def window_has(text: str, index: int | None, chars: set[str], radius: int = 6) -> bool:
    if index is None:
        return False
    start = max(0, index - radius)
    end = min(len(text), index + radius + 1)
    return any(char in chars for char in text[start:end])


def count_punct(text: str) -> int:
    return sum(1 for char in text if unicodedata.category(char) in PUNCT_CATEGORIES)


def classify_roundtrip(raw: str, decoded: str) -> str:
    diff = first_diff_index(raw, decoded)
    raw_char = raw[diff] if diff is not None and diff < len(raw) else None
    decoded_char = decoded[diff] if diff is not None and diff < len(decoded) else None
    labels = {
        f"first_raw_{char_kind(raw_char)}",
        f"first_decoded_{char_kind(decoded_char)}",
    }
    if len(raw) != len(decoded):
        labels.add("length_delta")
    if raw.count(" ") != decoded.count(" ") or raw.count("\t") != decoded.count("\t"):
        labels.add("whitespace_count_delta")
    if sum(raw.count(item) for item in APOSTROPHES) != sum(
        decoded.count(item) for item in APOSTROPHES
    ):
        labels.add("apostrophe_count_delta")
    if count_punct(raw) != count_punct(decoded):
        labels.add("punctuation_count_delta")
    if window_has(raw, diff, APOSTROPHES) or window_has(decoded, diff, APOSTROPHES):
        labels.add("near_apostrophe")
    if raw.replace(" ", "") == decoded.replace(" ", "") and raw != decoded:
        labels.add("space_only_difference")
    return ",".join(sorted(labels))


def line_has_protected(text: str, tokenizer: TurkishTokenizer) -> bool:
    return any(piece.kind.startswith("protected:") for piece in analyze_line(text, tokenizer))


def line_tags(text: str) -> list[str]:
    tags: list[str] = []
    if any(char in APOSTROPHES for char in text):
        tags.append("apostrophe")
    if any(char.isspace() for char in text):
        tags.append("whitespace")
    if any(unicodedata.category(char) in PUNCT_CATEGORIES for char in text):
        tags.append("punctuation")
    if any(char.isdigit() for char in text):
        tags.append("digit")
    if "  " in text or "\t" in text:
        tags.append("whitespace_run")
    return tags or ["plain"]


def load_runtime(config: TokenizerConfig) -> TokenizerRuntime:
    if config.path is None:
        raise ValueError(f"tokenizer {config.name} requires model path")
    processor = load_sp_processor(config.path)
    selected = (
        selected_piece_strings(config.selected_pieces)
        if config.selected_pieces is not None
        else []
    )
    boundary_vocab = (
        BoundaryBiasedVocab.from_vocab_file(config.vocab_path)
        if config.vocab_path is not None
        else None
    )
    return TokenizerRuntime(
        config=config,
        processor=processor,
        selected_pieces=selected,
        boundary_vocab=boundary_vocab,
    )


def encode_runtime(text: str, runtime: TokenizerRuntime) -> list[int]:
    return encode_line(
        text,
        config=runtime.config,
        processor=runtime.processor,
        selected_pieces=runtime.selected_pieces,
        boundary_vocab=runtime.boundary_vocab,
    )


def decode_runtime(ids: list[int], runtime: TokenizerRuntime) -> str:
    if runtime.config.kind == "sentencepiece":
        if hasattr(runtime.processor, "DecodeIds"):
            return str(runtime.processor.DecodeIds(ids))
        return str(runtime.processor.decode(ids))
    return decode_mixed_ids(
        ids,
        processor=runtime.processor,
        selected_pieces=runtime.selected_pieces,
        protected_piece_offset=_processor_piece_size(runtime.processor),
    )


def audit(
    *,
    lines: list[str],
    runtimes: list[TokenizerRuntime],
    official_runtime: TokenizerRuntime,
    max_lines: int | None,
    sample_limit: int,
    progress: int,
) -> tuple[list[RoundtripSummary], list[WrapperTaxSummary], list[dict[str, Any]]]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    limit = len(lines) if max_lines is None else min(max_lines, len(lines))
    roundtrip_rows = [RoundtripSummary(runtime.config.name) for runtime in runtimes]
    wrapper_rows = [
        WrapperTaxSummary(runtime.config.name)
        for runtime in runtimes
        if runtime.config.name != official_runtime.config.name
    ]
    private_samples: list[dict[str, Any]] = []

    for line_index, raw in enumerate(lines[:limit], start=1):
        has_protected = line_has_protected(raw, tokenizer)
        official_ids = encode_runtime(raw, official_runtime)

        for runtime, summary in zip(runtimes, roundtrip_rows, strict=True):
            ids = encode_runtime(raw, runtime)
            decoded = decode_runtime(ids, runtime)
            summary.lines += 1
            summary.tokens += len(ids)
            summary.raw_bytes += len(raw.encode("utf-8"))
            summary.decoded_bytes += len(decoded.encode("utf-8"))
            if decoded == raw:
                summary.exact += 1
            else:
                summary.failures += 1
                failure_class = classify_roundtrip(raw, decoded)
                summary.classes[failure_class] += 1
                if len(private_samples) < sample_limit:
                    diff = first_diff_index(raw, decoded)
                    private_samples.append(
                        {
                            "kind": "roundtrip_failure",
                            "tokenizer": runtime.config.name,
                            "line_number": line_index,
                            "class": failure_class,
                            "first_diff": diff,
                            "raw": raw,
                            "decoded": decoded,
                            "raw_context": raw[max(0, (diff or 0) - 40) : (diff or 0) + 40],
                            "decoded_context": decoded[
                                max(0, (diff or 0) - 40) : (diff or 0) + 40
                            ],
                        }
                    )

        if not has_protected:
            for runtime, tax in zip(
                [item for item in runtimes if item.config.name != official_runtime.config.name],
                wrapper_rows,
                strict=True,
            ):
                candidate_ids = encode_runtime(raw, runtime)
                tax.lines += 1
                tax.official_tokens += len(official_ids)
                tax.candidate_tokens += len(candidate_ids)
                delta = len(candidate_ids) - len(official_ids)
                if delta > 0:
                    tax.candidate_longer += 1
                elif delta < 0:
                    tax.candidate_shorter += 1
                else:
                    tax.candidate_equal += 1
                for tag in line_tags(raw):
                    tax.line_tags[tag] += delta

        if progress > 0 and line_index % progress == 0:
            print(f"audited {line_index:,} lines", flush=True)

    return roundtrip_rows, wrapper_rows, private_samples


def format_report(
    *,
    config_path: Path,
    split: str,
    max_lines: int | None,
    roundtrip_rows: list[RoundtripSummary],
    wrapper_rows: list[WrapperTaxSummary],
    private_out: Path,
) -> str:
    lines = [
        "# v2.0 Roundtrip And Wrapper Tax Audit",
        "",
        f"Config: `{config_path.as_posix()}`",
        f"Split: `{split}`",
        f"Max lines: `{max_lines if max_lines is not None else 'all'}`",
        "",
        "This audit is designed after the lambda-0 advisor review. It blocks",
        "longer BPB work until exact roundtrip and clean-line wrapper tax are",
        "understood.",
        "",
        "## Roundtrip Summary",
        "",
        "| Tokenizer | Lines | Exact | Failures | Exact rate | Tokens/raw byte | Raw bytes | Decoded bytes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in roundtrip_rows:
        lines.append(
            f"| {row.tokenizer} | {row.lines} | {row.exact} | {row.failures} | "
            f"{row.exact_rate:.6f} | {row.tokens_per_byte:.6f} | "
            f"{row.raw_bytes} | {row.decoded_bytes} |"
        )

    lines.extend(["", "## Roundtrip Failure Classes", ""])
    for row in roundtrip_rows:
        lines.extend([f"### {row.tokenizer}", ""])
        if not row.classes:
            lines.append("No failures.")
            lines.append("")
            continue
        lines.extend(["| Class | Count |", "| --- | ---: |"])
        for label, count in row.classes.most_common(12):
            lines.append(f"| `{label}` | {count} |")
        lines.append("")

    lines.extend(
        [
            "## Clean-Line Wrapper Tax",
            "",
            "Only lines without protected routes are included. Positive delta means",
            "the candidate uses more tokens than official SP on clean text.",
            "",
            "| Candidate | Lines | Avg official SP tokens | Avg candidate tokens | Avg delta | Candidate shorter | Candidate longer | Candidate equal |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in wrapper_rows:
        lines.append(
            f"| {row.name} | {row.lines} | {row.avg_official:.4f} | "
            f"{row.avg_candidate:.4f} | {row.avg_delta:.4f} | "
            f"{row.candidate_shorter} | {row.candidate_longer} | {row.candidate_equal} |"
        )

    lines.extend(["", "## Wrapper Tax By Line Tag", ""])
    for row in wrapper_rows:
        lines.extend([f"### {row.name}", "", "| Tag | Net token delta |", "| --- | ---: |"])
        for tag, delta in row.line_tags.most_common():
            lines.append(f"| `{tag}` | {delta} |")
        lines.append("")

    lines.extend(
        [
            "## Private Samples",
            "",
            f"Private raw/decoded samples: `{private_out.as_posix()}`",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Classify v2.0 roundtrip failures and clean-line wrapper tax."
    )
    parser.add_argument("config")
    parser.add_argument("--split", default="valid", choices=("train", "valid", "test"))
    parser.add_argument("--tokenizer", action="append", default=[])
    parser.add_argument("--official-tokenizer", default="sp_unigram_64000_train_only")
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--sample-limit", type=int, default=50)
    parser.add_argument("--progress", type=int, default=0)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_roundtrip_wrapper_tax_audit.md",
    )
    parser.add_argument(
        "--private-out",
        default="artifacts/private/v2_0_roundtrip_wrapper_tax_audit.samples.jsonl",
    )
    args = parser.parse_args(argv)

    probe = load_probe_config(args.config)
    by_name = {item.name: item for item in probe.tokenizers}
    if args.official_tokenizer not in by_name:
        raise ValueError(f"unknown official tokenizer: {args.official_tokenizer}")

    selected_names = args.tokenizer or [
        args.official_tokenizer,
        "finite_protected_sp64_numeric_sp_floor",
        "boundary_biased_lambda0_numeric_sp",
        "boundary_biased_lambda4_numeric_sp",
    ]
    unknown = set(selected_names) - set(by_name)
    if unknown:
        raise ValueError(f"unknown tokenizer name(s): {', '.join(sorted(unknown))}")

    runtimes = [load_runtime(by_name[name]) for name in selected_names]
    official_runtime = load_runtime(by_name[args.official_tokenizer])
    lines = load_split_lines(probe.split_dir, args.split)
    roundtrip_rows, wrapper_rows, private_samples = audit(
        lines=lines,
        runtimes=runtimes,
        official_runtime=official_runtime,
        max_lines=args.max_lines,
        sample_limit=args.sample_limit,
        progress=args.progress,
    )

    private_out = Path(args.private_out)
    private_out.parent.mkdir(parents=True, exist_ok=True)
    with private_out.open("w", encoding="utf-8") as handle:
        for sample in private_samples:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")

    report = format_report(
        config_path=Path(args.config),
        split=args.split,
        max_lines=args.max_lines,
        roundtrip_rows=roundtrip_rows,
        wrapper_rows=wrapper_rows,
        private_out=private_out,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    print(f"wrote_private: {private_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
