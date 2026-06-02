from pathlib import Path
import json

from scripts.materialize_v2_protected_routes import (
    format_report,
    materialize_protected_routes,
)


def test_materialize_protected_routes_writes_routes_and_inventory(tmp_path: Path):
    input_path = tmp_path / "train.txt"
    jsonl_out = tmp_path / "routes.jsonl"
    inventory_out = tmp_path / "inventory.tsv"
    input_path.write_text(
        "README.md'yi ac.\n"
        "transformers>=4.40 uygundur.\n"
        "https://example.com adresine bak.\n",
        encoding="utf-8",
    )

    stats = materialize_protected_routes(
        input_path=input_path,
        jsonl_out=jsonl_out,
        inventory_out=inventory_out,
        max_lines=None,
        progress=0,
    )

    assert stats.lines == 3
    assert stats.protected_pieces >= 3
    assert stats.suffix_tails_after_protected >= 1
    assert stats.unique_protected_surfaces >= 3

    rows = [json.loads(line) for line in jsonl_out.read_text(encoding="utf-8").splitlines()]
    first_routes = rows[0]["routes"]
    assert any(route["surface"] == "README.md" for route in first_routes)
    assert any(route["surface"] == "yi" and route["route"].startswith("suffix_tail_after_") for route in first_routes)

    inventory = inventory_out.read_text(encoding="utf-8")
    assert "category\troute\tsurface\tcount\tbytes" in inventory
    assert "README.md" in inventory
    assert "transformers>=4.40" in inventory

    report = format_report(
        input_path=input_path,
        jsonl_out=jsonl_out,
        inventory_out=inventory_out,
        stats=stats,
        max_lines=None,
    )
    assert "v2.0 Protected Route Materialization" in report
    assert "Protected pieces" in report
