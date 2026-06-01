from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import RealBaselineSpec, encode_with_spec  # noqa: E402
from scripts.report_protected_spans import is_span_preserved  # noqa: E402
from scripts.run_sentencepiece_sweep import load_sentencepiece_sweep_config  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.pretok import (  # noqa: E402
    is_file_like_token,
    is_numeric_like_token,
    is_technical_comparator_token,
    is_url_like_token,
    pre_tokenize,
)

UNKNOWN_TOKENS = {"<unk>", "[UNK]", "⁇"}
WORD_JOINERS = {"_", "'", "’", "ʻ", "ʼ", "-"}


@dataclass(frozen=True)
class CanaryCase:
    row: int
    category: str
    text: str

    @property
    def bytes(self) -> int:
        return len(self.text.encode("utf-8"))

    @property
    def words(self) -> int:
        return count_canary_words(self.text)


def count_canary_words(text: str) -> int:
    count = 0
    in_word = False
    for char in text:
        is_word_char = char.isalnum() or char in WORD_JOINERS
        if is_word_char and not in_word:
            count += 1
        in_word = is_word_char
    return count


@dataclass(frozen=True)
class CanaryResult:
    spec: RealBaselineSpec
    case: CanaryCase
    status: str
    reason: str
    tokens: list[str]
    roundtrip_ok: bool
    protected_total: int
    protected_preserved: int

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def tokens_per_word(self) -> float:
        return self.token_count / self.case.words if self.case.words else 0.0

    @property
    def tokens_per_byte(self) -> float:
        return self.token_count / self.case.bytes if self.case.bytes else 0.0

    @property
    def unknown_or_byte_tokens(self) -> int:
        return sum(is_unknown_or_byte_token(token) for token in self.tokens)


@dataclass(frozen=True)
class CanarySummary:
    model_name: str
    status: str
    lines: int
    words: int
    bytes: int
    tokens: int
    avg_tokens_word: float
    tokens_byte: float
    bytes_token: float
    roundtrip_failures: int
    protected_total: int
    protected_broken: int
    unknown_or_byte_tokens: int
    reason: str = ""

    @property
    def protected_break_rate(self) -> float:
        return self.protected_broken / self.protected_total if self.protected_total else 0.0


def load_cases(path: str | Path) -> list[CanaryCase]:
    cases: list[CanaryCase] = []
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        for row, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\n")
            if not line:
                continue
            fields = line.split("\t")
            if len(fields) != 2:
                raise ValueError(f"{source}:{row}: expected category<TAB>text")
            cases.append(CanaryCase(row=row, category=fields[0], text=fields[1]))
    return cases


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
    return token in UNKNOWN_TOKENS or token.startswith("<0x") or "\ufffd" in token


def decode_with_spec(spec: RealBaselineSpec, tokens: list[str]) -> str:
    if spec.kind == "custom":
        tokenizer = TurkishTokenizer(preserve_whitespace=True)
        return tokenizer.decode(tokens)
    if spec.kind == "sentencepiece":
        import sentencepiece as spm  # type: ignore[import-not-found]

        processor = spm.SentencePieceProcessor(model_file=spec.value)
        return str(processor.decode(tokens))
    if spec.kind == "unicode_char":
        return "".join(tokens)
    return ""


def encode_for_canary(spec: RealBaselineSpec, text: str) -> tuple[str, str, list[str], str]:
    if spec.kind == "custom":
        tokenizer = TurkishTokenizer(preserve_whitespace=True)
        return "ok", "", tokenizer.encode(text), tokenizer.decode(tokenizer.encode(text))
    encoding = encode_with_spec(spec, text, local_files_only=True)
    if encoding.status != "ok":
        return encoding.status, encoding.reason, [], ""
    return encoding.status, encoding.reason, encoding.tokens, decode_with_spec(spec, encoding.tokens)


