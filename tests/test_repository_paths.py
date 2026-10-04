"""Check relocation boundaries and corruption detection with tiny saved files."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from deathmap_ai.repository_paths import resolve_relocation, RECEIPT


class RepositoryPathTests(unittest.TestCase):
    def fixture(self, root):
        archive = root / 'archive'
        archive.mkdir()
        target = archive / 'original.json'
        target.write_bytes(b'original')
        receipt = root / RECEIPT
        receipt.parent.mkdir()
        record = {'archive_root': str(archive), 'files': {'outputs/old.json': {
            'preserved_path': str(target),
            'sha256': hashlib.sha256(b'original').hexdigest()}}}
        receipt.write_text(json.dumps(record), encoding='utf-8')
        return target, receipt, record

    def test_original_bytes_resolve_and_corruption_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target, _, _ = self.fixture(root)
            old = root / 'outputs/old.json'
            self.assertEqual(resolve_relocation(old, root), target)
            target.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                resolve_relocation(old, root)

    def test_outside_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            _, receipt, record = self.fixture(root)
            outside = root / 'outside.json'
            outside.write_bytes(b'original')
            record['files']['outputs/old.json']['preserved_path'] = str(outside)
            receipt.write_text(json.dumps(record), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                resolve_relocation(root / 'outputs/old.json', root)

    def test_existing_unlisted_and_missing_archive_paths_stay_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target, _, _ = self.fixture(root)
            existing = root / 'active.json'
            existing.write_bytes(b'active')
            self.assertEqual(resolve_relocation(existing, root), existing)
            missing = root / 'unlisted.json'
            self.assertEqual(resolve_relocation(missing, root), missing)
            target.unlink()
            old = root / 'outputs/old.json'
            self.assertEqual(resolve_relocation(old, root), old)

    def test_only_registered_dependency_paths_resolve(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            _, receipt, record = self.fixture(root)
            old = root / 'outputs/experiment/node_modules'
            saved = root / 'archive/node_modules'
            saved.mkdir()
            child = saved / 'package.json'
            child.write_bytes(b'dependency')
            record['links'] = [{'old_path': str(old), 'target': str(saved), 'traversed': False}]
            receipt.write_text(json.dumps(record), encoding='utf-8')
            self.assertEqual(resolve_relocation(old / 'package.json', root), child)
            unregistered = root / 'outputs/other/node_modules/package.json'
            self.assertEqual(resolve_relocation(unregistered, root), unregistered)
            record['links'][0]['target'] = str(root / 'outside')
            receipt.write_text(json.dumps(record), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                resolve_relocation(old / 'package.json', root)
