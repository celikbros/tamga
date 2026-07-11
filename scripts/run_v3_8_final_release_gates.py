from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys


# Consumer (LLM-team) environment root. The historical literal is kept as the
# fallback so old runbooks stay reproducible; set GARDASH_ROOT when the
# consumer environment lives elsewhere.
GARDASH_ROOT = os.environ.get("GARDASH_ROOT", "C:/CELIK-GARDASH")
DEFAULT_BASE_DIR = Path(GARDASH_ROOT)
DEFAULT_SNAPSHOT_DIR = Path("tokenizer_v3_0_repo_snapshot")
DEFAULT_TOKENIZER_NAME = "sp64k_final_protected_passthrough_sidecar_controls128"


@dataclass(frozen=True)
class GateCommand:
    name: str
    argv: list[str]
    report_path: Path


@dataclass
class GateResult:
    name: str
    report_path: Path
    command: list[str]
    status: str = "planned"
    exit_code: int | None = None
    log_path: Path | None = None


@dataclass(frozen=True)
class ReleaseGatePlan:
    base_dir: Path
    snapshot_dir: Path
    corpus_text: Path
    tokenizer_config: Path
    sidecar_config: Path
    tokenizer_name: str
    tokenized_out_dir: Path
    report_dir: Path
    max_lines: int
    smoke_max_lines: int
    tokenization_max_lines: int
    workers: int
    chunk_lines: int
    progress: int
    batch_size: int
    seq_len: int
    execute: bool
    continue_on_fail: bool

    @property
    def snapshot_root(self) -> Path:
        return self.snapshot_dir if self.snapshot_dir.is_absolute() else self.base_dir / self.snapshot_dir

    @property
    def scripts_dir(self) -> Path:
        return self.snapshot_root / "scripts"


def path_text(path: Path) -> str:
    return str(path)


def read_sp_model_path(tokenizer_config: Path) -> Path:
    if not tokenizer_config.exists():
        return DEFAULT_BASE_DIR / "models" / "tokenizer_v3_8" / "sp_unigram_64000_final.model"
    raw = json.loads(tokenizer_config.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"tokenizer config must be a JSON object: {tokenizer_config}")
    model = raw.get("model", {})
    if not isinstance(model, dict):
        raise ValueError(f"tokenizer config model field must be an object: {tokenizer_config}")
    return Path(str(model.get("sp_model_path", "")))


def maybe_max_lines_args(value: int) -> list[str]:
    return ["--max-lines", str(value)] if value > 0 else []


def build_gate_commands(plan: ReleaseGatePlan) -> list[GateCommand]:
    python = sys.executable
    report_dir = plan.report_dir
    private_dir = report_dir / "private"
    tokenized_manifest = plan.tokenized_out_dir / "manifest.json"
    sp_model = read_sp_model_path(plan.tokenizer_config)

    return [
        GateCommand(
            name="config_validation",
            report_path=report_dir / "config_validation.md",
            argv=[
                python,
                path_text(plan.scripts_dir / "validate_v3_1_tokenizer_config.py"),
                "--config",
                path_text(plan.tokenizer_config),
                "--report-out",
                path_text(report_dir / "config_validation.md"),
            ],
        ),
        GateCommand(
            name="route_density",
            report_path=report_dir / "route_density.md",
            argv=[
                python,
                path_text(plan.scripts_dir / "audit_v2_1_sidecar_route_density.py"),
                "--input",
                path_text(plan.corpus_text),
                "--sp-model",
                path_text(sp_model),
                *maybe_max_lines_args(plan.max_lines),
                "--progress",
                str(plan.progress),
                "--with-token-pressure",
                "--report-out",
                path_text(report_dir / "route_density.md"),
            ],
        ),
        GateCommand(
            name="fertility",
            report_path=report_dir / "fertility.md",
            argv=[
                python,
                path_text(plan.scripts_dir / "report_v3_1_gardash_fertility.py"),
                "--config",
                path_text(plan.sidecar_config),
                "--tokenizer",
                plan.tokenizer_name,
                "--input",
                path_text(plan.corpus_text),
                *maybe_max_lines_args(plan.max_lines),
                "--progress",
                str(plan.progress),
                "--report-out",
                path_text(report_dir / "fertility.md"),
                "--json-out",
                path_text(report_dir / "fertility.json"),
            ],
        ),
        GateCommand(
            name="handoff_smoke",
            report_path=report_dir / "handoff_smoke.md",
            argv=[
                python,
                path_text(plan.scripts_dir / "audit_v2_2_llm_handoff_smoke.py"),
                "--config",
                path_text(plan.sidecar_config),
                "--tokenizer",
                plan.tokenizer_name,
                "--input",
                path_text(plan.corpus_text),
                *maybe_max_lines_args(plan.smoke_max_lines),
                "--progress",
                str(plan.progress),
                "--batch-size",
                str(plan.batch_size),
                "--seq-len",
                str(plan.seq_len),
                "--sidecar-out",
                path_text(private_dir / "handoff_smoke.sidecar.jsonl"),
                "--failures-out",
                path_text(private_dir / "handoff_smoke.failures.jsonl"),
                "--report-out",
                path_text(report_dir / "handoff_smoke.md"),
            ],
        ),
        GateCommand(
            name="tokenize_corpus",
            report_path=report_dir / "tokenize_corpus.md",
            argv=[
                python,
                path_text(plan.scripts_dir / "tokenize_corpus.py"),
                "--config",
                path_text(plan.sidecar_config),
                "--tokenizer",
                plan.tokenizer_name,
                "--input",
                path_text(plan.corpus_text),
                "--out-dir",
                path_text(plan.tokenized_out_dir),
                "--report-out",
                path_text(report_dir / "tokenize_corpus.md"),
                "--max-lines",
                str(plan.tokenization_max_lines),
                "--workers",
                str(plan.workers),
                "--chunk-lines",
                str(plan.chunk_lines),
                "--progress",
                str(plan.progress),
            ],
        ),
        GateCommand(
            name="tokenized_package",
            report_path=report_dir / "tokenized_package_gates" / "gate_summary.md",
            argv=[
                python,
                path_text(plan.scripts_dir / "run_v3_8_tokenized_package_gates.py"),
                "--manifest",
                path_text(tokenized_manifest),
                "--config",
                path_text(plan.tokenizer_config),
                "--base-dir",
                path_text(plan.base_dir),
                "--report-dir",
                path_text(report_dir / "tokenized_package_gates"),
                "--batch-size",
                str(plan.batch_size),
                "--seq-len",
                str(plan.seq_len),
            ],
        ),
    ]


