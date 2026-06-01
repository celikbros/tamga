from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.run_sentencepiece_sweep import load_sentencepiece_sweep_config  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class RoundtripSpec:
    name: str
    kind: str
    value: str = ""


@dataclass(frozen=True)
class RoundtripFailure:
    split: str
    row: int
    source_line_index: int | None
    input_hash: str
    input_bytes: int
    decoded_bytes: int
    token_count: int


@dataclass
class RoundtripSplitResult:
    tokenizer: str
    split: str
    status: str
    lines: int = 0
    failures: int = 0
    bytes: int = 0
    tokens: int = 0
    reason: str = ""
    failure_details: list[RoundtripFailure] = field(default_factory=list)

    @property
    def failure_rate(self) -> float:
        return self.failures / self.lines if self.lines else 0.0

    @property
    def avg_tokens_line(self) -> float:
        return self.tokens / self.lines if self.lines else 0.0


def _sha12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _load_source_line_indexes(manifest_path: Path) -> list[int | None]:
    if not manifest_path.exists():
        return []
    indexes: list[int | None] = []
    with manifest_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                import json

                item = json.loads(raw_line)
            except Exception:
                indexes.append(None)
                continue
            value = item.get("source_line_index")
            indexes.append(value if isinstance(value, int) else None)
    return indexes


def _iter_split_lines(split_dir: Path, split: str):
    path = split_dir / f"{split}.txt"
    indexes = _load_source_line_indexes(split_dir / f"{split}.manifest.jsonl")
    with path.open("r", encoding="utf-8") as handle:
        for row, raw_line in enumerate(handle, start=1):
            text = raw_line.rstrip("\n")
            source_line_index = indexes[row - 1] if row - 1 < len(indexes) else None
            yield row, source_line_index, text


@lru_cache(maxsize=32)
def _load_sentencepiece_processor(model_path: str):
    import sentencepiece as spm  # type: ignore[import-not-found]

    return spm.SentencePieceProcessor(model_file=model_path)


def encode_decode(spec: RoundtripSpec, text: str) -> tuple[list[str], str]:
    if spec.kind == "custom":
        tokenizer = TurkishTokenizer(preserve_whitespace=True)
        tokens = tokenizer.encode(text)
        return tokens, tokenizer.decode(tokens)
    if spec.kind == "sentencepiece":
        processor = _load_sentencepiece_processor(spec.value)
        tokens = list(processor.encode(text, out_type=str))
        return tokens, str(processor.decode(tokens))
    raise ValueError(f"unsupported tokenizer kind: {spec.kind}")


def check_roundtrip(
    split_dir: str | Path,
    specs: list[RoundtripSpec],
    *,
    max_failures: int,
    progress: bool = False,
) -> list[RoundtripSplitResult]:
    root = Path(split_dir)
    results: list[RoundtripSplitResult] = []

    for spec in specs:
        skipped_reason = ""
        if spec.kind == "sentencepiece" and not Path(spec.value).exists():
            skipped_reason = f"missing sentencepiece model: {spec.value}"

        for split in ("train", "valid", "test"):
            if progress:
                print(f"checking_roundtrip tokenizer={spec.name} split={split}", flush=True)
            result = RoundtripSplitResult(
                tokenizer=spec.name,
                split=split,
                status="skipped" if skipped_reason else "ok",
                reason=skipped_reason,
            )
            if skipped_reason:
                results.append(result)
                continue

            for row, source_line_index, text in _iter_split_lines(root, split):
                result.lines += 1
                result.bytes += len(text.encode("utf-8"))
                tokens, decoded = encode_decode(spec, text)
                result.tokens += len(tokens)
                if decoded != text:
                    result.failures += 1
                    if len(result.failure_details) < max_failures:
                        result.failure_details.append(
                            RoundtripFailure(
                                split=split,
                                row=row,
                                source_line_index=source_line_index,
                                input_hash=_sha12(text),
                                input_bytes=len(text.encode("utf-8")),
                                decoded_bytes=len(decoded.encode("utf-8")),
                                token_count=len(tokens),
                            )
                    )
            results.append(result)
            if progress:
                print(
                    f"finished_roundtrip tokenizer={spec.name} split={split} "
                    f"lines={result.lines} failures={result.failures}",
                    flush=True,
                )
    return results


def load_roundtrip_specs(sp_config: str | Path | None) -> list[RoundtripSpec]:
    specs = [RoundtripSpec("custom_tr_morph", "custom")]
    if sp_config is None:
        return specs
    config = load_sentencepiece_sweep_config(sp_config)
    for model in config.models:
        specs.append(
            RoundtripSpec(
                name=model.name,
                kind="sentencepiece",
                value=model.model_path.as_posix(),
            )
        )
    return specs


def format_roundtrip_report(
    results: list[RoundtripSplitResult],
    *,
    split_dir: str | Path,
    sp_config: str | Path | None,
) -> str:
    lines = [
        "# v1.8 Tokenizer Roundtrip Report",
        "",
        f"Split dir: `{Path(split_dir).as_posix()}`",
        f"SentencePiece config: `{Path(sp_config).as_posix() if sp_config else ''}`",
        "",
        "This report checks whether each tokenizer can exactly reconstruct each",
        "input line after encode/decode. It does not include private corpus text.",
        "",
        "## Summary",
        "",
        "| Tokenizer | Split | Status | Lines | Failures | Failure rate | Avg tokens/line | Notes |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.tokenizer} | {result.split} | {result.status} | "
            f"{result.lines} | {result.failures} | {result.failure_rate:.6f} | "
            f"{result.avg_tokens_line:.4f} | {result.reason} |"
        )

    lines.extend(
        [
            "",
            "## Failure Details",
            "",
            "Rows, source line indexes, hashes, and lengths are reported instead of",
            "private text snippets.",
        ]
    )
    grouped = [result for result in results if result.failure_details]
    if not grouped:
        lines.append("")
        lines.append("No roundtrip failures found.")
        return "\n".join(lines) + "\n"

    for result in grouped:
        lines.extend(
            [
                "",
                f"### {result.tokenizer} / {result.split}",
                "",
                "| Row | Source line | Input hash | Input bytes | Decoded bytes | Tokens |",
                "| ---: | ---: | --- | ---: | ---: | ---: |",
            ]
        )
        for failure in result.failure_details:
            source_line = (
                str(failure.source_line_index)
                if failure.source_line_index is not None
                else ""
            )
            lines.append(
                f"| {failure.row} | {source_line} | {failure.input_hash} | "
                f"{failure.input_bytes} | {failure.decoded_bytes} | "
                f"{failure.token_count} |"
            )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Check exact encode/decode roundtrip for v1.8 probe tokenizers.",
    )
    parser.add_argument("--split-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sp-config")
    parser.add_argument("--max-failures", type=int, default=10)
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args(argv)

    specs = load_roundtrip_specs(args.sp_config)
    results = check_roundtrip(
        args.split_dir,
        specs,
        max_failures=args.max_failures,
        progress=args.progress,
    )
    report = format_roundtrip_report(
        results,
        split_dir=args.split_dir,
        sp_config=args.sp_config,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
