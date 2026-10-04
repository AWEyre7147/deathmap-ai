"""Resolve original provenance paths through the owner-approved relocation map.

Archived manifests keep their original paths and hashes. Missing evidence paths
resolve to recorded, hash-identical copies inside the approved archive. Recorded
dependency junctions are relocated without traversing or copying their libraries;
their callers retain responsibility for comparing historical dependency hashes.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = 'logs/repository-relocations-20261004.json'


@lru_cache(maxsize=8)
def _registry(path, modified_ns, size):
    """Reuse a registry during bulk verification; file changes invalidate its key.

    Only parsed locations are cached. Every resolved evidence file is still read
    and hashed, so cached registration cannot conceal changed scientific bytes.
    """
    return json.loads(Path(path).read_text(encoding='utf-8'))


def resolve_relocation(path, root=None):
    """Return a hash-verified archived copy for a recorded missing repository path.

    Unrelated paths and fixture roots remain untouched. Corrupt or missing archived
    evidence is never replaced by guessed metadata or a newly generated artifact.
    """
    path = Path(path)
    if path.is_file():
        return path
    root = Path(root or ROOT).absolute()
    try:
        relative = path.absolute().relative_to(root).as_posix()
    except ValueError:
        return path
    receipt = root / RECEIPT
    if not receipt.is_file():
        return path
    stat = receipt.stat()
    record = _registry(str(receipt), stat.st_mtime_ns, stat.st_size)
    entry = record.get('files', {}).get(relative)
    if not entry:
        # Old workbook experiments had junctions to the bundled node libraries.
        # Their historical baselines include dependency files. Resolve only a
        # registered node_modules junction; never infer arbitrary folder moves.
        for link in record.get('links', []):
            old_link = Path(link['old_path'])
            if old_link.name != 'node_modules' or link.get('traversed') is not False:
                continue
            try:
                child = path.absolute().relative_to(old_link.absolute())
            except ValueError:
                continue
            if '..' in child.parts:
                raise ValueError('Dependency path escapes recorded junction')
            target = Path(link['target']) / child
            if not target.absolute().is_relative_to(Path(record['archive_root']).absolute()):
                raise ValueError('Relocation target escapes approved archive')
            return target if target.is_file() else path
        return path
    target = Path(entry['preserved_path'])
    if not target.resolve().is_relative_to(Path(record['archive_root']).resolve()):
        raise ValueError('Relocation target escapes approved archive')
    if not target.is_file():
        return path
    h = hashlib.sha256()
    with target.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    if h.hexdigest() != entry['sha256']:
        raise ValueError(f'Archived evidence hash mismatch: {relative}')
    return target
