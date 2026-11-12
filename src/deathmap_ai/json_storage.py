"""Read plain/gzip JSON and losslessly compress completed enrichment outputs."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def resolve_json_path(path):
    """Accept an existing path, or its compressed replacement after promotion."""
    path = Path(path)
    compressed = Path(str(path) + '.gz')
    return compressed if not path.exists() and path.suffix == '.json' and compressed.exists() else path


def load_json(path):
    """Read either storage format; preserve all JSON values and native types."""
    path = resolve_json_path(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', encoding='utf-8-sig') as stream:
        return json.load(stream)


def compress_json(path, *, remove_original=False):
    """Verify decompressed bytes before publishing or deleting a plain JSON.

    Existing compressed destinations are refused. Exact-byte hashes distinguish
    the unchanged logical source from its new compressed storage representation.
    """
    path = Path(path)
    if path.suffix != '.json':
        raise ValueError('Expected a plain .json source')
    output = Path(str(path) + '.gz')
    if output.exists():
        raise FileExistsError(output)
    with path.open('rb') as source:
        original_hash = hashlib.file_digest(source, 'sha256').hexdigest()
    # Validate JSON before a malformed input could replace a usable artifact.
    load_json(path)
    created = False
    try:
        with output.open('xb') as target:
            created = True
            with gzip.GzipFile(filename='', mode='wb', fileobj=target, mtime=0) as archive:
                with path.open('rb') as source:
                    shutil.copyfileobj(source, archive)
        with gzip.open(output, 'rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != original_hash:
                raise ValueError('Gzip round-trip hash mismatch')
        with output.open('rb') as source:
            compressed_hash = hashlib.file_digest(source, 'sha256').hexdigest()
        receipt = {'path': str(output), 'sha256': compressed_hash,
                   'uncompressed_sha256': original_hash,
                   'original_bytes': path.stat().st_size, 'compressed_bytes': output.stat().st_size}
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    if remove_original:
        path.unlink()
    return receipt


def compress_stage_output(folder, receipt):
    """Compress the finished canonical database, leaving resumable evidence intact."""
    folder = Path(folder)
    candidates = [p for p in (folder / 'database.json', folder / 'geo-enrichment.json') if p.exists()]
    if not candidates:
        return receipt  # Registry stages and already compressed synthesis need no change.
    if len(candidates) != 1:
        raise ValueError('Ambiguous canonical database for compression')
    info = compress_json(candidates[0])
    # Update only the final export manifests, never source responses/checkpoints.
    for path in folder.glob('*.manifest.json'):
        manifest = load_json(path)
        if 'source_database_sha256' in manifest:
            manifest['uncompressed_source_database_sha256'] = manifest['source_database_sha256']
            manifest['source_database_sha256'] = info['sha256']
            manifest['source_database'] = str(Path(info['path']).resolve())
        if 'database_sha256' in manifest:
            manifest['uncompressed_database_sha256'] = manifest['database_sha256']
            manifest['database_sha256'] = info['sha256']
            manifest['database'] = str(Path(info['path']).resolve())
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')
    receipt.update(canonical_database=str(Path(info['path']).resolve()), compression=info)
    for field in ('source_database', 'database'):
        hashkey = field + '_sha256'
        if hashkey in receipt:
            receipt['uncompressed_' + hashkey] = receipt[hashkey]
            receipt[hashkey] = info['sha256']
            receipt[field] = str(Path(info['path']).resolve())
    candidates[0].unlink()
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--remove-original', action='store_true')
    args = parser.parse_args()
    for path in args.paths:
        print(json.dumps(compress_json(path, remove_original=args.remove_original)))


if __name__ == '__main__':
    main()
