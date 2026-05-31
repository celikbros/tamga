from __future__ import annotations

from dataclasses import dataclass
import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.compare_real_tokenizers import (  # noqa: E402
    RealBaselineSpec,
    format_markdown,
    format_report,
    run_report,
)
from scripts.evaluate_tokenizer import load_cases  # noqa: E402


@dataclass(frozen=True)
class BaselineDataset:
    name: str
    path: Path
    markdown_out: Path


@dataclass(frozen=True)
class BaselineMatrixConfig:
    path: Path
    allow_download: bool
    datasets: list[BaselineDataset]
    baselines: list[dict[str, Any]]


def _strip_comment(line: str) -> str:
    in_quote = False
    escaped = False
    chars: list[str] = []
    for char in line:
        if char == "\\" and in_quote and not escaped:
            escaped = True
            chars.append(char)
            continue
        if char == '"' and not escaped:
            in_quote = not in_quote
        if char == "#" and not in_quote:
            break
        chars.append(char)
        escaped = False
    return "".join(chars).strip()


def _parse_simple_value(raw: str) -> Any:
    value = raw.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _parse_simple_toml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {"settings": {}, "datasets": [], "baselines": []}
    current: dict[str, Any] | None = None

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line)
        if not line:
            continue

        if line == "[settings]":
            current = data["settings"]
            continue
        if line == "[[datasets]]":
            current = {}
            data["datasets"].append(current)
            continue
        if line == "[[baselines]]":
            current = {}
            data["baselines"].append(current)
            continue

        if current is None or "=" not in line:
            raise ValueError(f"unsupported TOML line {line_no}: {raw_line}")

        key, value = line.split("=", 1)
        current[key.strip()] = _parse_simple_value(value)

    return data


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return _parse_simple_toml(path.read_text(encoding="utf-8"))

    with path.open("rb") as handle:
        return tomllib.load(handle)


def _string_field(item: dict[str, Any], field: str, *, context: str) -> str:
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} requires string field {field!r}")
    return value


def load_baseline_config(path: str | Path) -> BaselineMatrixConfig:
    config_path = Path(path)
    raw = _load_toml(config_path)
    settings = raw.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("[settings] must be a table")

    datasets: list[BaselineDataset] = []
    for item in raw.get("datasets", []):
        if not isinstance(item, dict):
            raise ValueError("[[datasets]] entries must be tables")
        name = _string_field(item, "name", context="dataset")
        dataset_path = Path(_string_field(item, "path", context=f"dataset {name}"))
        markdown_out = Path(
            item.get("markdown_out", f"artifacts/v1_7_baseline_matrix_{name}.md")
        )
        datasets.append(
            BaselineDataset(
                name=name,
                path=dataset_path,
                markdown_out=markdown_out,
            )
        )

    baselines = raw.get("baselines", [])
    if not isinstance(baselines, list):
        raise ValueError("[[baselines]] entries must be an array")

    return BaselineMatrixConfig(
        path=config_path,
        allow_download=bool(settings.get("allow_download", False)),
        datasets=datasets,
        baselines=[baseline for baseline in baselines if isinstance(baseline, dict)],
    )


def build_specs_from_config(config: BaselineMatrixConfig) -> list[RealBaselineSpec]:
    specs: list[RealBaselineSpec] = []
    valid_kinds = {
        "custom",
        "unicode_char",
        "toy_bpe",
        "hf",
        "sentencepiece",
        "tokenizers_json",
    }

    for item in config.baselines:
        if item.get("enabled", True) is False:
            continue

        name = _string_field(item, "name", context="baseline")
        kind = _string_field(item, "kind", context=f"baseline {name}")
        if kind not in valid_kinds:
            raise ValueError(f"unknown baseline kind for {name}: {kind}")

        value = ""
        if kind in {"toy_bpe", "sentencepiece", "tokenizers_json"}:
            value = _string_field(item, "path", context=f"baseline {name}")
        elif kind == "hf":
            value = _string_field(item, "model", context=f"baseline {name}")

        specs.append(RealBaselineSpec(name=name, kind=kind, value=value))

    return specs


def _matrix_markdown(
    dataset: BaselineDataset,
    config: BaselineMatrixConfig,
    summary_markdown: str,
) -> str:
    body_lines = summary_markdown.splitlines()
    if body_lines and body_lines[0].startswith("# "):
        body_lines = body_lines[2:]

    lines = [
        f"# v1.7 Baseline Matrix: {dataset.name}",
        "",
        f"Dataset: `{dataset.path.as_posix()}`",
        f"Config: `{config.path.as_posix()}`",
        "",
        "This visible-set report is for baseline tracking only. It must not be",
        "used as hidden-eval evidence or as a downstream LLM-quality claim.",
        "",
    ]
    lines.extend(body_lines)
    return "\n".join(lines).rstrip() + "\n"


def run_matrix(
    config: BaselineMatrixConfig,
    *,
    dataset_names: set[str] | None = None,
    allow_download: bool | None = None,
) -> list[Path]:
    if dataset_names is not None:
        known = {dataset.name for dataset in config.datasets}
        unknown = dataset_names - known
        if unknown:
            raise ValueError(f"unknown dataset filter(s): {', '.join(sorted(unknown))}")

    specs = build_specs_from_config(config)
    if not specs:
        raise ValueError("no enabled baselines in config")

    local_files_only = not (
        config.allow_download if allow_download is None else allow_download
    )
    written: list[Path] = []

    for dataset in config.datasets:
        if dataset_names is not None and dataset.name not in dataset_names:
            continue

        cases = load_cases(dataset.path)
        summary_rows, category_table = run_report(
            cases,
            specs,
            local_files_only=local_files_only,
        )
        print(f"DATASET {dataset.name}")
        print(format_report(summary_rows, category_table))
        print("")

        dataset.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        dataset.markdown_out.write_text(
            _matrix_markdown(
                dataset,
                config,
                format_markdown(summary_rows, category_table),
            ),
            encoding="utf-8",
        )
        written.append(dataset.markdown_out)
        print(f"wrote_markdown: {dataset.markdown_out}")

    return written


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Run the v1.7 visible baseline matrix from a TOML config.",
    )
    parser.add_argument("config", help="Baseline matrix TOML config path.")
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Run only a named dataset from the config. Can be repeated.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="Allow Hugging Face tokenizers to download missing local models.",
    )
    args = parser.parse_args(argv)

    config = load_baseline_config(args.config)
    run_matrix(
        config,
        dataset_names=set(args.dataset) if args.dataset else None,
        allow_download=args.allow_download or config.allow_download,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
