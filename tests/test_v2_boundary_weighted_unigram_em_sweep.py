import pytest

from scripts.run_v2_boundary_weighted_unigram_em_sweep import (
    lambda_label,
    main,
    parse_lambdas,
)


def test_parse_lambdas_accepts_comma_separated_numbers():
    assert parse_lambdas("0,1,2.5, 4") == [0.0, 1.0, 2.5, 4.0]


def test_parse_lambdas_rejects_empty_list():
    with pytest.raises(Exception):
        parse_lambdas(" , ")


def test_lambda_label_is_path_friendly():
    assert lambda_label(0.0) == "0"
    assert lambda_label(2.5) == "2p5"
    assert lambda_label(-1.25) == "m1p25"


def test_dry_run_prints_materialization_and_ci_commands(capsys):
    result = main(
        [
            "--lambdas",
            "0,1",
            "--max-lines",
            "10",
            "--iterations",
            "1",
            "--ci-samples",
            "5",
            "--dry-run",
        ]
    )

    output = capsys.readouterr().out
    assert result == 0
    assert "materialize_v2_boundary_weighted_unigram_em.py" in output
    assert "lambda0_iter1_10lines_unigram_64000.model" in output
    assert "lambda1_iter1_10lines_unigram_64000.model" in output
    assert "report_v2_sp_model_ci.py" in output
    assert "sweep_complete" in output
