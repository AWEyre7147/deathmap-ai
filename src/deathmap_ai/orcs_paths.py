"""Resolve authorized ORCS index and archive relocations without rewriting history.

Active readers use data/orcs. Frozen manifests retain their original paths; only
known index files and registered archive copies resolve only with original bytes.
"""
from pathlib import Path
import hashlib
from deathmap_ai.repository_paths import resolve_relocation

INDEX = 'data/orcs/screen-index.json'
CSV = 'data/orcs/screen-metadata.csv'
LEGACY = 'outputs/orcs/cache/legacy/20260904T213941Z/'
SUMMARY = 'data/orcs/cache-summary.json'
RELOCATIONS = {
    LEGACY + 'orcs-screens.raw.json': (INDEX, '3ace1de98615e857b5829c2fe50e8c106eb4df20030f86362d55f36a298cd37e'),
    LEGACY + 'orcs-screen-metadata.csv': (CSV, 'ed651772fbe589fc99c67d999ad1bd2e18d10f6e8ceceb54b5c56004dacb8908'),
}


def resolve_historical(path):
    """Resolve a missing legacy index to its hash-verified new path; never guess."""
    path = Path(path)
    if path.is_file():
        return path
    for old, (new, expected) in RELOCATIONS.items():
        old_parts = Path(old).parts
        if path.parts[-len(old_parts):] != old_parts:
            continue
        root = path
        for _ in old_parts:
            root = root.parent
        target = root / new
        if not target.is_file():
            return path
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError('Relocated historical ORCS index hash mismatch')
        return target
    return resolve_relocation(path)
