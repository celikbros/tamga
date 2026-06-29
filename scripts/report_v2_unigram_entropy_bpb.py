from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_tiny_lm_bpb_probe import (  # noqa: E402
    EncodedSplit,
    TokenizerConfig,
    encode_tokenizer,
    load_probe_config,
    load_split_texts,
)


@dataclass(frozen=True)
class UnigramRow:
    tokenizer: str
    vocab_size: int
    train_tokens_per_byte: float
    test_tokens_per_byte: float
    train_seen_types: int
    test_unseen_tokens: int
    test_unseen_rate: float
    alpha: float
    test_bits_per_token: float
    test_bpb: float
    unsmoothed_known_bits_per_token: float
    unsmoothed_known_coverage: float


def nll_bits_for_split(
    *,
    train: EncodedSplit,
    target: EncodedSplit,
    vocab_size: int,
    alpha: float,
) -> tuple[float, float, int, float, float]:
    counts = Counter(train.ids)
    denominator = len(train.ids) + alpha * vocab_size
    total = 0.0
    unsmoothed_total = 0.0
    known = 0
    unseen = 0
    for token_id in target.ids:
        count = counts.get(token_id, 0)
        probability = (count + alpha) / denominator
        total += -math.log2(probability)
        if count > 0:
            unsmoothed_total += -math.log2(count / len(train.ids))
            known += 1
        else:
            unseen += 1
    bits_per_token = total / len(target.ids) if target.ids else float("nan")
    bpb = total / target.bytes if target.bytes else float("nan")
    known_bits = unsmoothed_total / known if known else float("nan")
    known_coverage = known / len(target.ids) if target.ids else 0.0
    return bits_per_token, bpb, unseen, known_bits, known_coverage


def evaluate_tokenizer(
    tokenizer: TokenizerConfig,
    *,
    config_path: Path,
    alpha: float,
    encode_progress: int,
) -> UnigramRow:
    config = load_probe_config(config_path)
    splits = load_split_texts(config.split_dir)
    encoded = encode_tokenizer(
        tokenizer,
        splits,
        encode_progress=encode_progress,
    )
    if encoded.status != "ok":
        raise RuntimeError(f"{tokenizer.name} failed to encode: {encoded.reason}")
    train = encoded.splits["train"]
    test = encoded.splits["test"]
    bits_per_token, bpb, unseen, known_bits, known_coverage = nll_bits_for_split(
        train=train,
        target=test,
        vocab_size=encoded.vocab_size,
        alpha=alpha,
    )
    return UnigramRow(
        tokenizer=tokenizer.name,
        vocab_size=encoded.vocab_size,
        train_tokens_per_byte=train.tokens_per_byte,
        test_tokens_per_byte=test.tokens_per_byte,
        train_seen_types=len(set(train.ids)),
        test_unseen_tokens=unseen,
        test_unseen_rate=unseen / test.tokens if test.tokens else 0.0,
        alpha=alpha,
        test_bits_per_token=bits_per_token,
        test_bpb=bpb,
        unsmoothed_known_bits_per_token=known_bits,
        unsmoothed_known_coverage=known_coverage,
    )


def format_report(rows: list[UnigramRow]) -> str:
    lines = [
        "# v2.0 Unigram Entropy BPB Decomposition",
        "",
        "This is a zero-training decomposition. It tokenizes train/test exactly",
        "through the configured tokenizer path, estimates a smoothed unigram",
        "distribution from the train token stream, and evaluates test negative",
        "log likelihood normalized by raw test bytes.",
        "",
        "This answers whether the tiny-LM BPB gap is already present in static",
        "token distribution geometry before any contextual modeling.",
        "",
        "## Results",
        "",
        "| Tokenizer | Vocab | Train tokens/byte | Test tokens/byte | Train seen types | Test unseen rate | Alpha | Test bits/token | Test unigram BPB | Known-token bits/token | Known coverage |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.tokenizer} | {row.vocab_size} | "
            f"{row.train_tokens_per_byte:.6f} | {row.test_tokens_per_byte:.6f} | "
            f"{row.train_seen_types} | {row.test_unseen_rate:.6f} | "
            f"{row.alpha:.4g} | {row.test_bits_per_token:.6f} | "
            f"{row.test_bpb:.6f} | {row.unsmoothed_known_bits_per_token:.6f} | "
            f"{row.unsmoothed_known_coverage:.6f} |"
        )
    if rows:
        baseline = rows[0].test_bpb
        lines.extend(
            [
                "",
                "## Delta Versus First Row",
                "",
                "| Tokenizer | Test unigram BPB delta |",
                "| --- | ---: |",
            ]
        )
        for row in rows:
            lines.append(f"| {row.tokenizer} | {row.test_bpb - baseline:+.6f} |")
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If the teacher-distilled row already wins by roughly the same amount in",
            "this table as in tiny-LM BPB, most of the gain is static distributional",
            "geometry. If it does not win here but wins in tiny-LM, the evidence",
            "points more toward contextual/morphological usefulness.",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Report unigram entropy BPB.")
    parser.add_argument("config")
    parser.add_argument(
        "--tokenizer",
        action="append",
        default=[],
        help="Restrict to one or more tokenizer names.",
    )
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--encode-progress", type=int, default=1000)
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_unigram_entropy_bpb.md",
    )
    args = parser.parse_args(argv)

    config = load_probe_config(args.config)
    selected = set(args.tokenizer)
    tokenizers = [
        tokenizer
        for tokenizer in config.tokenizers
        if not selected or tokenizer.name in selected
    ]
    unknown = selected - {tokenizer.name for tokenizer in tokenizers}
    if unknown:
        raise ValueError(f"unknown tokenizer name(s): {', '.join(sorted(unknown))}")

    rows: list[UnigramRow] = []
    for tokenizer in tokenizers:
        print(f"Evaluating unigram entropy tokenizer={tokenizer.name}", flush=True)
        rows.append(
            evaluate_tokenizer(
                tokenizer,
                config_path=Path(args.config),
                alpha=args.alpha,
                encode_progress=args.encode_progress,
            )
        )

    report = format_report(rows)
    out = Path(args.report_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
