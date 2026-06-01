from scripts.compare_real_tokenizers import RealBaselineSpec
from scripts.report_v1_8_canary_diagnostics import (
    CanaryCase,
    count_canary_words,
    evaluate,
    protected_candidates,
    summarize,
)


def test_count_canary_words_handles_non_latin_scripts():
    assert count_canary_words("مرحبا بالعالم.") == 2
    assert count_canary_words("Москва — большой город.") == 3
    assert count_canary_words("Αθήνα είναι όμορφη πόλη.") == 4


def test_custom_canary_roundtrip_and_protected_span():
    cases = [
        CanaryCase(
            row=1,
            category="technical",
            text="README.md'yi https://example.com/a?x=1 adresinden aç.",
        )
    ]

    assert protected_candidates(cases[0].text)

    results = evaluate(cases, [RealBaselineSpec("custom_tr_morph_lossless", "custom")])
    summary = summarize(results["custom_tr_morph_lossless"])

    assert summary.status == "ok"
    assert summary.roundtrip_failures == 0
    assert summary.protected_broken == 0
