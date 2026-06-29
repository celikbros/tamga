from scripts.audit_v2_non_turkish_latin_route_quality import classify_surface


def test_classifies_legacy_turkish_encoding_artifacts():
    assert classify_surface("kaynaþtýrma") == "legacy_turkish_encoding_artifact"
    assert classify_surface("öðretmen") == "legacy_turkish_encoding_artifact"


def test_classifies_other_non_turkish_latin():
    assert classify_surface("Straße") == "other_non_turkish_latin"
    assert classify_surface("niño") == "other_non_turkish_latin"


def test_classifies_turkish_loan_diacritics():
    assert classify_surface("hâlâ") == "turkish_loan_diacritic"
    assert classify_surface("ma'lûmat") == "turkish_loan_diacritic"
