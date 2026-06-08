from scripts.compare_tokenizers import BoundaryScore
from scripts.evaluate_v2_finite_protected_sp64_intrinsic import ModelCaseResult
from scripts.report_v2_train_only_marker_ci import bootstrap_rows


def _result(model_name: str, correct: int, predicted: int, gold: int) -> ModelCaseResult:
    precision = correct / predicted if predicted else 0.0
    recall = correct / gold if gold else 0.0
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return ModelCaseResult(
        model_name=model_name,
        category="toy",
        text="a b",
        expected=["a", "b"],
        logical_tokens=["a", "b"],
        model_token_count=2,
        status="ok",
        reason="",
        boundary=BoundaryScore(precision, recall, f1, correct, predicted, gold),
    )


def test_bootstrap_rows_reports_point_estimate():
    rows = bootstrap_rows(
        {"toy": [_result("toy", 1, 1, 1), _result("toy", 0, 1, 1)]},
        samples=20,
        seed=1,
    )

    assert len(rows) == 1
    assert rows[0].model_name == "toy"
    assert 0.0 <= rows[0].boundary_f1.point <= 1.0
