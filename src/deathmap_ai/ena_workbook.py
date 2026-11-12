"""Export registered ENA rows using the existing template-preserving XML writer.

This CLI is metadata-only and portable with the project's existing dependencies.
It reuses the registration/mapping checks shared with GEO; no ENA retrieval,
screen classification or experimental-file access occurs during export.
"""
from .json_storage import load_json, resolve_json_path
import argparse
import json
from pathlib import Path
from .enrichment_export import export_registered as _registered_export
from .ena_indexed_projection import project
from .enrichment_indices import DEFAULT_REGISTRY


def export_workbook(database_path, template, output, *, publication_registry=None, index_registry=None):
    """Write and verify selected ENA rows without a full spreadsheet-engine model.

    Parameters
    ----------
    database_path, template, output : Path or str
        Completed canonical ENA metadata, registered template and fresh output.
    publication_registry : Path, optional
        Existing PUB crosswalk for publications without an embedded index.
    index_registry : Path, optional
        Append-only entity registry; defaults to the shared resource registry.

    Returns
    -------
    dict
        Template/output hashes and per-sheet counts, also saved as a receipt.

    Raises
    ------
    ValueError
        Retrieval is unfinished or registered fields/template do not match.
    FileExistsError
        An existing workbook would be overwritten.
    """
    database_path, template, output = map(Path, (database_path, template, output))
    if output.exists():
        raise FileExistsError(output)
    database_path = resolve_json_path(database_path)
    database = load_json(database_path)
    if database['status'] not in ('complete', 'complete_with_issues', 'complete_with_omissions'):
        raise ValueError('ENA retrieval is unfinished')
    # Completed historical runs can be reprojected from native metadata without
    # repeating discovery or trusting their obsolete workbook column layout.
    rows = project(database, publication_registry, index_registry or DEFAULT_REGISTRY)
    result = _registered_export(template, output, rows)
    (output.parent / 'workbook-receipt.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def main():
    """Export one completed canonical ENA run into a fresh registered workbook."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    parser.add_argument('template', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--publication-registry', type=Path)
    parser.add_argument('--index-registry', type=Path)
    args = parser.parse_args()
    print(json.dumps(export_workbook(args.database, args.template, args.output,
        publication_registry=args.publication_registry, index_registry=args.index_registry)))


if __name__ == '__main__':
    main()
