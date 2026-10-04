"""Export an ORCS vocabulary snapshot as Obsidian-compatible Markdown notes.

The exporter reads the raw metadata snapshot produced by the ORCS pilot. It does
not contact ORCS or modify the raw response. Each vocabulary category becomes a
separate note so large term sets remain navigable in Obsidian.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _slug(value: str) -> str:
    """Create a stable, readable filename from an ORCS category label."""

    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def _escape_table_cell(value: Any) -> str:
    """Prevent ORCS punctuation from breaking a Markdown table row."""

    return (
        str(value)
        .replace("|", "\\|")
        # Chemical names can contain double brackets that Obsidian otherwise
        # interprets as internal links.
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("\n", "<br>")
    )


def export_vocabularies(snapshot_path: Path, output_dir: Path) -> list[Path]:
    """Write an index and one Markdown note per controlled-vocabulary category."""

    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    categories = payload.get("categories")
    terms_by_category = payload.get("terms_by_category")
    if not isinstance(categories, dict) or not isinstance(terms_by_category, dict):
        raise ValueError("The vocabulary snapshot lacks categories or term collections.")

    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []
    index_rows: list[tuple[str, str, int]] = []

    for category_id, category_name in sorted(
        categories.items(), key=lambda item: str(item[1]).casefold()
    ):
        terms = terms_by_category.get(str(category_id))
        if not isinstance(terms, dict):
            raise ValueError(f"Vocabulary category {category_id} is not a term mapping.")

        filename = f"{_slug(str(category_name))}.md"
        note_path = output_dir / filename
        lines = [
            "---",
            f'orcs_category_id: "{category_id}"',
            "tags:",
            "  - deathmap-ai",
            "  - orcs",
            "  - controlled-vocabulary",
            "---",
            "",
            f"# ORCS vocabulary: {category_name}",
            "",
            f"Terms: {len(terms)}",
            "",
            "| ORCS term ID | Term |",
            "|---:|---|",
        ]
        for term_id, term in sorted(terms.items(), key=lambda item: str(item[1]).casefold()):
            lines.append(f"| {_escape_table_cell(term_id)} | {_escape_table_cell(term)} |")
        lines.append("")
        note_path.write_text("\n".join(lines), encoding="utf-8")
        generated.append(note_path)
        index_rows.append((str(category_name), note_path.stem, len(terms)))

    index_path = output_dir / "index.md"
    relative_snapshot = snapshot_path.as_posix()
    index_lines = [
        "---",
        "aliases:",
        "  - ORCS controlled vocabularies",
        "tags:",
        "  - deathmap-ai",
        "  - orcs",
        "  - index",
        "---",
        "",
        "# ORCS controlled vocabularies",
        "",
        "These notes reproduce the controlled terms returned by the ORCS metadata",
        "service. They document source terminology; they do not define DeathMap-AI",
        "eligibility rules.",
        "",
        f"Source snapshot: `{relative_snapshot}`",
        "",
        "| Category | Terms |",
        "|---|---:|",
    ]
    for category_name, note_stem, count in index_rows:
        index_lines.append(f"| [[{note_stem}|{category_name}]] | {count} |")
    index_lines.extend(
        [
            "",
            "## Updating these notes",
            "",
            "Run the metadata probe to create a new raw vocabulary snapshot, then run",
            "`scripts/export_orcs_vocab_markdown.py` with that snapshot. Review the",
            "Markdown changes before accepting an ORCS terminology update.",
            "",
        ]
    )
    index_path.write_text("\n".join(index_lines), encoding="utf-8")
    generated.append(index_path)
    return generated


def main() -> None:
    """Parse explicit paths and report generated note names."""

    parser = argparse.ArgumentParser(description="Export ORCS vocabularies to Markdown.")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    generated = export_vocabularies(args.snapshot, args.output_dir)
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
