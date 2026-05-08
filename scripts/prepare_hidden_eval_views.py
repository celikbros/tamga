from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


HEADER = [
    "category",
    "text",
    "gold_independent_tokens_json",
    "gold_policy_tokens_json",
    "divergence_note",
]


def _validate_tokens(raw_json: str, *, source: Path, line_number: int) -> list[str]:
    tokens = json.loads(raw_json)
    if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
        raise ValueError(f"{source}:{line_number}: token gold must be a JSON string list")
    return tokens


def load_hidden_rows(path: str | Path) -> list[tuple[str, str, list[str], list[str], str]]:
    source = Path(path)
    rows: list[tuple[str, str, list[str], list[str], str]] = []

    with source.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.rstrip("\n")
            if not line:
                continue

            fields = line.split("\t")
            if line_number == 1 and fields == HEADER:
                continue
            if len(fields) != 5:
                raise ValueError(
                    f"{source}:{line_number}: expected "
                    "category<TAB>text<TAB>gold_independent<TAB>gold_policy<TAB>note"
                )

            category, text, independent_json, policy_json, note = fields
            independent = _validate_tokens(
                independent_json,
                source=source,
                line_number=line_number,
            )
            policy = _validate_tokens(
                policy_json,
                source=source,
                line_number=line_number,
            )
            rows.append((category, text, independent, policy, note))

    return rows


def render_standard_eval(
    rows: list[tuple[str, str, list[str], list[str], str]],
    *,
    which: str,
) -> str:
    if which not in {"independent", "policy"}:
        raise ValueError("which must be 'independent' or 'policy'")

    gold_index = 2 if which == "independent" else 3
    lines: list[str] = []
    for row in rows:
        category = row[0]
        text = row[1]
        tokens = row[gold_index]
        tokens_json = json.dumps(tokens, ensure_ascii=False, separators=(",", ":"))
        lines.append(f"{category}\t{text}\t{tokens_json}")
    return "\n".join(lines) + "\n"


def default_output_paths(input_path: str | Path, out_dir: str | Path | None) -> tuple[Path, Path]:
    source = Path(input_path)
    target_dir = Path(out_dir) if out_dir else source.parent
    stem = source.stem
    if stem.endswith("_hidden_eval"):
        prefix = stem
    else:
        prefix = "tr_hidden_eval"
    return (
        target_dir / f"{prefix}_independent.tsv",
        target_dir / f"{prefix}_policy.tsv",
    )


def write_eval_views(
    input_path: str | Path,
    *,
    out_dir: str | Path | None = None,
) -> tuple[Path, Path]:
    rows = load_hidden_rows(input_path)
    independent_path, policy_path = default_output_paths(input_path, out_dir)
    independent_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    independent_path.write_text(
        render_standard_eval(rows, which="independent"),
        encoding="utf-8",
    )
    policy_path.write_text(
        render_standard_eval(rows, which="policy"),
        encoding="utf-8",
    )
    return independent_path, policy_path


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Create standard eval TSV views from a two-gold hidden eval TSV."
    )
    parser.add_argument("input_tsv")
    parser.add_argument("--out-dir")
    args = parser.parse_args(argv)

    independent_path, policy_path = write_eval_views(
        args.input_tsv,
        out_dir=args.out_dir,
    )
    print(f"wrote_independent: {independent_path}")
    print(f"wrote_policy:      {policy_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