def powershell_command(argv: list[str]) -> str:
    escaped = []
    for item in argv:
        if any(char.isspace() for char in item) or "\\" in item or ":" in item:
            escaped.append(f'"{item}"')
        else:
            escaped.append(item)
    if len(escaped) <= 1:
        return " ".join(escaped)
    lines = [escaped[0] + " `"]
    for index, item in enumerate(escaped[1:], start=1):
        suffix = " `" if index < len(escaped) - 1 else ""
        lines.append(f"  {item}{suffix}")
    return "\n".join(lines)


def execute_commands(plan: ReleaseGatePlan, commands: list[GateCommand]) -> list[GateResult]:
    results: list[GateResult] = []
    log_dir = plan.report_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    for command in commands:
        log_path = log_dir / f"{command.name}.log"
        completed = subprocess.run(
            command.argv,
            cwd=plan.base_dir,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_path.write_text(completed.stdout, encoding="utf-8", newline="\n")
        status = "PASS" if completed.returncode == 0 else "FAIL"
        results.append(
            GateResult(
                name=command.name,
                report_path=command.report_path,
                command=command.argv,
                status=status,
                exit_code=completed.returncode,
                log_path=log_path,
            )
        )
        if completed.returncode != 0 and not plan.continue_on_fail:
            break
    executed = {result.name for result in results}
    for command in commands:
        if command.name not in executed:
            results.append(
                GateResult(
                    name=command.name,
                    report_path=command.report_path,
                    command=command.argv,
                    status="SKIPPED",
                    exit_code=None,
                    log_path=None,
                )
            )
    return results


def planned_results(commands: list[GateCommand]) -> list[GateResult]:
    return [
        GateResult(name=command.name, report_path=command.report_path, command=command.argv)
        for command in commands
    ]


def format_report(plan: ReleaseGatePlan, results: list[GateResult]) -> str:
    status = "PASS" if plan.execute and all(result.status == "PASS" for result in results) else "PLANNED"
    if plan.execute and any(result.status == "FAIL" for result in results):
        status = "FAIL"
    lines = [
        "# v3.8 Final Tokenizer Release Gate Runner",
        "",
        f"Status: `{status}`",
        f"Execute: `{plan.execute}`",
        "",
        "## Inputs",
        "",
        f"- Base dir: `{plan.base_dir}`",
        f"- Snapshot root: `{plan.snapshot_root}`",
        f"- Corpus text: `{plan.corpus_text}`",
        f"- Tokenizer config: `{plan.tokenizer_config}`",
        f"- Sidecar config: `{plan.sidecar_config}`",
        f"- Tokenizer name: `{plan.tokenizer_name}`",
        f"- Tokenized output dir: `{plan.tokenized_out_dir}`",
        "",
        "## Gates",
        "",
        "| Gate | Status | Exit code | Report | Log |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for result in results:
        exit_code = "" if result.exit_code is None else str(result.exit_code)
        log_path = str(result.log_path) if result.log_path else ""
        lines.append(
            f"| `{result.name}` | `{result.status}` | {exit_code} | "
            f"`{result.report_path}` | `{log_path}` |"
        )

    lines.extend(["", "## Commands", ""])
    for result in results:
        lines.extend(
            [
                f"### {result.name}",
                "",
                "```powershell",
                powershell_command(result.command),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Notes",
            "",
            "- Default mode is dry-run planning. Use `--execute` only after final SP retrain is complete.",
            "- The canary-like wrapper check is `handoff_smoke`; it uses the sidecar tokenizer path, unlike the old SentencePiece-only canary helper.",
            "- Full-corpus tokenization is intentionally part of this runner because package gates require the generated `manifest.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def run_plan(plan: ReleaseGatePlan) -> tuple[list[GateResult], Path]:
    commands = build_gate_commands(plan)
    plan.report_dir.mkdir(parents=True, exist_ok=True)
    results = execute_commands(plan, commands) if plan.execute else planned_results(commands)
    summary_path = plan.report_dir / "release_gate_summary.md"
    summary_path.write_text(format_report(plan, results), encoding="utf-8", newline="\n")
    return results, summary_path


def parse_args(argv: list[str] | None = None) -> ReleaseGatePlan:
    parser = argparse.ArgumentParser(
        description="Plan or run the v3.8 final tokenizer release gate sequence."
    )
    parser.add_argument("--base-dir", default=str(DEFAULT_BASE_DIR))
    parser.add_argument("--snapshot-dir", default=str(DEFAULT_SNAPSHOT_DIR))
    parser.add_argument(
        "--corpus-text",
        default=f"{GARDASH_ROOT}/datasets/pretraining_final/final_corpus_text.txt",
    )
    parser.add_argument(
        "--tokenizer-config",
        default=f"{GARDASH_ROOT}/configs/tokenizer_v3_0/tokenizer_config.json",
    )
    parser.add_argument(
        "--sidecar-config",
        default=f"{GARDASH_ROOT}/configs/tokenizer_v3_0/v3_8_final_sidecar_sp64k.toml",
    )
    parser.add_argument("--tokenizer-name", default=DEFAULT_TOKENIZER_NAME)
    parser.add_argument(
        "--tokenized-out-dir",
        default=f"{GARDASH_ROOT}/datasets/tokenizer_v3_8_final_full",
    )
    parser.add_argument(
        "--report-dir",
        default=f"{GARDASH_ROOT}/artifacts/tokenizer_v3_0/v3_8_final_release_gates",
    )
    parser.add_argument("--max-lines", type=int, default=100000)
    parser.add_argument("--smoke-max-lines", type=int, default=5000)
    parser.add_argument("--tokenization-max-lines", type=int, default=0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--chunk-lines", type=int, default=256)
    parser.add_argument("--progress", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--seq-len", type=int, default=128)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--continue-on-fail", action="store_true")
    args = parser.parse_args(argv)
    if args.max_lines < 0 or args.smoke_max_lines < 0 or args.tokenization_max_lines < 0:
        raise ValueError("line limits must be non-negative")
    if args.workers <= 0 or args.chunk_lines <= 0 or args.batch_size <= 0 or args.seq_len <= 0:
        raise ValueError("workers, chunk-lines, batch-size, and seq-len must be positive")
    return ReleaseGatePlan(
        base_dir=Path(args.base_dir),
        snapshot_dir=Path(args.snapshot_dir),
        corpus_text=Path(args.corpus_text),
        tokenizer_config=Path(args.tokenizer_config),
        sidecar_config=Path(args.sidecar_config),
        tokenizer_name=str(args.tokenizer_name),
        tokenized_out_dir=Path(args.tokenized_out_dir),
        report_dir=Path(args.report_dir),
        max_lines=int(args.max_lines),
        smoke_max_lines=int(args.smoke_max_lines),
        tokenization_max_lines=int(args.tokenization_max_lines),
        workers=int(args.workers),
        chunk_lines=int(args.chunk_lines),
        progress=int(args.progress),
        batch_size=int(args.batch_size),
        seq_len=int(args.seq_len),
        execute=bool(args.execute),
        continue_on_fail=bool(args.continue_on_fail),
    )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    plan = parse_args(argv)
    results, summary_path = run_plan(plan)
    print(summary_path.read_text(encoding="utf-8"))
    print(f"wrote_summary: {summary_path}")
    if plan.execute and any(result.status == "FAIL" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