def evaluate(cases: list[CanaryCase], specs: list[RealBaselineSpec]) -> dict[str, list[CanaryResult]]:
    output: dict[str, list[CanaryResult]] = {}
    skipped: dict[str, tuple[str, str]] = {}
    for spec in specs:
        results: list[CanaryResult] = []
        for case in cases:
            if spec.name in skipped:
                status, reason = skipped[spec.name]
                tokens: list[str] = []
                decoded = ""
            else:
                status, reason, tokens, decoded = encode_for_canary(spec, case.text)
                if status != "ok":
                    skipped[spec.name] = (status, reason)

            candidates = protected_candidates(case.text)
            preserved = (
                sum(is_span_preserved(span, tokens) for span in candidates)
                if status == "ok"
                else 0
            )
            results.append(
                CanaryResult(
                    spec=spec,
                    case=case,
                    status=status,
                    reason=reason,
                    tokens=tokens,
                    roundtrip_ok=status == "ok" and decoded == case.text,
                    protected_total=len(candidates),
                    protected_preserved=preserved,
                )
            )
        output[spec.name] = results
    return output


def summarize(results: list[CanaryResult]) -> CanarySummary:
    model_name = results[0].spec.name if results else ""
    status = "ok" if all(result.status == "ok" for result in results) else "skipped"
    reason = next((result.reason for result in results if result.reason), "")
    if status != "ok":
        return CanarySummary(model_name, status, len(results), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, reason)

    lines = len(results)
    words = sum(result.case.words for result in results)
    byte_count = sum(result.case.bytes for result in results)
    tokens = sum(result.token_count for result in results)
    protected_total = sum(result.protected_total for result in results)
    protected_preserved = sum(result.protected_preserved for result in results)
    return CanarySummary(
        model_name=model_name,
        status=status,
        lines=lines,
        words=words,
        bytes=byte_count,
        tokens=tokens,
        avg_tokens_word=tokens / words if words else 0.0,
        tokens_byte=tokens / byte_count if byte_count else 0.0,
        bytes_token=byte_count / tokens if tokens else 0.0,
        roundtrip_failures=sum(not result.roundtrip_ok for result in results),
        protected_total=protected_total,
        protected_broken=protected_total - protected_preserved,
        unknown_or_byte_tokens=sum(result.unknown_or_byte_tokens for result in results),
        reason=reason,
    )


def category_table(results: list[CanaryResult]) -> list[tuple[str, int, float, int]]:
    grouped: dict[str, list[CanaryResult]] = {}
    for result in results:
        grouped.setdefault(result.case.category, []).append(result)

    rows: list[tuple[str, int, float, int]] = []
    for category, category_results in sorted(grouped.items()):
        tokens = sum(result.token_count for result in category_results)
        words = sum(result.case.words for result in category_results)
        failures = sum(not result.roundtrip_ok for result in category_results)
        rows.append((category, len(category_results), tokens / words if words else 0.0, failures))
    return rows


def worst_lines(results: list[CanaryResult], *, limit: int = 5) -> list[CanaryResult]:
    ok_results = [result for result in results if result.status == "ok"]
    return sorted(
        ok_results,
        key=lambda result: (result.tokens_per_word, result.token_count),
        reverse=True,
    )[:limit]


def load_sp_specs(config_path: str | Path, names: set[str]) -> list[RealBaselineSpec]:
    config = load_sentencepiece_sweep_config(config_path)
    specs: list[RealBaselineSpec] = []
    for model in config.models:
        if model.name in names:
            specs.append(RealBaselineSpec(model.name, "sentencepiece", str(model.model_path)))
    return specs


def default_specs(sp_config: str | Path, hybrid_sp_config: str | Path | None) -> list[RealBaselineSpec]:
    specs = [RealBaselineSpec("custom_tr_morph_lossless", "custom")]
    specs.extend(
        load_sp_specs(
            sp_config,
            {
                "sp_bpe_32000_train_only",
                "sp_unigram_32000_train_only",
                "sp_bpe_64000_train_only",
                "sp_unigram_64000_train_only",
            },
        )
    )
    if hybrid_sp_config is not None:
        specs.extend(
            load_sp_specs(
                hybrid_sp_config,
                {
                    "hybrid_morph_pretok_bpe_64000_train_only",
                    "hybrid_morph_pretok_unigram_64000_train_only",
                },
            )
        )
    specs.append(RealBaselineSpec("unicode_char", "unicode_char"))
    return specs


