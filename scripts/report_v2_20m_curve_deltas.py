from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Point:
    step: int
    approx_bytes: float
    tokens_seen: int
    valid_bpb: float
    valid_bits_per_token: float | None


@dataclass(frozen=True)
class Series:
    name: str
    points: list[Point]


def load_series(name: str, path: Path) -> Series:
    points: list[Point] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        item = json.loads(raw)
        points.append(
            Point(
                step=int(item["step"]),
                approx_bytes=float(item["approx_bytes_seen"]),
                tokens_seen=int(item["tokens_seen"]),
                valid_bpb=float(item["valid_bpb"]),
                valid_bits_per_token=(
                    float(item["valid_bits_per_token"])
                    if "valid_bits_per_token" in item
                    else None
                ),
            )
        )
    return Series(name=name, points=points)


def nearest(series: Series, target_bytes: float) -> Point:
    return min(series.points, key=lambda point: abs(point.approx_bytes - target_bytes))


def default_series() -> list[Series]:
    root = Path("artifacts/private")
    return [
        load_series(
            "sp64_floor",
            root
            / "v2_0_tiny_lm_curve_sp64_floor_20mbytes"
            / "finite_protected_sp64_numeric_sp_floor"
            / "metrics.jsonl",
        ),
        load_series(
            "self_distilled_16000",
            root
            / "v2_0_tiny_lm_curve_self_distilled_16000_20mbytes"
            / "finite_protected_self_distilled_16000"
            / "metrics.jsonl",
        ),
        load_series(
            "teacher_distilled_16000",
            root
            / "v2_0_tiny_lm_curve_teacher_distilled_16000_20mbytes"
            / "finite_protected_teacher_distilled_16000"
            / "metrics.jsonl",
        ),
    ]


def format_report(series: list[Series], targets: list[float]) -> str:
    baseline = series[0]
    lines = [
        "# v2.0 20M Learning Curve Delta Report",
        "",
        "This report reads the logged validation checkpoints from the 20M runs and",
        "compares candidates at nearest matched raw-byte checkpoints.",
        "",
        "## Delta Versus SP64 Floor",
        "",
        "| Target bytes | SP64 bytes | SP64 valid BPB | Self bytes | Self valid BPB | Self delta | Teacher bytes | Teacher valid BPB | Teacher delta |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    teacher_deltas: list[float] = []
    for target in targets:
        base = nearest(baseline, target)
        self_point = nearest(series[1], target)
        teacher = nearest(series[2], target)
        self_delta = self_point.valid_bpb - base.valid_bpb
        teacher_delta = teacher.valid_bpb - base.valid_bpb
        teacher_deltas.append(teacher_delta)
        lines.append(
            f"| {target:,.0f} | {base.approx_bytes:,.0f} | {base.valid_bpb:.6f} | "
            f"{self_point.approx_bytes:,.0f} | {self_point.valid_bpb:.6f} | "
            f"{self_delta:+.6f} | {teacher.approx_bytes:,.0f} | "
            f"{teacher.valid_bpb:.6f} | {teacher_delta:+.6f} |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
        ]
    )
    if teacher_deltas and all(delta > 0 for delta in teacher_deltas[1:]):
        lines.append(
            "Teacher-distilled is worse than SP64 at every matched checkpoint after the first tiny initial point."
        )
    elif teacher_deltas and teacher_deltas[-1] > 0:
        lines.append(
            "Teacher-distilled ends worse than SP64. Any early advantage is not durable within this 20M window."
        )
    else:
        lines.append(
            "Teacher-distilled does not end worse than SP64 in this window; inspect the table before closing."
        )
    lines.extend(
        [
            "",
            "The 2M endpoint from the earlier ladder should not be spliced into",
            "this curve because that run used older accounting. The within-run",
            "20M curve is the cleaner decision artifact.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Report 20M curve deltas.")
    parser.add_argument(
        "--targets",
        default="2000000,4000000,6000000,8000000,10000000,12000000,14000000,16000000,18000000,20000000",
    )
    parser.add_argument(
        "--report-out",
        default="artifacts/v2_0_20m_learning_curve_delta_report.md",
    )
    args = parser.parse_args()

    targets = [float(item) for item in args.targets.split(",") if item.strip()]
    report = format_report(default_series(), targets)
    out = Path(args.report_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"wrote_report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
