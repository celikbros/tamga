from scripts.report_confidence_intervals import MetricInterval
from scripts.report_v2_sp_model_ci import format_report, parse_model
from pathlib import Path


def test_parse_model_requires_label_path():
    spec = parse_model("sp64=path/to/model.model")

    assert spec.label == "sp64"
    assert spec.path.as_posix() == "path/to/model.model"


def test_format_report_includes_interval_columns():
    report = format_report(
        dataset=Path("eval.tsv"),
        rows=[
            type(
                "Row",
                (),
                {
                    "model_name": "toy",
                    "examples": 2,
                    "boundary_f1": MetricInterval(0.5, 0.25, 0.75),
                    "avg_model_tokens_word": MetricInterval(2.0, 1.0, 3.0),
                    "exact_match_rate": MetricInterval(0.0, 0.0, 0.0),
                },
            )()
        ],
        samples=10,
        numeric_sp_passthrough=True,
    )

    assert "Boundary F1 95% CI" in report
    assert "`toy`" in report