def format_text_report(model_results: dict[str, list[CanaryResult]]) -> str:
    lines = [
        "CANARY DIAGNOSTICS",
        "model_name\tstatus\tlines\twords\tbytes\ttokens\tavg_tokens/word\t"
        "tokens/byte\tbytes/token\troundtrip_failures\tprotected_broken\t"
        "protected_total\tunknown_or_byte_tokens\treason",
    ]
    for results in model_results.values():
        row = summarize(results)
        lines.append(
            f"{row.model_name}\t{row.status}\t{row.lines}\t{row.words}\t{row.bytes}\t"
            f"{row.tokens}\t{row.avg_tokens_word:.4f}\t{row.tokens_byte:.6f}\t"
            f"{row.bytes_token:.4f}\t{row.roundtrip_failures}\t"
            f"{row.protected_broken}\t{row.protected_total}\t"
            f"{row.unknown_or_byte_tokens}\t{row.reason}"
        )
    return "\n".join(lines)


def format_markdown(
    model_results: dict[str, list[CanaryResult]],
    *,
    input_path: str | Path,
) -> str:
    lines = [
        "# v1.8 Canary Diagnostics",
        "",
        f"Input: `{Path(input_path).as_posix()}`",
        "",
        "This is a small public/synthetic diagnostic set. It is not a hidden eval,",
        "not a downstream LM-loss result, and not a final tokenizer selection.",
        "",
        "## Summary",
        "",
        "| Model | Status | Lines | Words | Bytes | Tokens | Avg tokens/word | Tokens/byte | Bytes/token | Roundtrip failures | Protected broken | Unknown/byte tokens | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for results in model_results.values():
        row = summarize(results)
        protected = f"{row.protected_broken}/{row.protected_total}"
        lines.append(
            f"| {row.model_name} | {row.status} | {row.lines} | {row.words} | "
            f"{row.bytes} | {row.tokens} | {row.avg_tokens_word:.4f} | "
            f"{row.tokens_byte:.6f} | {row.bytes_token:.4f} | "
            f"{row.roundtrip_failures} | {protected} | "
            f"{row.unknown_or_byte_tokens} | {row.reason} |"
        )

    lines.extend(["", "## Category Diagnostics", ""])
    for model_name, results in model_results.items():
        lines.extend(
            [
                f"### {model_name}",
                "",
                "| Category | Lines | Avg tokens/word | Roundtrip failures |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for category, count, tokens_word, failures in category_table(results):
            lines.append(f"| {category} | {count} | {tokens_word:.4f} | {failures} |")
        lines.append("")

    lines.extend(["## Highest Fertility Lines", ""])
    for model_name, results in model_results.items():
        lines.extend([f"### {model_name}", ""])
        for result in worst_lines(results):
            lines.append(
                f"- row {result.case.row} `{result.case.category}`: "
                f"{result.tokens_per_word:.4f} tokens/word, "
                f"{result.token_count} tokens - `{result.case.text}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- The custom tokenizer is evaluated in lossless whitespace-preserving mode here.",
            "- Protected candidates are auto-detected URL/file-like/numeric-like/comparator spans.",
            "- Unknown/byte token count is a coarse diagnostic for explicit fallback markers.",
            "- Canary failures should block overconfident claims, not automatically kill the project.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Report v1.8 canary diagnostics.")
    parser.add_argument("--input", default="data/eval/v1_8_canary.tsv")
    parser.add_argument("--sp-config", default="configs/v1_8_train_only_sentencepiece_sweep.toml")
    parser.add_argument("--hybrid-sp-config", default="configs/v1_8_hybrid_sentencepiece_sweep.toml")
    parser.add_argument("--out", default="artifacts/v1_8_canary_diagnostics.md")
    args = parser.parse_args(argv)

    hybrid_config = args.hybrid_sp_config if args.hybrid_sp_config else None
    cases = load_cases(args.input)
    specs = default_specs(args.sp_config, hybrid_config)
    results = evaluate(cases, specs)

    print(format_text_report(results))

    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(format_markdown(results, input_path=args.input), encoding="utf-8")
    print(f"wrote_markdown: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
