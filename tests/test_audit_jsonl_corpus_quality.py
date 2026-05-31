from __future__ import annotations

import json
from pathlib import Path

from scripts.audit_jsonl_corpus_quality import (
    audit_jsonl_corpus,
    format_quality_report,
    language_hint,
    normalize_for_duplicate,
)


def test_language_hint_detects_basic_turkish_and_english() -> None:
    assert language_hint("Bu bir Türkçe metin ve daha çok örnek içerir.") == "tr_like"
    assert language_hint("This is an English text and it is useful.") == "en_like"


def test_normalize_for_duplicate_collapses_whitespace() -> None:
    assert normalize_for_duplicate("Merhaba   dünya\nbugün") == "Merhaba dünya bugün"


def test_audit_jsonl_corpus_counts_structure_and_quality(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.jsonl"
    rows = [
        {"text": "Bu bir Türkçe metin ve oldukça temiz bir satırdır.", "source": "tr"},
        {"text": "Bu bir Türkçe metin ve oldukça temiz bir satırdır.", "source": "tr"},
        {"text": "This is an English text and it is clean.", "source": "en"},
        {"text": "kısa", "source": "short"},
        {"text": "Visit https://example.com for <b>HTML</b>.", "source": "web"},
        {"not_text": "missing"},
    ]
    corpus.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
        + "\n"
        + "{invalid json}\n",
        encoding="utf-8",
    )

    stats = audit_jsonl_corpus(corpus, long_threshold=20)

    assert stats.scanned_lines == 7
    assert stats.valid_json == 6
    assert stats.invalid_json == 1
    assert stats.missing_text == 1
    assert stats.usable_texts == 5
    assert stats.duplicate_exact == 1
    assert stats.duplicate_normalized == 1
    assert stats.very_short_texts == 1
    assert stats.url_texts == 1
    assert stats.html_texts == 1
    assert stats.long_for_sentencepiece == 4
    assert stats.source_counts["tr"] == 2
    assert stats.language_counts["tr_like"] >= 1

    report = format_quality_report(
        stats,
        max_lines=None,
        text_field="text",
        long_threshold=20,
    )
    assert "JSONL Corpus Quality Audit" in report
    assert "exact_duplicates_in_scan" in report
