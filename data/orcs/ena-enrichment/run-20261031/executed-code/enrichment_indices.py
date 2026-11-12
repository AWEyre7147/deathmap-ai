"""Readable, persistent resource indices anchored to native record identities."""
import json
from pathlib import Path
import re

DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / 'data/identifiers/supplemental-index-registry.json'


def native_key(*parts):
    """Encode native identifiers losslessly; display indices never replace them."""
    if not parts or any(not isinstance(p, str) or not p for p in parts):
        raise ValueError('Nonempty native identity strings required')
    return json.dumps(parts, ensure_ascii=False, separators=(',', ':'))


def assign_indices(prefix, keys, registry=None):
    """Return PREFIX-0001 indices; append new identities without renumbering.

    With registry=None this is a deterministic in-memory projection. Maintained
    collection commands supply a persistent registry shared across cohorts.
    Native keys, rather than cohort Publication Index values, define identity.
    """
    if not re.fullmatch(r'[A-Z]{2,6}', prefix):
        raise ValueError('Invalid index prefix')
    keys = set(keys)
    if any(not isinstance(k, str) or not k for k in keys):
        raise ValueError('Invalid native identity key')
    if registry is None:
        return {key: f'{prefix}-{i:04d}' for i, key in enumerate(sorted(keys), 1)}
    registry = Path(registry)
    registry.parent.mkdir(parents=True, exist_ok=True)
    lock = registry.with_suffix(registry.suffix + '.lock')
    # Fail rather than race another collector or overwrite its allocations.
    handle = lock.open('x')
    try:
        data = json.loads(registry.read_text(encoding='utf-8')) if registry.exists() else {
            'schema_version': 'enrichment-indices/1', 'namespaces': {}}
        if data.get('schema_version') != 'enrichment-indices/1':
            raise ValueError('Unsupported index registry schema')
        for namespace, mapping in data['namespaces'].items():
            values = list(mapping.values())
            if len(values) != len(set(values)) or any(
                    not re.fullmatch(re.escape(namespace) + r'-[0-9]{4,}', v) or int(v.rsplit('-', 1)[1]) < 1
                    for v in values):
                raise ValueError('Invalid or duplicate registry indices')
        mapping = data['namespaces'].setdefault(prefix, {})
        next_number = max((int(v.rsplit('-', 1)[1]) for v in mapping.values()), default=0) + 1
        changed = False
        for key in sorted(keys - mapping.keys()):
            mapping[key] = f'{prefix}-{next_number:04d}'
            next_number += 1
            changed = True
        if changed or not registry.exists():
            temporary = registry.with_suffix(registry.suffix + '.tmp')
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            temporary.replace(registry)
        return {key: mapping[key] for key in keys}
    finally:
        handle.close()
        lock.unlink()
