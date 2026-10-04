"""Tests for reproducible ORCS vocabulary Markdown notes."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_orcs_vocab_markdown import export_vocabularies


class VocabularyMarkdownTests(unittest.TestCase):
    def test_export_creates_linked_obsidian_notes(self) -> None:
        payload = {
            "categories": {"7": "Library Methodology"},
            "terms_by_category": {
                "7": {"29": "knockout", "31": "activation", "32": "compound [[test]]"}
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot = root / "vocabs.json"
            snapshot.write_text(json.dumps(payload), encoding="utf-8")
            output = root / "docs" / "orcs" / "vocabularies"

            export_vocabularies(snapshot, output)

            index = (output / "index.md").read_text(encoding="utf-8")
            note = (output / "library-methodology.md").read_text(encoding="utf-8")
            self.assertIn("[[library-methodology|Library Methodology]]", index)
            self.assertIn("| 29 | knockout |", note)
            self.assertIn(r"compound \[\[test\]\]", note)
            self.assertIn('orcs_category_id: "7"', note)


if __name__ == "__main__":
    unittest.main()
