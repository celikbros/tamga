from __future__ import annotations

from dataclasses import dataclass
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    build_specs,
    encode_with_spec,
)
from scripts.compare_tokenizers import count_words  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from tr_tokenizer.pretok import (  # noqa: E402
    is_file_like_token,
    is_numeric_like_token,
    is_technical_comparator_token,
    is_url_like_token,
    pre_tokenize,
)

UNKNOWN_TOKENS = {"<unk>", "[UNK]", "⁇"}
BYTE_TOKEN_RE = re.compile(r"^<0x[0-9A-Fa-f]{2}>$")


@dataclass(frozen=True)
class CorpusLine:
    index: int
    text: str


@dataclass(frozen=True)
class FertilityLineResult:
    line: CorpusLine
    model_name: str
    tokens: list[str]
    status: str
    reason: str
    words: int
    protected_candidates: list[str]

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def tokens_per_word(self) -> float:
        return self.token_count / self.words if self.words else 0.0

    @property
    def protected_total(self) -> int:
        return len(self.protected_candidates)

    @property
    def protected_preserved(self) -> int:
        if self.status != "ok":
            return 0
        return sum(
            is_span_preserved(span, self.tokens)
            for span in self.protected_candidates
        )

    @property
    def unknown_or_byte_tokens(self) -> int:
        return sum(is_unknown_or_byte_token(token) for token in self.tokens)


@dataclass(frozen=True)
class FertilitySummary:
    model_name: str
    status: str
    lines: int
    words: int
    tokens: int
    avg_tokens_line: float
    avg_tokens_word: float
    max_tokens_word_line: float
    protected_total: int
    protected_preserved: int
    protected_broken: int
    unknown_or_byte_tokens: int
    reason: str = ""

    @property
    def protected_break_rate(self) -> float:
        if not self.protected_total:
            return 0.0
        return self.protected_broken / self.protected_total

    @property
    def unknown_or_byte_rate(self) -> float:
        if not self.tokens:
            return 0.0
        return self.unknown_or_byte_tokens / self.tokens


def load_corpus_lines(path: str | Path) -> list[CorpusLine]:
    lines: list[CorpusLine] = []
    source = Path(path)
    with source.open("r", encoding="utf-8") as file:
        for index, raw_line in enumerate(file, start=1):
            text = raw_line.strip()
            if not text:
                continue
            lines.append(CorpusLine(index=index, text=text))
    return lines


def protected_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    for token in pre_tokenize(text):
        if (
            is_url_like_token(token)
            or is_file_like_token(token)
            or is_numeric_like_token(token)
            or is_technical_comparator_token(token)
        ) and token not in seen:
            candidates.append(token)
            seen.add(token)
    return candidates


def is_unknown_or_byte_token(token: str) -> bool:
    return (
        token in UNKNOWN_TOKENS
        or BYTE_TOKEN_RE.match(token) is not None
        or "\ufffd" in token
    )


def evaluate_fertility(
    lines: list[CorpusLine],
    specs: list[RealBaselineSpec],
    *,
    local_files_only: bool = True,
) -> dict[str, list[FertilityLineResult]]:
    results: dict[str, list[FertilityLineResult]] = {}
    skipped: dict[str, tuple[str, str]] = {}
    candidates_by_line = {
        line.index: protected_candidates(line.text)
        for line in lines
    }

    for spec in specs:
        model_results: list[FertilityLineResult] = []
        for line in lines:
            if spec.name in skipped:
                status, reason = skipped[spec.name]
                tokens: list[str] = []
            else:
                encoding = encode_with_spec(
                    spec,
                    line.text,
                    local_files_only=local_files_only,
                )
                status = encoding.status
                reason = encoding.reason
                tokens = encoding.tokens
                if status != "ok":
                    skipped[spec.name] = (status, reason)

            model_results.append(
                FertilityLineResult(
                    line=line,
                    model_name=spec.name,
                    tokens=tokens,
                    status=status,
                    reason=reason,
                    words=count_words(line.text),
                    protected_candidates=candidates_by_line[line.index],
                )
            )
        results[spec.name] = model_results

    return results


def summarize_model(results: list[FertilityLineResult]) -> FertilitySummary:
    if not results:
        return FertilitySummary("", "skipped", 0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0, 0)

    model_name = results[0].model_name
    status = "ok" if all(result.status == "ok" for result in results) else "skipped"
    reason = next((result.reason for result in results if result.reason), "")
    if status != "ok":
        return FertilitySummary(
            model_name=model_name,
            status=status,
            lines=len(results),
            words=0,
            tokens=0,
            avg_tokens_line=0.0,
            avg_tokens_word=0.0,
            max_tokens_word_line=0.0,
            protected_total=0,
            protected_preserved=0,
            protected_broken=0,
            unknown_or_byte_tokens=0,
            reason=reason,
        )

    lines = len(results)
    words = sum(result.words for result in results)
    tokens = sum(result.token_count for result in results)
    protected_total = sum(result.protected_total for result in results)
    protected_preserved = sum(result.protected_preserved for result in results)
    protected_broken = protected_total - protected_preserved
    unknown_or_byte_tokens = sum(result.unknown_or_byte_tokens for result in results)
    max_tokens_word_line = max(
        (result.tokens_per_word for result in results),
        default=0.0,
    )

    return FertilitySummary(
        model_name=model_name,
        status=status,
        lines=lines,
        words=words,
        tokens=tokens,
        avg_tokens_line=tokens / lines if lines else 0.0,
        avg_tokens_word=tokens / words if words else 0.0,
        max_tokens_word_line=max_tokens_word_line,
        protected_total=protected_total,
        protected_preserved=protected_preserved,
        protected_broken=protected_broken,
        unknown_or_byte_tokens=unknown_or_byte_tokens,
        reason=reason,
    )


