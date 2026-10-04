"""Perform the owner's one-time, hash-verified repository organization.

Only explicitly listed paths may move. Historical bytes and pre-edit copies of
relocated active files remain in the external archive. Directory links are never
traversed, so temporary dependency junctions cannot move shared runtime contents.
The durable relocation map permits historical manifests to keep original paths.
"""
import hashlib
import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path('C:/Users/aweyr/Documents/Archives/deathmap-ai-v01-archive')
RECEIPT = ROOT / 'logs/repository-relocations-20261004.json'
SEARCH = 'cancer-cell-crispr-knockout-v01'
RUN = '20261003T173643920687Z'

def digest(path):
    """Hash bytes without interpreting scientific records or local credentials."""
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def inventory(path):
    """Enumerate regular files, recording but never entering directory junctions."""
    if path.is_file():
        return [path], []
    files, links = [], []
    for base, dirs, names in os.walk(path, followlinks=False):
        for name in list(dirs):
            child = Path(base) / name
            if child.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                links.append(child)
                dirs.remove(name)
        files.extend(Path(base) / name for name in names)
    return files, links

def main():
    """Validate paths, preserve originals, move each group, and verify every hash."""
    if RECEIPT.exists():
        raise FileExistsError('Migration receipt exists; inspect it instead of rerunning')
    assert ARCHIVE.is_dir() and ARCHIVE.resolve() == ARCHIVE
    active = [
        (f'searches/orcs/{SEARCH}.json', f'searches/orcs/{SEARCH}/profile.json'),
        (f'searches/orcs/{SEARCH}-run-plan.md', f'searches/orcs/{SEARCH}/run-plan.md'),
        (f'outputs/orcs/filter-runs/orcs-{SEARCH}', f'outputs/orcs/{SEARCH}'),
        ('docs/references/orcs-vocabulary-annotations', 'data/cellosaurus/orcs-annotations'),
        ('docs/orcs/vocabularies/orcs-local', 'docs/vocabularies/orcs/local'),
        ('docs/orcs/vocabularies/orcs-metadata-service', 'docs/vocabularies/orcs/metadata-service'),
        ('outputs/orcs/page-capability', 'data/orcs/website-capability'),
        ('docs/orcs-filter-run.md', 'docs/orcs/filter-run.md'),
        ('docs/owner-review-decisions.md', 'logs/owner-review-decisions.md'),
        ('docs/orcs-workbook-transition.json', 'logs/orcs-workbook-transition.json'),
        ('docs/sq01-preservation.json', 'logs/sq01-preservation.json'),
        ('docs/v03-preservation.json', 'logs/v03-preservation.json'),
    ]
    historical = []
    for name in ['01a0876c-output-structure', '01a0b0b8-reference']:
        historical.append((f'outputs/{name}', f'output-structure-experiments/outputs/{name}'))
    for name in ['immune-crispr-coculture-v02', 'immune-crispr-coculture-v03', 'omicsdi']:
        historical.append((f'outputs/{name}', f'historical-runs/outputs/{name}'))
    for name in ['cache', 'immune-crispr-coculture-v01', 'immune-crispr-coculture-v02', 'immune-crispr-coculture-v03']:
        historical.append((f'outputs/orcs/{name}', f'historical-runs/outputs/orcs/{name}'))
    for name in ['shared-resource-search.md', 'search-profile-curation.md', 'v03-query-planning.md',
                 'sq01-blind-discovery.md', 'proposed-discovery-enrichment-v03.md']:
        historical.append((f'docs/{name}', f'superseded-documentation/docs/{name}'))
    historical += [('docs/references/orcs-cell-annotation-pilot', 'superseded-documentation/docs/references/orcs-cell-annotation-pilot'),
        ('data/brainstorming', 'historical-runs/data/brainstorming'),
        ('data/output-example', 'historical-runs/data/output-example'),
        ('.tmp', 'temporary-artifacts/.tmp'), ('tmp', 'temporary-artifacts/tmp'),
        ('results', 'temporary-artifacts/results'), ('data/interim', 'temporary-artifacts/data/interim')]
    for name in ['first-run.md', 'offline-repair.md', 'search-information.md']:
        historical.append((f'docs/omicsdi/{name}', f'superseded-documentation/docs/omicsdi/{name}'))
    groups = [(old, ROOT / new, 'active') for old, new in active] + [(old, ARCHIVE / new, 'archived') for old, new in historical]
    groups = [(old, target, role) for old, target, role in groups if (ROOT / old).exists()]
    entries, link_entries = {}, []
    for old, target, role in groups:
        source = ROOT / old
        assert source.resolve().is_relative_to(ROOT.resolve())
        boundary = ROOT if role == 'active' else ARCHIVE
        assert target.resolve().is_relative_to(boundary.resolve()) and not target.exists()
        files, links = inventory(source)
        for file in files:
            suffix = file.relative_to(source) if source.is_dir() else Path()
            new = target / suffix if source.is_dir() else target
            relative = file.relative_to(ROOT).as_posix()
            preserved = ARCHIVE / 'historical-runs/relocated-originals' / relative if role == 'active' else new
            entries[relative] = {'new_path': str(new), 'preserved_path': str(preserved),
                'sha256': digest(file), 'role': role, 'bytes': file.stat().st_size}
        link_entries += [{'old_path': str(p), 'target': str(target / p.relative_to(source)), 'traversed': False} for p in links]
    # Recover the genuinely blank template and complete cache summary before
    # moving their containers. No Excel cells or scientific fields are changed.
    run = ROOT / f'outputs/orcs/filter-runs/orcs-{SEARCH}/{RUN}'
    template = ROOT / 'data/templates/DeathMap-AI-v1-reference-output.xlsx'
    template.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((run / 'run_manifest.json').read_text(encoding='utf-8'))
    expected = manifest['input_hashes']['data/output-example/DeathMap-AI-v1-reference-output.xlsx']
    assert digest(run / 'workbook-original.xlsx') == expected and not template.exists()
    shutil.copy2(run / 'workbook-original.xlsx', template)
    assert digest(template) == expected
    summary = ROOT / 'data/orcs/cache-summary.json'
    assert not summary.exists()
    shutil.copy2(ROOT / 'outputs/orcs/cache/legacy/20260904T213941Z/summary.json', summary)
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    record = {'authority': 'Owner-confirmed organization and external archive, 2026-10-04',
              'archive_root': str(ARCHIVE), 'created_at': datetime.now(timezone.utc).isoformat(),
              'status': 'prepared', 'files': entries, 'links': link_entries, 'completed_groups': []}
    def save():
        RECEIPT.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    save()
    for old, target, role in groups:
        source = ROOT / old
        assert source.resolve().is_relative_to(ROOT.resolve())
        assert target.resolve().is_relative_to((ROOT if role == 'active' else ARCHIVE).resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        if role == 'active':
            for relative, entry in entries.items():
                if relative == old or relative.startswith(old + '/'):
                    preserved = Path(entry['preserved_path'])
                    preserved.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ROOT / relative, preserved)
                    assert digest(preserved) == entry['sha256']
        os.rename(source, target)
        for relative, entry in entries.items():
            if relative == old or relative.startswith(old + '/'):
                assert digest(Path(entry['new_path'])) == entry['sha256']
        record['completed_groups'].append(old)
        save()
    record.update(status='complete', completed_at=datetime.now(timezone.utc).isoformat(), files_verified=len(entries))
    save()
    print(f'Completed {len(groups)} moves; verified {len(entries)} files; {len(link_entries)} dependency links not traversed.')

if __name__ == '__main__':
    main()
