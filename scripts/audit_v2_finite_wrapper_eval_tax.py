from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_tokenizers import BoundaryScore, boundary_score, count_words  # noqa: E402
from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    canonicalize_external_tokens,
    encode_with_spec,
)
from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import (  # noqa: E402
    encode_finite_protected_sp64,
    load_sp_processor,
    selected_piece_strings,
)
from scripts.materialize_v2_soft_morph_artifacts import analyze_line  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402


@dataclass(frozen=True)
class EvalTaxRow:
    category: str
    route_tag: str
    feature_tags: tuple[str, ...]
    text: str
    words: int
    bare_tokens: list[str]
    finite_tokens: list[str]
    bare_model_tokens: int
    finite_model_tokens: int
    bare_boundary: BoundaryScore
    finite_boundary: BoundaryScore

    @property
    def model_token_delta(self) -> int:
        return self.finite_model_tokens - self.bare_model_tokens

    @property
    def f1_delta(self) -> float:
        return self.finite_boundary.f1 - self.bare_boundary.f1


@dataclass(frozen=True)
class GroupSummary:
    group: str
    examples: int
    words: int
    bare_f1: float
    finite_f1: float
    avg_bare_tokens_word: float
    avg_finite_tokens_word: float
    avg_model_token_delta: float


def route_tag(text: str) -> str:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    kinds = sorted(
        {
            piece.kind.removeprefix("protected:")
            for piece in analyze_line(text, tokenizer)
            if piece.kind.startswith("protected:")
        }
    )
    return "+".join(kinds) if kinds else "no_protected"


def feature_tags(text: str) -> tuple[str, ...]:
    tokenizer = TurkishTokenizer(preserve_whitespace=True)
    tags: set[str] = set()
    for piece in analyze_line(text, tokenizer):
        if piece.kind.startswith("protected:"):
            tags.add(piece.kind.removeprefix("protected:"))
        elif piece.kind == "apostrophe":
            tags.add("apostrophe")
        elif piece.kind == "suffix" and piece.boundary_before == "hard":
            tags.add("hard_suffix")
        elif piece.kind == "punctuation":
            tags.add("punctuation")
        elif piece.kind == "whitespace":
            tags.add("whitespace")
    return tuple(sorted(tags)) or ("plain",)


def encode_bare_sp(text: str, sp_model: Path) -> tuple[list[str], int]:
    spec = RealBaselineSpec(name="bare_sp", kind="sentencepiece", value=str(sp_model))
    encoding = encode_with_spec(spec, text, local_files_only=True)
    if encoding.status != "ok":
        return [], 0
    return canonicalize_external_tokens(encoding.tokens), len(encoding.tokens)


def evaluate_rows(
    *,
    cases: list[EvalCase],
    processor,
    sp_model: Path,
    selected_pieces: list[str],
    numeric_sp_passthrough: bool,
) -> list[EvalTaxRow]:
    rows: list[EvalTaxRow] = []
    for case in cases:
        bare_tokens, bare_count = encode_bare_sp(case.text, sp_model)
        finite = encode_finite_protected_sp64(
            case.text,
            processor=processor,
            selected_pieces=selected_pieces,
            numeric_sp_passthrough=numeric_sp_passthrough,
        )
        rows.append(
            EvalTaxRow(
                category=case.category,
                route_tag=route_tag(case.text),
                feature_tags=feature_tags(case.text),
                text=case.text,
                words=count_words(case.text),
                bare_tokens=bare_tokens,
                finite_tokens=finite.logical_tokens,
                bare_model_tokens=bare_count,
                finite_model_tokens=finite.model_token_count,
                bare_boundary=boundary_score(bare_tokens, case.expected),
                finite_boundary=boundary_score(finite.logical_tokens, case.expected),
            )
        )
    return rows


def micro_boundary(scores: list[BoundaryScore]) -> float:
    correct = sum(score.correct for score in scores)
    predicted = sum(score.predicted for score in scores)
    gold = sum(score.gold for score in scores)
    precision = correct / predicted if predicted else (1.0 if gold == 0 else 0.0)
    recall = correct / gold if gold else (1.0 if predicted == 0 else 0.0)
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def summarize_group(name: str, rows: list[EvalTaxRow]) -> GroupSummary:
    words = sum(row.words for row in rows)
    bare_tokens = sum(row.bare_model_tokens for row in rows)
    finite_tokens = sum(row.finite_model_tokens for row in rows)
    return GroupSummary(
        group=name,
        examples=len(rows),
        words=words,
        bare_f1=micro_boundary([row.bare_boundary for row in rows]),
        finite_f1=micro_boundary([row.finite_boundary for row in rows]),
        avg_bare_tokens_word=bare_tokens / words if words else 0.0,
        avg_finite_tokens_word=finite_tokens / words if words else 0.0,
        avg_model_token_delta=sum(row.model_token_delta for row in rows) / len(rows)
        if rows
        else 0.0,
    )


