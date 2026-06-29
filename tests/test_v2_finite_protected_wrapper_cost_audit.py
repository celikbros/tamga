from collections import Counter

from scripts.audit_v2_finite_protected_wrapper_cost import (
    LineAudit,
    SplitAudit,
    audit_line,
)
from tr_tokenizer import TurkishTokenizer


class FakeProcessor:
    def EncodeAsIds(self, text: str) -> list[int]:
        return list(range(len([part for part in text.split(" ") if part])))

    def EncodeAsPieces(self, text: str) -> list[str]:
        return ["\u2581" + part for part in text.split(" ") if part]


def test_audit_line_counts_protected_components():
    audit = audit_line(
        split="toy",
        line_no=1,
        text="README.md'yi aç.",
        processor=FakeProcessor(),
        selected_pieces=["README", ".md"],
        tokenizer=TurkishTokenizer(preserve_whitespace=True),
    )

    assert audit.protected_pieces == 1
    assert audit.protected_surface_bytes == len("README.md".encode("utf-8"))
    assert audit.protected_piece_tokens == 2
    assert audit.protected_byte_tokens == 0
    assert audit.apostrophe_tokens == 1
    assert audit.hard_suffix_tokens == 1
    assert audit.finite_tokens >= audit.protected_model_tokens


def test_split_audit_rates():
    stats = SplitAudit(
        split="toy",
        lines=1,
        raw_bytes=100,
        baseline_sp_tokens=10,
        finite_tokens=12,
        protected_piece_tokens=3,
        protected_byte_tokens=2,
        protected_surface_bytes=20,
        route_counts=Counter({"file": 1}),
    )

    assert stats.baseline_tokens_per_byte == 0.1
    assert stats.finite_tokens_per_byte == 0.12
    assert stats.delta_tokens_per_byte == 0.02
    assert stats.relative_delta == 0.2
    assert stats.protected_bytes_share == 0.2
    assert stats.protected_tokens_per_protected_byte == 0.25
