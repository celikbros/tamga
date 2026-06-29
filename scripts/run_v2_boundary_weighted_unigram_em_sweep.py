from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_lambdas(value: str) -> list[float]:
    lambdas: list[float] = []
    for raw in value.split(","):
        stripped = raw.strip()
        if not stripped:
            continue
        lambdas.append(float(stripped))
    if not lambdas:
        raise argparse.ArgumentTypeError("at least one lambda is required")
    return lambdas


def lambda_label(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value).replace(".", "p").replace("-", "m")


def command_to_text(command: list[str]) -> str:
    return " ".join(command)


def run_command(command: list[str], *, dry_run: bool) -> None:
    print(command_to_text(command), flush=True)
    if dry_run:
        return
    subprocess.run(command, cwd=ROOT, check=True)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Run a boundary-weighted Unigram/EM lambda sweep."
    )
    parser.add_argument("--lambdas", type=parse_lambdas, default=parse_lambdas("0,1,2,4"))
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--max-lines", type=int, default=2000)
    parser.add_argument("--progress", type=int, default=500)
    parser.add_argument(
        "--private-dir",
        default="artifacts/private/v2_0_boundary_weighted_unigram_em",
    )
    parser.add_argument(
        "--public-prefix",
        default="artifacts/v2_0_boundary_weighted_unigram_em",
    )
    parser.add_argument("--ci-samples", type=int, default=1000)
    parser.add_argument("--dataset", default="data/eval/tr_challenge.tsv")
    parser.add_argument("--skip-ci", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    private_dir = Path(args.private_dir)
    public_prefix = Path(args.public_prefix)
    model_args: list[str] = []

    print("# Boundary-weighted Unigram/EM sweep", flush=True)
    print(
        f"lambdas={','.join(str(value) for value in args.lambdas)} "
        f"iterations={args.iterations} max_lines={args.max_lines}",
        flush=True,
    )

    for value in args.lambdas:
        label = lambda_label(value)
        stem = f"lambda{label}_iter{args.iterations}_{args.max_lines}lines"
        model_path = private_dir / f"{stem}_unigram_64000.model"
        vocab_path = private_dir / f"{stem}_unigram_64000.vocab"
        report_path = public_prefix.parent / f"{public_prefix.name}_{stem}.md"

        command = [
            sys.executable,
            "scripts/materialize_v2_boundary_weighted_unigram_em.py",
            "--boundary-lambda",
            str(value),
            "--iterations",
            str(args.iterations),
            "--max-lines",
            str(args.max_lines),
            "--progress",
            str(args.progress),
            "--out-model",
            str(model_path),
            "--out-vocab",
            str(vocab_path),
            "--report-out",
            str(report_path),
        ]
        run_command(command, dry_run=args.dry_run)
        model_args.extend([f"em_l{label}_{args.max_lines}", str(model_path)])

    if not args.skip_ci:
        ci_report = public_prefix.parent / (
            f"{public_prefix.name}_{args.max_lines}lines_ci.md"
        )
        command = [
            sys.executable,
            "scripts/report_v2_sp_model_ci.py",
            "--dataset",
            args.dataset,
            "--numeric-sp-passthrough",
            "--samples",
            str(args.ci_samples),
        ]
        for index in range(0, len(model_args), 2):
            command.extend(["--model", f"{model_args[index]}={model_args[index + 1]}"])
        command.extend(["--report-out", str(ci_report)])
        run_command(command, dry_run=args.dry_run)

    print("sweep_complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
