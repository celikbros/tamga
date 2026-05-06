from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.evaluate_tokenizer import EvalCase, load_cases  # noqa: E402
from tr_tokenizer import TurkishTokenizer  # noqa: E402
from tr_tokenizer.baseline_bpe import encode_bpe, load_bpe  # noqa: E402
from tr_tokenizer.pretok import TURKISH_LETTERS  # noqa: E402

_WORD_RE = re.compile(rf"[0-9{TURKISH_LETTERS}_]+")
_WATCHLIST = {
    "Arabalarımızdakilerdenmişsiniz.",
    "OpenAIlaştırılamayanlardanmış.",
    "Geliyom musun?",
    "Rengini beğendim.",
    "Türkiye'den İstanbul'a gittim.",
}


@dataclass(frozen=True)
class BoundaryScore:
    precision: float
    recall: float
    f1: float
    correct: int
    predicted: int
    gold: int


@dataclass(frozen=True)
class CompareResult:
    category: str
    text: str
    expected: list[str]
    custom_tokens: list[str]
    bpe_tokens: list[str]
    custom_boundary: BoundaryScore
    bpe_boundary: BoundaryScore

    @property
    def custom_exact_match(self) -> bool:
        return self.expected == self.custom_tokens


def format_tokens(tokens: list[str]) -> str:
    return json.dumps(tokens, ensure_ascii=False, separators=(",", ":"))


def token_boundaries(tokens: list[str]) -> set[int]:
    text = ""
    boundaries: set[int] = set()

    for token in tokens:
        if not token:
            continue

        if token.startswith("▁"):
            if text:
                text += " "
            text += token[1:]
        elif token.startswith("+"):
            text += token[1:]
        else:
            text += token

        boundaries.add(len(text))

    boundaries.discard(len(text))
    return boundaries


def boundary_score(predicted_tokens: list[str], gold_tokens: list[str]) -> BoundaryScore:
    predicted = token_boundaries(predicted_tokens)
    gold = token_boundaries(gold_tokens)
    correct = len(predicted & gold)
    precision = correct / len(predicted) if predicted else (1.0 if not gold else 0.0)
    recall = correct / len(gold) if gold else (1.0 if not predicted else 0.0)
    denominator = precision + recall
    f1 = 0.0 if denominator == 0 else 2 * precision * recall / denominator
    return BoundaryScore(
        precision=precision,
        recall=recall,
        f1=f1,
        correct=correct,
        predicted=len(predicted),
        gold=len(gold),
    )


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text))


def compare_cases(cases: list[EvalCase], bpe_model: dict) -> list[CompareResult]:
    tokenizer = TurkishTokenizer()
    results: list[CompareResult] = []

    for case in cases:
        custom_tokens = tokenizer.encode(case.text)
        bpe_tokens = encode_bpe(case.text, bpe_model)
        results.append(
            CompareResult(
                category=case.category,
                text=case.text,
                expected=case.expected,
                custom_tokens=custom_tokens,
                bpe_tokens=bpe_tokens,
                custom_boundary=boundary_score(custom_tokens, case.expected),
                bpe_boundary=boundary_score(bpe_tokens, case.expected),
            )
        )

    return results


def _micro_boundary(results: list[CompareResult], which: str) -> BoundaryScore:
    correct = 0
    predicted = 0
    gold = 0

    for result in results:
        score = result.custom_boundary if which == "custom" else result.bpe_boundary
        correct += score.correct
        predicted += score.predicted
        gold += score.gold

    precision = correct / predicted if predicted else (1.0 if gold == 0 else 0.0)
    recall = correct / gold if gold else (1.0 if predicted == 0 else 0.0)
    denominator = precision + recall
    f1 = 0.0 if denominator == 0 else 2 * precision * recall / denominator
    return BoundaryScore(precision, recall, f1, correct, predicted, gold)


def _avg_token_count(results: list[CompareResult], which: str) -> float:
    if not results:
        return 0.0
    if which == "custom":
        return sum(len(result.custom_tokens) for result in results) / len(results)
    return sum(len(result.bpe_tokens) for result in results) / len(results)


