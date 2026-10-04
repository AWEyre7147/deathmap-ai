"""Durable local I/O, preservation and single-writer controls for SQ01 only.

A process-held OS lock survives stale lock files and is released on process exit.
Atomic replace is retried only for transient local locks; a failed checkpoint
never permits the next request. Historical files are hashed, never regenerated.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

from deathmap_ai.sq01_plan import VERSION
from deathmap_ai.orcs_paths import resolve_historical


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(resolve_historical(path).read_text(encoding='utf-8'))


def sha(path):
    """Hash bytes incrementally without interpreting metadata or workbook cells."""
    h = hashlib.sha256()
    with resolve_historical(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic_bytes(path, body):
    """Persist and fsync bytes before bounded atomic replacement; preserve failure."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('wb') as handle:
        handle.write(body)
        handle.flush()
        os.fsync(handle.fileno())
    for attempt in range(5):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt+1))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')


def write(path, value):
    atomic_bytes(path, encoded(value))


def folders(root):
    """Resolve only the three authorized output folders; reject redirected paths."""
    root = Path(root).resolve()
    paths = {'shared': root/'outputs'/VERSION,
             'omicsdi': root/'outputs/omicsdi'/VERSION, 'orcs': root/'outputs/orcs'/VERSION}
    for path in paths.values():
        if path.resolve() != path:
            raise ValueError('Output path redirected by link/junction')
    return paths


@contextmanager
def writer_lock(root):
    """Acquire a nonblocking OS lock for all SQ01 writers; no PID-based guessing."""
    folder = folders(root)['shared']
    folder.mkdir(parents=True, exist_ok=True)
    with (folder/'.writer.lock').open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise RuntimeError('Another SQ01 writer holds the ledger lock') from error
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == 'nt':
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def preservation(root, baseline=None):
    """Validate only approved historical paths; never open evaluation materials."""
    baseline = baseline or (Path(root)/'logs/sq01-preservation.json' if (Path(root)/'logs/sq01-preservation.json').is_file() else Path(root)/'docs/sq01-preservation.json')
    before = read(baseline)['before']
    if not before or any(not p.startswith(('outputs/', 'data/output-example/')) or 'icraft' in p.casefold() or '..' in Path(p).parts for p in before):
        raise ValueError('Invalid preservation baseline targets')
    changed = [p for p,h in before.items() if not resolve_historical(Path(root)/p).is_file() or sha(Path(root)/p) != h]
    # Handoff 11 explicitly replaces the owner's blank review workbook. Its
    # historical bytes must still exist, and only the recorded replacement is
    # permitted. Other historical files and subsequent edits remain detectable.
    target = 'data/output-example/DeathMap-AI-v1-reference-output.xlsx'
    receipt_path = Path(root)/'logs/orcs-workbook-transition.json'
    if not receipt_path.is_file():
        receipt_path = Path(root)/'docs/orcs-workbook-transition.json'
    if target in changed and receipt_path.is_file():
        receipt = read(receipt_path)
        backup = Path(root)/receipt.get('backup_path', '')
        safe = backup.resolve().is_relative_to((Path(root)/'outputs/orcs/filter-runs').resolve())
        if (safe and receipt.get('authority') == '11 ORCS Filter Run and Excel Handoff.md'
                and receipt.get('original_sha256') == before[target]
                and resolve_historical(backup).is_file() and sha(backup) == before[target]
                and sha(Path(root)/target) == receipt.get('replacement_sha256')):
            changed.remove(target)
    if changed:
        raise ValueError('Historical preservation mismatch: '+repr(changed))
    return {'checked_files': len(before), 'changed_files': [], 'baseline_sha256': sha(baseline)}


def freeze(folder, plan_digest):
    """Bind all completed resource bytes to the accepted plan; never re-freeze."""
    target = folder/'freeze_manifest.json'
    if target.exists():
        verify_freeze(folder, plan_digest)
        return
    hashes = {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
    if any(p.endswith('.tmp') for p in hashes):
        raise ValueError('Uncommitted output prevents freezing')
    write(target, {'frozen_at': now(), 'plan_digest': plan_digest, 'files': hashes})


def verify_freeze(folder, plan_digest):
    """Detect missing, altered or added files in a completed resource package."""
    manifest = read(folder/'freeze_manifest.json')
    current = {p.relative_to(folder).as_posix(): sha(p) for p in sorted(folder.rglob('*')) if p.is_file() and p.name != 'freeze_manifest.json'}
    if manifest['plan_digest'] != plan_digest or current != manifest['files']:
        raise ValueError('Frozen resource integrity mismatch: '+str(folder))