def grouped(rows: list[EvalTaxRow], attr: str) -> list[GroupSummary]:
    buckets: dict[str, list[EvalTaxRow]] = {}
    for row in rows:
        buckets.setdefault(getattr(row, attr), []).append(row)
    return [
        summarize_group(name, items)
        for name, items in sorted(buckets.items(), key=lambda item: item[0])
    ]


def grouped_by_feature(rows: list[EvalTaxRow]) -> list[GroupSummary]:
    buckets: dict[str, list[EvalTaxRow]] = {}
    for row in rows:
        for tag in row.feature_tags:
            buckets.setdefault(tag, []).append(row)
    return [
        summarize_group(name, items)
        for name, items in sorted(buckets.items(), key=lambda item: item[0])
    ]


def format_group_table(title: str, summaries: list[GroupSummary]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Group | Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(
            f"| `{row.group}` | {row.examples} | {row.bare_f1:.4f} | "
            f"{row.finite_f1:.4f} | {row.finite_f1 - row.bare_f1:+.4f} | "
            f"{row.avg_bare_tokens_word:.4f} | {row.avg_finite_tokens_word:.4f} | "
            f"{row.avg_model_token_delta:+.4f} |"
        )
    lines.append("")
    return lines


def worst_rows(rows: list[EvalTaxRow], limit: int) -> list[EvalTaxRow]:
    return sorted(rows, key=lambda row: (row.f1_delta, -row.model_token_delta, row.text))[
        :limit
    ]


def format_report(
    *,
    dataset: Path,
    sp_model: Path,
    rows: list[EvalTaxRow],
    numeric_sp_passthrough: bool,
    worst_limit: int,
) -> str:
    overall = summarize_group("overall", rows)
    route_counts = Counter(row.route_tag for row in rows)
    lines = [
        "# v2.0 Finite Wrapper Eval Tax Audit",
        "",
        f"Dataset: `{dataset.as_posix()}`",
        f"SP model: `{sp_model.as_posix()}`",
        f"Numeric protected SP passthrough: `{numeric_sp_passthrough}`",
        "",
        "This report decomposes how much the finite protected wrapper changes",
        "visible eval behavior compared with the bare SP model.",
        "",
        "## Overall",
        "",
        "| Examples | Bare F1 | Finite F1 | F1 delta | Bare tokens/word | Finite tokens/word | Avg token delta/example |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {overall.examples} | {overall.bare_f1:.4f} | {overall.finite_f1:.4f} | "
        f"{overall.finite_f1 - overall.bare_f1:+.4f} | "
        f"{overall.avg_bare_tokens_word:.4f} | {overall.avg_finite_tokens_word:.4f} | "
        f"{overall.avg_model_token_delta:+.4f} |",
        "",
        "## Route Tag Counts",
        "",
        "| Route tag | Examples |",
        "| --- | ---: |",
    ]
    for tag, count in route_counts.most_common():
        lines.append(f"| `{tag}` | {count} |")
    lines.append("")
    lines.extend(format_group_table("By Route Tag", grouped(rows, "route_tag")))
    lines.extend(format_group_table("By Feature Tag", grouped_by_feature(rows)))
    lines.extend(format_group_table("By Eval Category", grouped(rows, "category")))
    lines.extend(
        [
            "## Worst F1 Deltas",
            "",
            "| Category | Route tag | F1 delta | Token delta | Text |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in worst_rows(rows, worst_limit):
        text = row.text.replace("|", "\\|")
        lines.append(
            f"| `{row.category}` | `{row.route_tag}` | {row.f1_delta:+.4f} | "
            f"{row.model_token_delta:+d} | `{text}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If most F1 loss is concentrated in protected route tags, wrapper design",
            "is the bottleneck. If no-protected rows also lose F1, normal text",
            "segmentation is being changed unexpectedly.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Audit finite wrapper eval tax.")
    parser.add_argument("--dataset", default="data/eval/tr_challenge.tsv")
    parser.add_argument(
        "--sp-model",
        default="artifacts/private/v1_8_train_only_sentencepiece/sp_unigram_64000_train_only.model",
    )
    parser.add_argument(
        "--selected-pieces",
        default="artifacts/private/v2_0_protected_aware/protected_piece_vocab.train.tsv",
    )
    parser.add_argument("--numeric-sp-passthrough", action="store_true")
    parser.add_argument("--worst-limit", type=int, default=20)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_finite_wrapper_eval_tax_challenge.md",
    )
    args = parser.parse_args(argv)

    dataset = Path(args.dataset)
    sp_model = Path(args.sp_model)
    processor = load_sp_processor(sp_model)
    selected = selected_piece_strings(Path(args.selected_pieces))
    rows = evaluate_rows(
        cases=load_cases(dataset),
        processor=processor,
        sp_model=sp_model,
        selected_pieces=selected,
        numeric_sp_passthrough=args.numeric_sp_passthrough,
    )
    report = format_report(
        dataset=dataset,
        sp_model=sp_model,
        rows=rows,
        numeric_sp_passthrough=args.numeric_sp_passthrough,
        worst_limit=args.worst_limit,
    )
    report_out = Path(args.report_out)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
