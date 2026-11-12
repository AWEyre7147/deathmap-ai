"""Compression preserves source bytes and remains usable by pipeline readers."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from deathmap_ai.json_storage import compress_json, compress_stage_output, load_json


class JsonStorageTests(unittest.TestCase):
    def test_round_trip_exact_bytes_types_and_old_path_resolution(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'database.json'
            native = b'{"text":"caf\\u00e9", "count":0, "flag":true, "missing":null}\r\n'
            path.write_bytes(native)
            receipt = compress_json(path, remove_original=True)
            self.assertFalse(path.exists())
            self.assertEqual(gzip.decompress(Path(receipt['path']).read_bytes()), native)
            self.assertEqual(load_json(path), {'text': 'caf\u00e9', 'count': 0, 'flag': True, 'missing': None})
            self.assertEqual(receipt['uncompressed_sha256'], hashlib.sha256(native).hexdigest())

    def test_invalid_input_and_existing_destination_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'database.json'
            path.write_text('invalid', encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):
                compress_json(path, remove_original=True)
            self.assertTrue(path.exists())
            self.assertFalse(Path(str(path) + '.gz').exists())
            path.write_text('{}', encoding='utf-8')
            compress_json(path)
            with self.assertRaises(FileExistsError):
                compress_json(path, remove_original=True)
            self.assertTrue(path.exists())

    def test_failed_verification_keeps_plain_original(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'database.json'
            path.write_text('{}', encoding='utf-8')
            with patch('deathmap_ai.json_storage.gzip.open', side_effect=OSError('Verification failed')):
                with self.assertRaises(OSError):
                    compress_json(path, remove_original=True)
            self.assertTrue(path.exists())
            self.assertFalse(Path(str(path) + '.gz').exists())

    def test_stage_updates_storage_hash_and_retains_logical_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            database = folder / 'database.json'
            database.write_text('{}', encoding='utf-8')
            logical = hashlib.sha256(database.read_bytes()).hexdigest()
            manifest = folder / 'Example.manifest.json'
            manifest.write_text(json.dumps({'source_database_sha256': logical}), encoding='utf-8')
            receipt = compress_stage_output(folder, {})
            self.assertFalse(database.exists())
            saved = load_json(manifest)
            self.assertEqual(saved['uncompressed_source_database_sha256'], logical)
            self.assertEqual(saved['source_database_sha256'], receipt['compression']['sha256'])
            self.assertTrue(Path(saved['source_database']).exists())

    def test_controller_compression_option_finishes_with_gzip_canonical(self):
        from deathmap_ai.enrichment_commands import run_stage
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = root / 'publications.json'
            index.write_text('[]', encoding='utf-8')
            output = root / 'run'
            args = argparse.Namespace(root=root, stage='ena', publication_index=index,
                output_dir=output, registry=None, geo=index, pubmed=index, template=None,
                cache_root=[], metadata_only_project=[], compress_json=True)
            def retrieve(*args, **kwargs):
                output.mkdir()
                (output / 'database.json').write_text('{"status":"complete","rows":{}}', encoding='utf-8')
                return {'status': 'complete', 'rows': {}, 'summary': {}}
            with patch('deathmap_ai.ena_collection.run', side_effect=retrieve), patch(
                    'deathmap_ai.enrichment_commands.export_registered', return_value={}):
                receipt = run_stage(args)
            self.assertTrue(Path(receipt['canonical_database']).exists())
            self.assertFalse((output / 'database.json').exists())
            self.assertEqual(load_json(receipt['canonical_database'])['status'], 'complete')


if __name__ == '__main__':
    unittest.main()
