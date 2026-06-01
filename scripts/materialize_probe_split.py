from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.prepare_downstream_probe import (  # noqa: E402
    ProbeConfig,
    SplitSamples,
    _format_bytes,
    load_corpus_samples,
    load_probe_config,
    split_samples,
)


def write_split_files(
    config: ProbeConfig,
    splits: list[SplitSamples],
) -> dict[str, Path]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    manifest_rows: list[dict[str, int | str]] = []

    for split in splits:
        split_path = config.output_dir / f"{split.name}.txt"
        index_path = config.output_dir / f"{split.name}.manifest.jsonl"
        with (
            split_path.open("w", encoding="utf-8", newline="\n") as text_out,
            index_path.open("w", encoding="utf-8", newline="\n") as index_out,
        ):
            for local_index, sample in enumerate(split.samples, start=1):
                text_out.write(sample.text + "\n")
                row = {
                    "split": split.name,
                    "split_index": local_index,
                    "source_line_index": sample.index,
                    "byte_len": sample.byte_len,
                    "char_len": sample.char_len,
                    "word_count": sample.word_count,
                }
                index_out.write(json.dumps(row, ensure_ascii=False) + "\n")
                manifest_rows.append(row)
        written[split.name] = split_path
        written[f"{split.name}_manifest"] = index_path

    manifest_path = config.output_dir / "split_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "config": config.path.as_posix(),
                "corpus_path": config.corpus_path.as_posix(),
                "seed": config.seed,
                "max_lines": config.max_lines,
                "split_parts": {
                    "train": config.train_parts,
                    "valid": config.valid_parts,
                    "test": config.test_parts,
                },
                "splits": {
                    split.name: {
                        "path": written[split.name].as_posix(),
                        "manifest": written[f"{split.name}_manifest"].as_posix(),
                        "lines": split.line_count,
                        "bytes": split.byte_count,
                        "chars": split.char_count,
                        "words": split.word_count,
                    }
                    for split in splits
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    written["manifest"] = manifest_path
    return written


def format_split_report(
    config: ProbeConfig,
    splits: list[SplitSamples],
    written: dict[str, Path],
) -> str:
    lines = [
        "# v1.8 Local LM Probe Split Materialization",
        "",
        f"Config: `{config.path.as_posix()}`",
        f"Corpus: `{config.corpus_path.as_posix()}`",
        f"Seed: `{config.seed}`",
        f"Split parts: `{config.train_parts}:{config.valid_parts}:{config.test_parts}`",
        f"Output dir: `{config.output_dir.as_posix()}`",
        "",
        "This report records the raw train/valid/test split for v1.8 fairness",
        "work. Raw split files are private artifacts and must not be committed.",
        "",
        "## Split Summary",
        "",
        "| Split | Lines | Bytes | Chars | Words | Text path | Manifest path |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for split in splits:
        lines.append(
            f"| {split.name} | {split.line_count} | {_format_bytes(split.byte_count)} | "
            f"{split.char_count} | {split.word_count} | "
            f"`{written[split.name].as_posix()}` | "
            f"`{written[f'{split.name}_manifest'].as_posix()}` |"
        )

    lines.extend(
        [
            "",
            "## Next Use",
            "",
            "Train-only SentencePiece baselines must use only:",
            "",
            f"`{written['train'].as_posix()}`",
            "",
            "Validation/test text files must not be used for SP vocabulary training.",
        ]
    )
    return "\n".join(lines) + "\n"


def materialize_probe_split(config: ProbeConfig) -> tuple[list[SplitSamples], dict[str, Path]]:
    samples = load_corpus_samples(config.corpus_path, max_lines=config.max_lines)
    splits = split_samples(config, samples)
    written = write_split_files(config, splits)
    return splits, written


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Materialize deterministic raw train/valid/test splits for LM probes.",
    )
    parser.add_argument("config")
    args = parser.parse_args(argv)

    config = load_probe_config(args.config)
    splits, written = materialize_probe_split(config)
    report = format_split_report(config, splits, written)
    config.report_out.parent.mkdir(parents=True, exist_ok=True)
    config.report_out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {config.report_out}")
    print(f"wrote_split_dir: {config.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