def _avg_tokens_per_word(results: list[CompareResult], which: str) -> float:
    word_count = sum(count_words(result.text) for result in results)
    if word_count == 0:
        return 0.0
    if which == "custom":
        token_count = sum(len(result.custom_tokens) for result in results)
    else:
        token_count = sum(len(result.bpe_tokens) for result in results)
    return token_count / word_count


def _by_category(results: list[CompareResult]) -> dict[str, list[CompareResult]]:
    grouped: dict[str, list[CompareResult]] = {}
    for result in results:
        grouped.setdefault(result.category, []).append(result)
    return dict(sorted(grouped.items()))


def print_comparison(results: list[CompareResult]) -> None:
    print("EXAMPLES")
    for result in results:
        print(f"category: {result.category}")
        print(f"text:     {result.text}")
        print(f"gold:     {format_tokens(result.expected)}")
        print(f"custom:   {format_tokens(result.custom_tokens)}")
        print(f"bpe:      {format_tokens(result.bpe_tokens)}")
        print(
            f"counts:   custom={len(result.custom_tokens)} "
            f"bpe={len(result.bpe_tokens)}"
        )
        print()

    custom_boundary = _micro_boundary(results, "custom")
    bpe_boundary = _micro_boundary(results, "bpe")
    custom_exact = sum(result.custom_exact_match for result in results)
    total = len(results)

    print("SUMMARY")
    print(f"examples:                  {total}")
    print(f"custom avg tokens/example: { _avg_token_count(results, 'custom'):.4f}")
    print(f"bpe avg tokens/example:    { _avg_token_count(results, 'bpe'):.4f}")
    print(f"custom avg tokens/word:    { _avg_tokens_per_word(results, 'custom'):.4f}")
    print(f"bpe avg tokens/word:       { _avg_tokens_per_word(results, 'bpe'):.4f}")
    print(f"custom exact match:        {custom_exact}/{total}")
    print(f"custom boundary f1:        {custom_boundary.f1:.4f}")
    print(f"bpe boundary f1:           {bpe_boundary.f1:.4f}")

    print()
    print("CATEGORY SUMMARY")
    for category, category_results in _by_category(results).items():
        custom_score = _micro_boundary(category_results, "custom")
        bpe_score = _micro_boundary(category_results, "bpe")
        print(
            f"{category}: "
            f"custom_f1={custom_score.f1:.4f} "
            f"bpe_f1={bpe_score.f1:.4f} "
            f"custom_avg_tokens={_avg_token_count(category_results, 'custom'):.4f} "
            f"bpe_avg_tokens={_avg_token_count(category_results, 'bpe'):.4f}"
        )

    worst = sorted(results, key=lambda result: (result.bpe_boundary.f1, result.text))[:10]
    print()
    print("WORST BPE EXAMPLES")
    for result in worst:
        _print_worst_result(result)

    missing_watchlist = [
        result for result in results if result.text in _WATCHLIST and result not in worst
    ]
    if missing_watchlist:
        print()
        print("WATCHLIST EXAMPLES")
        for result in sorted(missing_watchlist, key=lambda item: item.text):
            _print_worst_result(result)


def _print_worst_result(result: CompareResult) -> None:
    print(f"category: {result.category}")
    print(f"text:     {result.text}")
    print(f"bpe_f1:   {result.bpe_boundary.f1:.4f}")
    print(f"gold:     {format_tokens(result.expected)}")
    print(f"custom:   {format_tokens(result.custom_tokens)}")
    print(f"bpe:      {format_tokens(result.bpe_tokens)}")
    print()


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Compare TR-MorphTokenizer with a toy BPE baseline.",
    )
    parser.add_argument("gold_tsv")
    parser.add_argument("bpe_model")
    args = parser.parse_args(argv)

    cases = load_cases(args.gold_tsv)
    model = load_bpe(args.bpe_model)
    print_comparison(compare_cases(cases, model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
