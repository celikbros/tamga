from scripts.audit_v2_protected_route_cost_classes import (
    classify_apostrophe_surface,
    classify_file_like,
    classify_numeric_like,
)


def test_classifies_numeric_like_subclasses():
    assert classify_numeric_like("1") == "plain_integer_1_digit"
    assert classify_numeric_like("2018") == "plain_integer_3_4_digit"
    assert classify_numeric_like("0.05") == "decimal_or_grouped_number"
    assert classify_numeric_like("2018-2019") == "year_range"
    assert classify_numeric_like("19/02/2018") == "calendar_date"
    assert classify_numeric_like("CO2") == "short_alnum_code"
    assert classify_numeric_like("toplam125") == "alnum_mixed_text"


def test_classifies_file_like_subclasses():
    assert classify_file_like("README.md") == "known_file_extension"
    assert classify_file_like("0.0px") == "css_px_value"
    assert classify_file_like("p0.05") == "statistical_p_value"
    assert classify_file_like("T.C") == "dotted_abbreviation_or_version"
    assert classify_file_like("değerlendirildi.Bulgular") == "glued_sentence_boundary"


def test_classifies_apostrophe_surface_subclasses():
    assert classify_apostrophe_surface("Türkiye'de") == "turkish_suffix_parseable"
    assert (
        classify_apostrophe_surface("\u00dcniversitesi'nde")
        == "turkish_suffix_parseable"
    )
    assert classify_apostrophe_surface("Mahkemesi'ne") == "turkish_suffix_parseable"
    assert classify_apostrophe_surface("M\u00fctarekesi'nden") == "turkish_suffix_parseable"
    assert classify_apostrophe_surface("Kur'an") == "lexical_transliteration_apostrophe"
    assert classify_apostrophe_surface("Cronbach's") == "english_contraction_or_possessive"