def worst_lines(
    results: list[FertilityLineResult],
    *,
    limit: int = 5,
) -> list[FertilityLineResult]:
    ok_results = [result for result in results if result.status == "ok"]
    return sorted(
        ok_results,
        key=lambda result: (result.tokens_per_word, result.token_count),
        reverse=True,
    )[:limit]


def _ratio(preserved: int, total: int) -> str:
    if total == 0:
        return "n/a"
    return f"{preserved}/{total} ({preserved / total:.4f})"


def format_text_report(model_results: dict[str, list[FertilityLineResult]]) -> str:
    rows = [summarize_model(results) for results in model_results.values()]
    lines = [
        "FERTILITY REPORT",
        "model_name\tstatus\tlines\twords\ttokens\tavg_tokens/line\t"
        "avg_tokens/word\tmax_line_tokens/word\tprotected_preserved\t"
        "protected_break_rate\tunknown_or_byte_tokens\tunknown_or_byte_rate\treason",
    ]
    for row in rows:
        lines.append(
            f"{row.model_name}\t{row.status}\t{row.lines}\t{row.words}\t"
            f"{row.tokens}\t{row.avg_tokens_line:.4f}\t"
            f"{row.avg_tokens_word:.4f}\t{row.max_tokens_word_line:.4f}\t"
            f"{row.protected_preserved}/{row.protected_total}\t"
            f"{row.protected_break_rate:.4f}\t{row.unknown_or_byte_tokens}\t"
            f"{row.unknown_or_byte_rate:.4f}\t{row.reason}"
        )
    return "\n".join(lines)


def format_markdown(model_results: dict[str, list[FertilityLineResult]]) -> str:
    rows = [summarize_model(results) for results in model_results.values()]
    lines = [
        "# Natural Corpus Fertility Report",
        "",
        "Tokenizer behavior is not changed by this report.",
        "",
        "## Summary",
        "",
        "| Model | Status | Lines | Words | Tokens | Avg tokens/line | Avg tokens/word | Max line tokens/word | Protected preserved | Break rate | Unknown/byte tokens | Unknown/byte rate | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.model_name} | {row.status} | {row.lines} | {row.words} | "
            f"{row.tokens} | {row.avg_tokens_line:.4f} | "
            f"{row.avg_tokens_word:.4f} | {row.max_tokens_word_line:.4f} | "
            f"{_ratio(row.protected_preserved, row.protected_total)} | "
            f"{row.protected_break_rate:.4f} | {row.unknown_or_byte_tokens} | "
            f"{row.unknown_or_byte_rate:.4f} | {row.reason} |"
        )

    lines.extend(["", "## Highest Fertility Lines", ""])
    for model_name, results in model_results.items():
        lines.extend([f"### {model_name}", ""])
        worst = worst_lines(results)
        if not worst:
            lines.append("No available lines.")
            lines.append("")
            continue
        for result in worst:
            lines.append(
                f"- line {result.line.index}: {result.tokens_per_word:.4f} "
                f"tokens/word, {result.token_count} tokens - `{result.line.text}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- This is a corpus-level fertility report, not a morphology gold evaluation.",
            "- `data/train/tr_bpe_train.txt` is a small demo corpus and is not a production benchmark.",
            "- Protected candidates are auto-detected URL/file-like/numeric-like spans.",
            "- Unknown/byte tokens are a coarse proxy for explicit fallback markers, not a full coverage proof.",
        ]
    )
    return "\n".join(lines) + "\n"


def default_specs() -> list[RealBaselineSpec]:
    return [
        RealBaselineSpec(name="custom_tr_morph", kind="custom"),
        RealBaselineSpec(name="unicode_char", kind="unicode_char"),
    ]


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Report tokenizer fertility on a plain-text corpus.",
    )
    parser.add_argument("corpus_path", help="Plain text corpus with one line per sample")
    parser.add_argument(
        "--toy-bpe",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Add a trained toy BPE model JSON.",
    )
    parser.add_argument(
        "--hf",
        action="append",
        default=[],
        metavar="NAME=MODEL_ID_OR_PATH",
        help="Add a Hugging Face tokenizer. Defaults to local cache only.",
    )
    parser.add_argument(
        "--sentencepiece",
        action="append",
        default=[],
        metavar="NAME=MODEL_PATH",
        help="Add a SentencePiece model file.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face tokenizers to download missing models.",
    )
    parser.add_argument("--markdown-out", help="Optional Markdown report output path")
    args = parser.parse_args(argv)

    specs = (
        build_specs(args)
        if (args.toy_bpe or args.hf or args.sentencepiece)
        else default_specs()
    )
    model_results = evaluate_fertility(
        load_corpus_lines(args.corpus_path),
        specs,
        local_files_only=not args.allow_download,
    )
    print(format_text_report(model_results))

    if args.markdown_out:
        target = Path(args.markdown_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(format_markdown(model_results), encoding="utf-8")
        print(f"wrote_markdown: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
